import prompts from "./chat-prompts.json";

const GEMINI_MODEL = "gemini-2.5-flash-lite";
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...CORS },
  });
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
      return jsonResponse(
        {
          error:
            "GEMINI_API_KEY is not set on the Worker. Run: wrangler secret put GEMINI_API_KEY",
        },
        503
      );
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
    if (!prompts[context]) {
      return jsonResponse({ error: "Invalid context. Use 'alex' or 'sarah'." }, 400);
    }

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
          systemInstruction: { parts: [{ text: prompts[context] }] },
          contents,
          generationConfig: { temperature: 0.7, maxOutputTokens: 1024 },
        }),
      });

      const body = await resp.json();
      if (!resp.ok) {
        const detail = body?.error?.message || resp.statusText;
        return jsonResponse({ error: `Gemini API error: ${detail}` }, 502);
      }

      const parts = body?.candidates?.[0]?.content?.parts || [];
      const reply = parts.map((p) => p.text || "").join("").trim();
      if (!reply) return jsonResponse({ error: "Gemini returned an empty response." }, 502);

      return jsonResponse({ reply, context });
    } catch (err) {
      return jsonResponse({ error: `Could not reach Gemini API: ${err.message}` }, 502);
    }
  },
};
