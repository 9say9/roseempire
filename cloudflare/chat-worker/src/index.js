import rules from "./chat-rules.json";
import { buildSystemPrompt } from "./build-prompt.js";

const GEMINI_MODEL = "gemini-2.5-flash-lite";
const DEFAULT_CATALOG_URL = "https://www.roseempire.co.uk/catalog-data.json";
const CATALOG_TTL_MS = 5 * 60 * 1000;

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

    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${apiKey}`;

    try {
      const resp = await fetch(geminiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          systemInstruction: { parts: [{ text: systemInstruction }] },
          contents,
          generationConfig: { temperature: 0.7, maxOutputTokens: 1024 },
        }),
      });

      const body = await resp.json();
      if (!resp.ok) {
        const detail = body?.error?.message || resp.statusText;
        return jsonResponse({ error: AI service error:  }, 502);
      }

      const parts = body?.candidates?.[0]?.content?.parts || [];
      const reply = parts.map((p) => p.text || "").join("").trim();
      if (!reply) return jsonResponse({ error: "Empty AI response." }, 502);

      return jsonResponse({ reply, context, catalogUpdatedAt: catalog?.updatedAt || null });
    } catch (err) {
      return jsonResponse({ error: Could not reach AI service:  }, 502);
    }
  },
};