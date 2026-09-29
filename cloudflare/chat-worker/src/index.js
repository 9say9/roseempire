import rules from "./chat-rules.json";
import { buildSystemPrompt } from "./build-prompt.js";
import { SARAH_TOOL_DECLARATIONS, executeSarahTool } from "./sarah-tools.js";

const PRIMARY_MODEL = "gemini-2.5-flash";
const FALLBACK_MODEL = "gemini-2.5-flash-lite";
const DEFAULT_CATALOG_URL = "https://www.roseempire.co.uk/catalog-data.json";
const CATALOG_TTL_MS = 5 * 60 * 1000;
const MAX_TOOL_ROUNDS = 4;

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

let catalogCache = { data: null, fetchedAt: 0 };

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...CORS },
  });
}

async function fetchCatalog(env) {
  const now = Date.now();
  if (catalogCache.data && now - catalogCache.fetchedAt < CATALOG_TTL_MS) {
    return catalogCache.data;
  }
  const url = env.CATALOG_URL || DEFAULT_CATALOG_URL;
  try {
    const resp = await fetch(url, { cf: { cacheTtl: 300, cacheEverything: true } });
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    const data = await resp.json();
    catalogCache = { data, fetchedAt: now };
    return data;
  } catch (err) {
    console.error("Catalog fetch failed:", err.message);
    return catalogCache.data;
  }
}

function generationConfigForModel(model) {
  const base = { temperature: 0.35, maxOutputTokens: 600 };
  if (model === PRIMARY_MODEL) {
    return { ...base, thinkingConfig: { thinkingBudget: 128 } };
  }
  return base;
}

async function callGemini(apiKey, model, systemInstruction, contents, useTools) {
  const geminiUrl =
    "https://generativelanguage.googleapis.com/v1beta/models/" +
    model +
    ":generateContent?key=" +
    apiKey;

  const body = {
    systemInstruction: { parts: [{ text: systemInstruction }] },
    contents,
    generationConfig: generationConfigForModel(model),
  };

  if (useTools) {
    body.tools = [{ functionDeclarations: SARAH_TOOL_DECLARATIONS }];
  }

  const resp = await fetch(geminiUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const parsed = await resp.json();
  return { ok: resp.ok, status: resp.status, body: parsed };
}

function extractModelParts(candidate) {
  const parts = candidate?.content?.parts || [];
  let text = "";
  const functionCalls = [];
  for (const p of parts) {
    if (p.text) text += p.text;
    if (p.functionCall) functionCalls.push(p.functionCall);
  }
  return { text: text.trim(), functionCalls };
}

async function runWithModel(apiKey, model, systemInstruction, contents, catalog, toolsEnabled) {
  const toolsUsed = [];
  let conversation = [...contents];
  let lastText = "";

  for (let round = 0; round < MAX_TOOL_ROUNDS; round++) {
    const { ok, body } = await callGemini(
      apiKey,
      model,
      systemInstruction,
      conversation,
      toolsEnabled && round < MAX_TOOL_ROUNDS - 1
    );

    if (!ok) {
      return { error: body?.error?.message || "AI service error", toolsUsed };
    }

    const candidate = body?.candidates?.[0];
    const { text, functionCalls } = extractModelParts(candidate);
    if (text) lastText = text;

    if (!functionCalls.length) {
      return { reply: lastText, toolsUsed };
    }

    const modelParts = candidate.content?.parts || [];
    conversation.push({ role: "model", parts: modelParts });

    const responseParts = [];
    for (const fc of functionCalls) {
      const name = fc.name;
      const args = fc.args || {};
      toolsUsed.push(name);
      const result = executeSarahTool(name, args, catalog);
      responseParts.push({
        functionResponse: {
          name,
          response: result,
        },
      });
    }
    conversation.push({ role: "user", parts: responseParts });
  }

  return { reply: lastText, toolsUsed };
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS });
    }
    if (request.method !== "POST") {
      return jsonResponse({ error: "Method not allowed." }, 405);
    }

    const apiKey = env.GEMINI_API_KEY;
    if (!apiKey) {
      return jsonResponse({ error: "Chat service is not configured." }, 503);
    }

    let data;
    try {
      data = await request.json();
    } catch {
      return jsonResponse({ error: "Invalid JSON body." }, 400);
    }

    const message = (data.message || "").trim();
    const context = (data.context || "sarah").toLowerCase();
    const history = Array.isArray(data.history) ? data.history : [];
    const toolsEnabled = context === "sarah" && data.tools !== false;

    if (!message) return jsonResponse({ error: "Message is required." }, 400);
    if (!rules[context]) {
      return jsonResponse({ error: "Invalid context." }, 400);
    }

    const catalog = await fetchCatalog(env);
    const systemInstruction = buildSystemPrompt(context, rules, catalog);

    const contents = [];
    for (const turn of history.slice(-10)) {
      const content = (turn.content || "").trim();
      if (!content) continue;
      contents.push({
        role: turn.role === "user" ? "user" : "model",
        parts: [{ text: content }],
      });
    }
    contents.push({ role: "user", parts: [{ text: message }] });

    const primary = env.GEMINI_MODEL || PRIMARY_MODEL;
    let modelUsed = primary;
    let fallback = false;
    let toolsUsed = [];
    let reply = "";

    try {
      let result = await runWithModel(apiKey, primary, systemInstruction, contents, catalog, toolsEnabled);
      if (result.error || !result.reply) {
        fallback = true;
        modelUsed = FALLBACK_MODEL;
        result = await runWithModel(apiKey, FALLBACK_MODEL, systemInstruction, contents, catalog, toolsEnabled);
      }
      if (result.error) {
        return jsonResponse({ error: "AI service error: " + result.error }, 502);
      }
      reply = result.reply || "";
      toolsUsed = result.toolsUsed || [];
      if (!reply) {
        fallback = true;
        modelUsed = FALLBACK_MODEL;
        const retry = await runWithModel(apiKey, FALLBACK_MODEL, systemInstruction, contents, catalog, toolsEnabled);
        reply = retry.reply || "";
        toolsUsed = retry.toolsUsed || toolsUsed;
      }
    } catch (err) {
      return jsonResponse(
        { error: "Could not reach AI service: " + (err.message || String(err)) },
        502
      );
    }

    if (!reply) return jsonResponse({ error: "Empty AI response." }, 502);

    return jsonResponse({
      reply,
      context,
      model: modelUsed,
      toolsUsed,
      fallback,
      catalogUpdatedAt: catalog?.updatedAt || null,
    });
  },
};
