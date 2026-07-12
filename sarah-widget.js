(function () {
  "use strict";

  /**
   * Sarah — instant website-aware assistant (Acquire-ready)
   * - Indexes the host site on load (current page instantly, more pages in background)
   * - Answers in milliseconds from site index + learned slots (no model download)
   * - Self-improves in fixed slots, total platform payload capped at 100KB
   */

  const KNOWLEDGE_SLOTS = 24;
  const MAX_BYTES = 100 * 1024;
  const MAX_CRAWL_PAGES = 12;
  const MAX_CHUNK_CHARS = 280;
  const META_DOM_ID = "sarah-meta-storage";
  const META_VERSION = 2;

  const script = document.currentScript;
  const apiBase = (
    script?.dataset?.apiBase ||
    (script?.src
      ? new URL(".", script.src).href.replace(/\/$/, "")
      : location.origin)
  ).replace(/\/$/, "");
  const adminToken =
    script?.dataset?.adminToken ||
    new URLSearchParams(location.search).get("sarah_admin") ||
    "";

  const config = {
    clientId: script?.dataset?.clientId || "default",
    title: script?.dataset?.title || "Sarah",
    accent: script?.dataset?.accent || "#8b5cf6",
    siteName:
      script?.dataset?.siteName ||
      document.title?.split(/[|\-–]/)[0]?.trim() ||
      "this website",
    whiteLabel: script?.dataset?.whiteLabel === "true",
    position: script?.dataset?.position === "left" ? "left" : "right",
    premiumFx: script?.dataset?.fx === "true" || script?.dataset?.premiumFx === "true",
  };

  function hexToRgb(hex) {
    const h = String(hex || "#8b5cf6").replace("#", "");
    const full = h.length === 3 ? h.split("").map((c) => c + c).join("") : h;
    const n = parseInt(full, 16) || 0x8b5cf6;
    return { r: (n >> 16) & 255, g: (n >> 8) & 255, b: n & 255 };
  }

  const accentRgb = hexToRgb(config.accent);
  const accentCss = `${accentRgb.r},${accentRgb.g},${accentRgb.b}`;

  const PAGE_PROFILES = [
    {
      id: "about",
      test: (p) => /\/about(\/|$)/i.test(p),
      nudge: "Want to know our story, mission, and brand values?",
      chips: ["Our mission", "Who we are", "Why choose us"],
      topic: "brand",
    },
    {
      id: "products",
      test: (p) => /\/products?(\/|$)/i.test(p),
      nudge: "Ask about products, wholesale, or bulk pricing.",
      chips: ["Wholesale pricing", "Product range", "Bulk orders"],
      topic: "sales",
    },
    {
      id: "pricing",
      test: (p) => /\/pricing(\/|$)/i.test(p),
      nudge: "Need help picking a plan or package?",
      chips: ["Compare plans", "Enterprise", "Free trial"],
      topic: "pricing",
    },
    {
      id: "contact",
      test: (p) => /\/contact(\/|$)/i.test(p),
      nudge: "Questions before you reach out? I can help.",
      chips: ["Support hours", "Sales contact", "Book a demo"],
      topic: "contact",
    },
    {
      id: "default",
      test: () => true,
      nudge: `Hi! I'm ${config.title}. Ask me anything about ${config.siteName}.`,
      chips: ["What do you offer?", "Pricing", "Get started"],
      topic: "general",
    },
  ];

  const MetaStorage = {
    siteKey: `sarah:platform:${config.clientId}:site`,
    knowledgeKey: `sarah:platform:${config.clientId}:knowledge`,
    sessionKey: `sarah:platform:${config.clientId}:session`,

    read(key, fallback) {
      try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : fallback;
      } catch {
        return fallback;
      }
    },

    write(key, value) {
      const blob = buildMirrorBlob(key, value);
      const payload = JSON.stringify(blob);
      if (byteSize(payload) > MAX_BYTES) {
        pruneMirrorBlob(blob);
      }
      const finalPayload = JSON.stringify(blob);
      if (byteSize(finalPayload) > MAX_BYTES) {
        throw new Error("Platform storage exceeded 100KB cap.");
      }
      localStorage.setItem(MetaStorage.siteKey, JSON.stringify(blob.site));
      localStorage.setItem(MetaStorage.knowledgeKey, JSON.stringify(blob.knowledge));
      localStorage.setItem(MetaStorage.sessionKey, JSON.stringify(blob.session));
      mirrorDom(blob);
    },

    loadAll() {
      hydrateFromDom();
      return {
        site: MetaStorage.read(MetaStorage.siteKey, emptySiteIndex()),
        knowledge: MetaStorage.read(MetaStorage.knowledgeKey, emptyKnowledge()),
        session: MetaStorage.read(MetaStorage.sessionKey, []),
      };
    },
  };

  function buildMirrorBlob(changedKey, changedValue) {
    const current = MetaStorage.loadAll();
    if (changedKey === MetaStorage.siteKey) current.site = changedValue;
    if (changedKey === MetaStorage.knowledgeKey) current.knowledge = changedValue;
    if (changedKey === MetaStorage.sessionKey) current.session = changedValue;
    return {
      v: META_VERSION,
      clientId: config.clientId,
      updatedAt: Date.now(),
      site: current.site,
      knowledge: current.knowledge,
      session: current.session,
    };
  }

  function pruneMirrorBlob(blob) {
    blob.session = blob.session.slice(-30);
    blob.site.chunks = (blob.site.chunks || []).slice(0, 48);
    blob.knowledge.slots = blob.knowledge.slots.map((slot, i) =>
      slot
        ? {
            ...slot,
            adjustment: slot.adjustment.slice(0, Math.floor(slot.adjustment.length * 0.6)),
          }
        : null
    );
  }

  function mirrorDom(blob) {
    let node = document.getElementById(META_DOM_ID);
    if (!node) {
      node = document.createElement("script");
      node.id = META_DOM_ID;
      node.type = "application/json";
      node.setAttribute("data-sarah-container", "true");
      (document.head || document.documentElement).appendChild(node);
    }
    node.textContent = JSON.stringify(blob);
  }

  function hydrateFromDom() {
    const node = document.getElementById(META_DOM_ID);
    if (!node?.textContent) return;
    try {
      const blob = JSON.parse(node.textContent);
      if (blob.site) localStorage.setItem(MetaStorage.siteKey, JSON.stringify(blob.site));
      if (blob.knowledge) localStorage.setItem(MetaStorage.knowledgeKey, JSON.stringify(blob.knowledge));
      if (blob.session) localStorage.setItem(MetaStorage.sessionKey, JSON.stringify(blob.session));
    } catch {
      /* ignore */
    }
  }

  function byteSize(str) {
    return new TextEncoder().encode(str).length;
  }

  function emptySiteIndex() {
    return {
      v: META_VERSION,
      origin: location.origin,
      updatedAt: 0,
      chunks: [],
    };
  }

  function emptyKnowledge() {
    return {
      v: META_VERSION,
      slots: Array.from({ length: KNOWLEDGE_SLOTS }, () => null),
      cycle: 0,
    };
  }

  const store = MetaStorage.loadAll();
  const state = {
    open: false,
    sending: false,
    ownerMode: Boolean(adminToken),
    siteConfig: null,
    pathname: location.pathname,
    pageProfile: resolveProfile(location.pathname),
    nudgeDismissedPath: null,
    messages: Array.isArray(store.session) ? store.session : [],
    siteIndex: store.site?.chunks?.length ? store.site : emptySiteIndex(),
    knowledge: store.knowledge?.slots?.length === KNOWLEDGE_SLOTS ? store.knowledge : emptyKnowledge(),
    crawlDone: false,
  };

  /* ─── Site Control: owner updates theme, prices, images, sections, bot name ─── */
  const SiteControl = {
    _loadGen: 0,

    async load() {
      const gen = ++this._loadGen;
      try {
        const res = await fetch(`${apiBase}/api/site-config`, {
          headers: { "X-Client-Id": config.clientId },
        });
        if (gen !== this._loadGen) return;
        if (res.ok) {
          const data = await res.json();
          const localAt = state.siteConfig?.updatedAt || 0;
          if (!state.siteConfig || data.updatedAt >= localAt) {
            state.siteConfig = data;
            this.apply();
          }
        }
      } catch {
        /* offline — widget still works from index */
      }
    },

    async save(mutations) {
      const res = await fetch(`${apiBase}/api/site-config`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "X-Client-Id": config.clientId,
          "X-Admin-Token": adminToken,
        },
        body: JSON.stringify({ ...(state.siteConfig || {}), ...mutations }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Could not save site changes");
      state.siteConfig = data.config;
      this._loadGen++;
      this.apply();
    },

    apply() {
      const sc = state.siteConfig;
      if (!sc) return;

      config.title = sc.bot?.title || config.title;
      config.accent = sc.bot?.accent || sc.theme?.accent || config.accent;

      root.style.setProperty("--sw-accent", config.accent);
      document.documentElement.style.setProperty("--sarah-accent", config.accent);

      if (sc.theme?.background) {
        document.body.style.background = sc.theme.background;
      }
      if (sc.theme?.text) {
        document.body.style.color = sc.theme.text;
      }
      if (sc.theme?.mode === "light") {
        document.documentElement.setAttribute("data-sarah-theme", "light");
      } else if (sc.theme?.mode === "dark") {
        document.documentElement.setAttribute("data-sarah-theme", "dark");
      }

      Object.entries(sc.prices || {}).forEach(([key, value]) => {
        document.querySelectorAll(`[data-sarah-price="${key}"]`).forEach((el) => {
          el.textContent = value;
        });
      });

      Object.entries(sc.images || {}).forEach(([key, url]) => {
        document.querySelectorAll(`[data-sarah-image="${key}"]`).forEach((el) => {
          if (el.tagName === "IMG") el.src = url;
          else el.style.backgroundImage = `url(${url})`;
        });
      });

      document.querySelectorAll("[data-sarah-section]").forEach((el) => {
        const key = el.getAttribute("data-sarah-section");
        const meta = sc.sections?.[key];
        el.style.display = meta?.hidden ? "none" : "";
      });

      (sc.textPatches || []).forEach((patch) => {
        try {
          document.querySelectorAll(patch.selector).forEach((el) => {
            el.textContent = patch.text;
          });
        } catch {
          /* invalid selector */
        }
      });

      const titleEl = root.querySelector(".sarah-header-title");
      if (titleEl) titleEl.textContent = config.title;
      const subEl = root.querySelector("#sarah-status-text");
      if (subEl && sc.bot?.subtitle) subEl.textContent = sc.bot.subtitle;

      (sc.rawKnowledge || []).forEach((entry) => {
        SiteBrain.upsertChunk(
          makeChunk("/", config.siteName, "owner-data", entry.slice(0, MAX_CHUNK_CHARS), 8)
        );
      });
    },

    parseCommand(text) {
      const replies = [];
      const mutations = {};
      const t = text.trim();

      let m;
      if ((m = t.match(/rename (?:the )?bot to (.+)/i))) {
        mutations.bot = { ...(state.siteConfig?.bot || {}), title: m[1].trim() };
        replies.push(`Bot renamed to "${m[1].trim()}".`);
      }
      if ((m = t.match(/(?:set |change )?(?:theme )?colou?r to (#?[a-f0-9]{3,8})/i))) {
        const color = m[1].startsWith("#") ? m[1] : `#${m[1]}`;
        mutations.bot = { ...(state.siteConfig?.bot || {}), accent: color };
        mutations.theme = { ...(state.siteConfig?.theme || {}), accent: color };
        replies.push(`Theme color set to ${color}.`);
      }
      if ((m = t.match(/set theme to (light|dark|auto)/i))) {
        mutations.theme = { ...(state.siteConfig?.theme || {}), mode: m[1].toLowerCase() };
        replies.push(`Theme mode set to ${m[1]}.`);
      }
      if ((m = t.match(/set (?:\w+ )*(starter|business|enterprise|pro|basic)(?: price)? to (.+)/i))) {
        mutations.prices = {
          ...(state.siteConfig?.prices || {}),
          [m[1].toLowerCase()]: m[2].trim(),
        };
        replies.push(`${m[1]} price set to ${m[2].trim()}.`);
      }
      if ((m = t.match(/hide (?:the )?(?:section )?#?([\w-]+)/i)) && !/(?:opening|closing)\s*hours?/i.test(t)) {
        mutations.sections = {
          ...(state.siteConfig?.sections || {}),
          [m[1]]: { hidden: true },
        };
        replies.push(`Section "${m[1]}" hidden on your site.`);
      }
      if (
        /(?:remove|hide|delete|take\s+off).*(?:opening|closing|business)\s*(?:hours?|timing|time)/i.test(t) ||
        /(?:opening|closing).*(?:hours?|timing|time).*(?:remove|hide|delete|take\s+off)/i.test(t)
      ) {
        mutations.sections = {
          ...(state.siteConfig?.sections || {}),
          "opening-hours": { hidden: true },
        };
        replies.push(`Opening hours hidden — contact details in the top bar stay visible.`);
      }
      if (/(?:remove|hide|delete)\s+(?:the\s+)?(?:entire\s+)?top\s*bar/i.test(t)) {
        mutations.sections = {
          ...(state.siteConfig?.sections || {}),
          "top-bar": { hidden: true },
        };
        replies.push(`Entire top bar hidden on your site.`);
      }
      if ((m = t.match(/show (?:the )?(?:section )?#?([\w-]+)/i))) {
        mutations.sections = {
          ...(state.siteConfig?.sections || {}),
          [m[1]]: { hidden: false },
        };
        replies.push(`Section "${m[1]}" is visible again.`);
      }
      if (
        /(?:show|restore|bring\s+back|unhide).*(?:opening|closing)\s*(?:hours?|timing|time)/i.test(t) ||
        /(?:opening|closing)\s*(?:hours?|timing).*(?:show|restore|back)/i.test(t)
      ) {
        mutations.sections = {
          ...(state.siteConfig?.sections || {}),
          "opening-hours": { hidden: false },
        };
        replies.push(`Opening hours are visible again.`);
      }
      if (/(?:show|restore|bring\s+back).*(?:top\s*bar|top\s+panel)/i.test(t)) {
        mutations.sections = {
          ...(state.siteConfig?.sections || {}),
          "top-bar": { hidden: false },
        };
        replies.push(`Top bar is visible again.`);
      }
      if (/(?:restore|undo|revert|reset)\s+(?:all\s+)?(?:site\s+)?(?:changes?|sections?|everything|website)/i.test(t)) {
        mutations.sections = {};
        replies.push(`All hidden sections restored to visible.`);
      }
      if ((m = t.match(/set subtitle to (.+)/i))) {
        mutations.bot = { ...(state.siteConfig?.bot || {}), subtitle: m[1].trim() };
        replies.push(`Subtitle set to "${m[1].trim()}".`);
      }
      if ((m = t.match(/set image ([\w-]+) to (https?:\/\/\S+)/i))) {
        mutations.images = { ...(state.siteConfig?.images || {}), [m[1]]: m[2] };
        replies.push(`Image slot "${m[1]}" updated.`);
      }
      if ((m = t.match(/set headline to (.+)/i))) {
        mutations.textPatches = [
          ...(state.siteConfig?.textPatches || []).filter((p) => p.selector !== "h1"),
          { selector: "h1", text: m[1].trim() },
        ];
        replies.push(`Main headline updated.`);
      }

      const bulkPrices = [...t.matchAll(/(starter|business|enterprise|pro|basic)\s*[:=\-]?\s*(\$[\d,]+|custom)/gi)];
      if (bulkPrices.length) {
        const prices = { ...(state.siteConfig?.prices || {}) };
        for (const hit of bulkPrices) prices[hit[1].toLowerCase()] = hit[2];
        mutations.prices = prices;
        replies.push(`Updated ${bulkPrices.length} price(s) from your data.`);
      }

      if (/^(learn|add knowledge):/i.test(t)) {
        const raw = t.replace(/^(learn|add knowledge):\s*/i, "").trim();
        mutations.rawKnowledge = [...(state.siteConfig?.rawKnowledge || []), raw].slice(-20);
        replies.push(`Saved ${raw.length} characters to your site knowledge.`);
      }

      if (!replies.length && t.length >= 48 && !/[?]/.test(t)) {
        mutations.rawKnowledge = [...(state.siteConfig?.rawKnowledge || []), t].slice(-20);
        replies.push(`Saved your pasted data (${t.length} chars) — visitors can ask about it now.`);
      }

      if (!replies.length) {
        return {
          ok: false,
          reply:
            'Owner mode commands:\n• hide opening hours\n• restore all changes\n• show top bar\n• set color to #ff5500\n• set starter price to $249\n• show leads / export leads\n• learn: paste FAQ or product data',
        };
      }
      return { ok: true, mutations, reply: replies.join(" ") };
    },
  };

  /* ─── Site indexer: reads the live website, not a downloaded model ─── */
  const SiteBrain = {
    indexDocument(doc = document, url = location.href, pathname = location.pathname) {
      const chunks = extractChunks(doc, url, pathname);
      for (const chunk of chunks) {
        this.upsertChunk(chunk);
      }

      // SPA sites: index hidden route sections so answers are instant without fetch
      doc.querySelectorAll("main.page, [data-sarah-page]").forEach((section) => {
        const routePath =
          section.dataset.sarahPage ||
          (section.id === "home" ? "/" : `/${section.id}`);
        const wrapper = document.implementation.createHTMLDocument("sarah");
        wrapper.body.appendChild(section.cloneNode(true));
        for (const chunk of extractChunks(wrapper, url, routePath)) {
          this.upsertChunk(chunk);
        }
      });

      state.siteIndex.updatedAt = Date.now();
      state.siteIndex.origin = location.origin;
      persistSite();
    },

    upsertChunk(chunk) {
      const chunks = state.siteIndex.chunks;
      const idx = chunks.findIndex(
        (c) => c.path === chunk.path && c.heading === chunk.heading
      );
      if (idx >= 0) chunks[idx] = chunk;
      else chunks.push(chunk);
      if (chunks.length > 64) {
        chunks.sort((a, b) => (b.weight || 0) - (a.weight || 0));
        state.siteIndex.chunks = chunks.slice(0, 64);
      }
    },

    async crawlBackground() {
      if (state.crawlDone) return;
      const links = collectInternalLinks().slice(0, MAX_CRAWL_PAGES);
      const current = location.pathname;

      for (const path of links) {
        if (path === current) continue;
        try {
          const res = await fetch(path, { credentials: "same-origin" });
          if (!res.ok) continue;
          const html = await res.text();
          const doc = new DOMParser().parseFromString(html, "text/html");
          const chunks = extractChunks(doc, new URL(path, location.origin).href, path);
          for (const chunk of chunks) this.upsertChunk(chunk);
        } catch {
          /* skip unreachable routes */
        }
      }

      state.crawlDone = true;
      state.siteIndex.updatedAt = Date.now();
      persistSite();
      setStatus(`Learned ${state.siteIndex.chunks.length} sections from ${config.siteName}`);
    },
  };

  function collectInternalLinks() {
    const origin = location.origin;
    const paths = new Set();
    document.querySelectorAll("a[href]").forEach((anchor) => {
      try {
        const url = new URL(anchor.getAttribute("href"), location.href);
        if (url.origin !== origin) return;
        if (url.pathname.match(/\.(pdf|zip|png|jpg|jpeg|gif|svg|css|js)$/i)) return;
        paths.add(url.pathname || "/");
      } catch {
        /* ignore */
      }
    });
    return [...paths];
  }

  function extractChunks(doc, url, pathname) {
    const chunks = [];
    const title = doc.title || config.siteName;
    const metaDesc =
      doc.querySelector('meta[name="description"]')?.content ||
      doc.querySelector('meta[property="og:description"]')?.content ||
      "";

    if (metaDesc) {
      chunks.push(makeChunk(pathname, title, "summary", metaDesc, 10));
    }

    const selectors = ["main", "article", "[role=main]", "#content", ".content", "body"];
    let root = doc.body;
    for (const sel of selectors) {
      const el = doc.querySelector(sel);
      if (el?.innerText?.trim().length > 80) {
        root = el;
        break;
      }
    }

    const headings = root.querySelectorAll("h1, h2, h3, p, li");
    headings.forEach((el, i) => {
      const text = el.innerText?.replace(/\s+/g, " ").trim();
      if (!text || text.length < 24) return;
      const tag = el.tagName.toLowerCase();
      const weight = tag === "h1" ? 9 : tag === "h2" ? 7 : tag === "h3" ? 5 : 3;
      chunks.push(
        makeChunk(pathname, title, tag + "-" + i, text.slice(0, MAX_CHUNK_CHARS), weight)
      );
    });

    doc.querySelectorAll('script[type="application/ld+json"]').forEach((node) => {
      try {
        const json = JSON.parse(node.textContent);
        const text = JSON.stringify(json).slice(0, MAX_CHUNK_CHARS);
        chunks.push(makeChunk(pathname, title, "schema", text, 6));
      } catch {
        /* ignore */
      }
    });

    return chunks;
  }

  function makeChunk(path, pageTitle, heading, text, weight) {
    return {
      path,
      pageTitle,
      heading,
      text,
      weight,
      keywords: tokenize(text + " " + pageTitle + " " + path),
    };
  }

  function tokenize(text) {
    const stop = new Set([
      "about", "with", "that", "this", "from", "your", "have", "what", "when",
      "where", "would", "could", "should", "there", "their", "they", "them", "also",
    ]);
    const words = String(text).toLowerCase().match(/[a-z0-9]{3,}/g) || [];
    const out = [];
    for (const w of words) {
      if (stop.has(w)) continue;
      if (!out.includes(w)) out.push(w);
      if (out.length >= 16) break;
    }
    return out;
  }

  function overlap(a, b) {
    const set = new Set(b);
    let n = 0;
    for (const t of a) if (set.has(t)) n++;
    return n;
  }

  /* ─── Instant responder (no network, no model weights) ─── */
  const Brain = {
  answer(query) {
      const q = query.toLowerCase();
      const qTokens = tokenize(query);
      const profile = state.pageProfile;
      const scored = [];

      for (const chunk of state.siteIndex.chunks) {
        let score = overlap(qTokens, chunk.keywords) * 2;
        if (chunk.path === state.pathname) score += 3;
        if (/wholesale|bulk|sales/.test(q) && chunk.path === "/products") score += 5;
        if (/price|pricing|plan/.test(q) && chunk.path === "/pricing") score += 5;
        if (/about|mission|brand/.test(q) && chunk.path === "/about") score += 5;
        if (profile.topic !== "general" && chunk.text.toLowerCase().includes(profile.topic)) score += 2;
        score += chunk.weight || 0;
        if (score > 0) scored.push({ chunk, score });
      }

      for (const slot of state.knowledge.slots) {
        if (!slot) continue;
        let score = overlap(qTokens, slot.keywords) * 3;
        if (slot.path === state.pathname) score += 2;
        if (score > 0) scored.push({ chunk: { text: slot.adjustment, path: slot.path, heading: "learned" }, score: score + 4 });
      }

      scored.sort((a, b) => b.score - a.score);
      return composeReply(query, scored.slice(0, 4), profile);
    },
  };

  function composeReply(query, hits, profile) {
    const q = query.toLowerCase();

    if (/weather|temperature|forecast/.test(q)) {
      return `I don't have live weather data — I'm trained on ${config.siteName}'s website content only. I can help with your products, pricing, policies, or how to get started though. What would you like to know about the site?`;
    }

    if (!hits.length) {
      return `I'm ${config.title}, your assistant for ${config.siteName}. I couldn't find an exact match for that on the site yet — try asking about ${profile.chips.join(", ").toLowerCase()}. Or leave your email here and the team will get back to you personally.`;
    }

    const snippets = [];
    for (const hit of hits) {
      const t = hit.chunk.text?.trim();
      if (!t) continue;
      if (!snippets.some((s) => s.slice(0, 50) === t.slice(0, 50))) snippets.push(t);
    }

    const body = snippets.join(" ");
    let reply = body
      ? `${openingForQuery(query, profile)} ${body}`
      : openingForQuery(query, profile);
    reply = reply.replace(/\s+/g, " ").trim();

    const source = hits[0].chunk.path;
    if (source && source !== state.pathname) {
      reply += ` (More on ${source})`;
    }
    return reply.slice(0, 900);
  }

  function openingForQuery(query, profile) {
    const q = query.toLowerCase();
    if (/^(hi|hello|hey|hii)\b/.test(q)) {
      return `Hello! Great to meet you — I'm here to help with ${config.siteName}.`;
    }
    if (/price|pricing|cost|plan/.test(q)) {
      return `Here's what I found about pricing on the site:`;
    }
    if (/wholesale|bulk|sales/.test(q)) {
      return `Regarding sales and wholesale:`;
    }
    if (/who|about|mission|brand/.test(q)) {
      return `About the brand:`;
    }
    return `Based on ${config.siteName}'s ${profile.id} page:`;
  }

  function learnFromExchange(userText, replyText) {
    const profile = state.pageProfile;
    const keywords = tokenize(userText + " " + replyText + " " + profile.topic);
    const adjustment = `Q: ${userText.slice(0, 100)} → A: ${replyText.slice(0, 220)}`;
    const slots = state.knowledge.slots;

    let best = 0;
    let bestScore = -Infinity;
    slots.forEach((slot, i) => {
      let score = slot ? overlap(keywords, slot.keywords) * 2 : -1;
      if (slot?.path === state.pathname) score += 2;
      if (!slot) score = -0.5;
      if (score > bestScore) {
        bestScore = score;
        best = i;
      }
    });

    slots[best] = {
      id: `slot-${best}`,
      path: state.pathname,
      topic: profile.topic,
      keywords: keywords.slice(0, 12),
      adjustment: adjustment.slice(0, 400),
      updatedAt: Date.now(),
    };
    state.knowledge.cycle = (state.knowledge.cycle || 0) + 1;
    persistAll();
  }

  function persistSite() {
    MetaStorage.write(MetaStorage.siteKey, state.siteIndex);
  }

  function persistAll() {
    MetaStorage.write(MetaStorage.knowledgeKey, state.knowledge);
  }

  function saveSession() {
    state.messages = state.messages.slice(-30);
    MetaStorage.write(MetaStorage.sessionKey, state.messages);
  }

  function resolveProfile(pathname) {
    return PAGE_PROFILES.find((p) => p.test(pathname)) || PAGE_PROFILES.at(-1);
  }

  function applyPageContext(pathname) {
    state.pathname = pathname;
    state.pageProfile = resolveProfile(pathname);
    SiteBrain.indexDocument();
    updateNudge();
    renderChips();
    if (state.open) renderMessages();
  }

  async function streamReply(text, onToken) {
    const words = text.split(/(\s+)/);
    for (const part of words) {
      onToken(part);
      await new Promise((r) => setTimeout(r, part.trim() ? 12 : 4));
    }
  }

  /* ─── Tech bot face SVG (circular AI identity) ─── */
  function botFaceSvg(id, size = 44) {
    const gid = `sarah-grad-${id}`;
    return `<svg class="sarah-bot-svg" width="${size}" height="${size}" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <defs>
        <radialGradient id="${gid}" cx="50%" cy="45%" r="55%">
          <stop offset="0%" stop-color="#ffffff"/>
          <stop offset="55%" stop-color="rgb(${accentCss})"/>
          <stop offset="100%" stop-color="rgb(${accentCss})" stop-opacity="0.2"/>
        </radialGradient>
        <linearGradient id="${gid}-shell" x1="8" y1="8" x2="56" y2="56">
          <stop offset="0%" stop-color="rgba(${accentCss},0.45)"/>
          <stop offset="100%" stop-color="rgba(15,15,25,0.9)"/>
        </linearGradient>
      </defs>
      <circle cx="32" cy="32" r="30" fill="url(#${gid}-shell)" stroke="rgba(255,255,255,0.14)" stroke-width="1"/>
      <circle cx="32" cy="32" r="25" stroke="rgba(${accentCss},0.35)" stroke-width="1" stroke-dasharray="4 6" class="sarah-bot-ring"/>
      <circle cx="32" cy="32" r="19" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
      <rect x="18" y="27" width="12" height="5" rx="2.5" fill="rgb(${accentCss})" class="sarah-bot-eye"/>
      <rect x="34" y="27" width="12" height="5" rx="2.5" fill="rgb(${accentCss})" class="sarah-bot-eye sarah-bot-eye-r"/>
      <path d="M24 42 Q32 47 40 42" stroke="rgba(255,255,255,0.45)" stroke-width="1.8" stroke-linecap="round" fill="none"/>
      <circle cx="32" cy="32" r="6" fill="url(#${gid})" class="sarah-bot-core"/>
      <circle cx="32" cy="9" r="2" fill="rgba(${accentCss},0.8)" class="sarah-bot-node"/>
      <circle cx="55" cy="32" r="1.8" fill="rgba(${accentCss},0.55)" class="sarah-bot-node"/>
      <circle cx="32" cy="55" r="1.8" fill="rgba(${accentCss},0.55)" class="sarah-bot-node"/>
      <circle cx="9" cy="32" r="2" fill="rgba(${accentCss},0.8)" class="sarah-bot-node"/>
    </svg>`;
  }

  const launcherBot = botFaceSvg("launcher", 52);
  const headerBot = botFaceSvg("header", 44);

  /* ─── Premium UI (Luma-inspired glass + motion) ─── */
  let subtitleEl, nudgeEl, chipsEl, messagesEl, input, sendBtn, panel, typingEl, ambientCanvas;

  const posSide = config.position === "left" ? "left:24px" : "right:24px";
  const panelSide = config.position === "left" ? "left:0" : "right:0";

  const styles = `
    #sarah-widget{
      --sw-accent:${config.accent};
      --sw-accent-rgb:${accentCss};
      --sw-bg:rgba(8,8,12,0.92);
      --sw-surface:rgba(255,255,255,0.04);
      --sw-border:rgba(255,255,255,0.09);
      --sw-text:#fafafa;
      --sw-muted:#a1a1aa;
      --sw-glow:rgba(${accentCss},0.35);
      position:fixed;bottom:24px;${posSide};z-index:2147483647;
      font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:var(--sw-text);
      -webkit-font-smoothing:antialiased;
    }
    #sarah-widget *{box-sizing:border-box}
    .sarah-glass{
      background:var(--sw-surface);
      backdrop-filter:blur(20px) saturate(160%);
      -webkit-backdrop-filter:blur(20px) saturate(160%);
      border:1px solid var(--sw-border);
    }
    #sarah-nudge{
      position:absolute;${panelSide};bottom:88px;width:min(340px,calc(100vw - 48px));
      padding:18px;border-radius:20px;
      box-shadow:0 20px 60px rgba(0,0,0,.45),0 0 0 1px rgba(255,255,255,.04) inset;
      opacity:0;pointer-events:none;transform:translateY(8px) scale(.98);
      transition:opacity .35s cubic-bezier(.16,1,.3,1),transform .35s cubic-bezier(.16,1,.3,1);
    }
    #sarah-nudge.visible{opacity:1;pointer-events:auto;transform:translateY(0) scale(1)}
    #sarah-nudge-text{margin:0;font-size:14px;line-height:1.55;color:#e4e4e7}
    .sarah-nudge-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:14px}
    .sarah-btn-ghost{padding:8px 14px;border-radius:10px;border:1px solid var(--sw-border);background:transparent;color:var(--sw-muted);font:inherit;font-size:13px;cursor:pointer;transition:border-color .2s,color .2s}
    .sarah-btn-ghost:hover{border-color:rgba(255,255,255,.2);color:#fff}
    .sarah-btn-primary{padding:8px 16px;border-radius:10px;border:none;background:linear-gradient(135deg,var(--sw-accent),color-mix(in srgb,var(--sw-accent) 70%,#fff));color:#fff;font:inherit;font-size:13px;font-weight:600;cursor:pointer;box-shadow:0 4px 20px var(--sw-glow)}
    #sarah-panel{
      position:absolute;${panelSide};bottom:80px;width:min(400px,calc(100vw - 32px));height:min(600px,calc(100vh - 100px));
      display:flex;flex-direction:column;border-radius:24px;overflow:hidden;
      background:rgba(6,6,10,0.88);
      box-shadow:0 32px 80px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.06) inset,0 0 60px rgba(${accentCss},0.08);
      opacity:0;pointer-events:none;transform:translateY(16px) scale(.96);
      transition:opacity .4s cubic-bezier(.16,1,.3,1),transform .4s cubic-bezier(.16,1,.3,1);
    }
    #sarah-panel.open{opacity:1;pointer-events:auto;transform:translateY(0) scale(1)}
    #sarah-header{position:relative;padding:0;border-bottom:1px solid var(--sw-border);overflow:hidden;flex-shrink:0}
    #sarah-ambient{position:absolute;inset:0;width:100%;height:100%;opacity:.55;pointer-events:none}
    .sarah-header-inner{position:relative;padding:18px 52px 16px 18px;z-index:1}
    .sarah-header-row{display:flex;align-items:center;gap:12px}
    .sarah-avatar{
      width:48px;height:48px;border-radius:50%;flex-shrink:0;position:relative;
      background:radial-gradient(circle at 35% 30%,rgba(255,255,255,0.1),rgba(6,6,12,0.95));
      border:1px solid rgba(255,255,255,0.12);
      box-shadow:0 0 28px rgba(${accentCss},0.35),0 0 0 1px rgba(${accentCss},0.15) inset;
      display:grid;place-items:center;overflow:visible;
    }
    .sarah-avatar::before{
      content:"";position:absolute;inset:-5px;border-radius:50%;
      border:1px dashed rgba(${accentCss},0.35);animation:sarah-orbit-spin 10s linear infinite;
    }
    .sarah-bot-svg{display:block}
    .sarah-bot-ring{transform-origin:32px 32px;animation:sarah-orbit-spin 14s linear infinite}
    .sarah-bot-eye{animation:sarah-eye-pulse 2.8s ease-in-out infinite}
    .sarah-bot-eye-r{animation-delay:.4s}
    .sarah-bot-core{animation:sarah-core-glow 2s ease-in-out infinite}
    .sarah-bot-node{animation:sarah-node-blink 3s ease infinite}
    .sarah-bot-node:nth-child(odd){animation-delay:.6s}
    @keyframes sarah-orbit-spin{to{transform:rotate(360deg)}}
    @keyframes sarah-eye-pulse{0%,100%{opacity:.75;filter:brightness(1)}50%{opacity:1;filter:brightness(1.4)}}
    @keyframes sarah-core-glow{0%,100%{opacity:.85;transform:scale(1)}50%{opacity:1;transform:scale(1.08)}}
    @keyframes sarah-node-blink{0%,100%{opacity:.4}50%{opacity:1}}
    .sarah-header-title{font-size:16px;font-weight:600;letter-spacing:-.02em}
    #sarah-subtitle{font-size:12px;color:var(--sw-muted);margin-top:2px;display:flex;align-items:center;gap:6px}
    .sarah-status-dot{width:7px;height:7px;border-radius:50%;background:#22c55e;box-shadow:0 0 8px #22c55e;animation:sarah-pulse 2s ease infinite}
    @keyframes sarah-pulse{0%,100%{opacity:1}50%{opacity:.45}}
    #sarah-close{
      position:absolute;top:14px;right:14px;z-index:2;width:32px;height:32px;border-radius:10px;
      border:1px solid var(--sw-border);background:rgba(255,255,255,.04);color:var(--sw-muted);
      cursor:pointer;font-size:16px;line-height:1;display:grid;place-items:center;transition:all .2s;
    }
    #sarah-close:hover{background:rgba(255,255,255,.08);color:#fff;border-color:rgba(255,255,255,.15)}
    #sarah-owner-badge{
      font-size:10px;padding:3px 8px;border-radius:999px;font-weight:600;letter-spacing:.04em;
      background:rgba(${accentCss},.18);color:color-mix(in srgb,var(--sw-accent) 80%,#fff);
      border:1px solid rgba(${accentCss},.3);
    }
    #sarah-chips{display:flex;flex-wrap:wrap;gap:8px;padding:12px 16px;border-bottom:1px solid var(--sw-border);flex-shrink:0}
    .sarah-chip{
      border:1px solid var(--sw-border);background:rgba(255,255,255,.03);color:#d4d4d8;
      border-radius:999px;padding:6px 12px;font-size:12px;font-weight:500;cursor:pointer;
      transition:all .25s cubic-bezier(.16,1,.3,1);
    }
    .sarah-chip:hover{border-color:rgba(${accentCss},.45);color:#fff;background:rgba(${accentCss},.12);box-shadow:0 0 20px rgba(${accentCss},.15)}
    #sarah-messages{flex:1;overflow:auto;padding:16px;display:flex;flex-direction:column;gap:12px;scroll-behavior:smooth}
    #sarah-messages::-webkit-scrollbar{width:5px}
    #sarah-messages::-webkit-scrollbar-thumb{background:rgba(255,255,255,.12);border-radius:99px}
    .sarah-bubble{
      max-width:88%;padding:12px 14px;border-radius:16px;font-size:14px;line-height:1.55;
      white-space:pre-wrap;animation:sarah-msg-in .35s cubic-bezier(.16,1,.3,1);
    }
    @keyframes sarah-msg-in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
    .sarah-bubble.user{
      align-self:flex-end;
      background:linear-gradient(135deg,var(--sw-accent),color-mix(in srgb,var(--sw-accent) 75%,#6366f1));
      color:#fff;border-bottom-right-radius:6px;box-shadow:0 4px 24px rgba(${accentCss},.25);
    }
    .sarah-bubble.assistant{
      align-self:flex-start;background:rgba(255,255,255,.05);border:1px solid var(--sw-border);
      border-bottom-left-radius:6px;
    }
    .sarah-msg-row{display:flex;align-items:flex-end;gap:8px;max-width:100%}
    .sarah-msg-row.assistant{align-self:flex-start}
    .sarah-msg-bot{
      width:28px;height:28px;border-radius:50%;flex-shrink:0;
      background:radial-gradient(circle,rgba(${accentCss},0.2),rgba(6,6,12,0.9));
      border:1px solid rgba(${accentCss},0.25);display:grid;place-items:center;
      box-shadow:0 0 12px rgba(${accentCss},0.2);
    }
    .sarah-msg-bot .sarah-bot-svg{width:22px;height:22px}
    .sarah-bubble.empty{align-self:center;text-align:center;color:var(--sw-muted);background:transparent;border:none;font-size:13px}
    #sarah-typing{display:none;padding:0 16px 8px}
    #sarah-typing.visible{display:block}
    .sarah-typing-bubble{
      display:inline-flex;align-items:center;gap:5px;padding:12px 16px;border-radius:16px;
      background:rgba(255,255,255,.05);border:1px solid var(--sw-border);
    }
    .sarah-typing-bubble span{width:6px;height:6px;border-radius:50%;background:rgba(${accentCss},.8);animation:sarah-dot 1.2s ease infinite}
    .sarah-typing-bubble span:nth-child(2){animation-delay:.15s}
    .sarah-typing-bubble span:nth-child(3){animation-delay:.3s}
    @keyframes sarah-dot{0%,80%,100%{transform:translateY(0);opacity:.4}40%{transform:translateY(-5px);opacity:1}}
    #sarah-form{display:flex;gap:10px;padding:14px 16px;border-top:1px solid var(--sw-border);background:rgba(0,0,0,.25);flex-shrink:0}
    #sarah-input{
      flex:1;min-height:44px;max-height:120px;border:1px solid var(--sw-border);border-radius:14px;
      background:rgba(255,255,255,.04);color:var(--sw-text);padding:11px 14px;resize:none;font:inherit;
      font-size:14px;line-height:1.4;transition:border-color .2s,box-shadow .2s;
    }
    #sarah-input:focus{outline:none;border-color:rgba(${accentCss},.5);box-shadow:0 0 0 3px rgba(${accentCss},.12)}
    #sarah-input::placeholder{color:#71717a}
    #sarah-send{
      width:44px;height:44px;flex-shrink:0;border:none;border-radius:14px;cursor:pointer;
      background:linear-gradient(135deg,var(--sw-accent),color-mix(in srgb,var(--sw-accent) 70%,#6366f1));
      color:#fff;font-size:18px;font-weight:600;
      box-shadow:0 4px 20px rgba(${accentCss},.35);transition:transform .2s,box-shadow .2s;
    }
    #sarah-send:hover:not(:disabled){transform:scale(1.05);box-shadow:0 6px 28px rgba(${accentCss},.45)}
    #sarah-send:disabled{opacity:.5;cursor:not-allowed}
    #sarah-launcher{
      position:relative;width:72px;height:72px;padding:0;border:none;border-radius:50%;cursor:pointer;
      background:radial-gradient(circle at 38% 32%,rgba(255,255,255,0.14),rgba(4,4,8,0.96) 52%,rgba(${accentCss},0.22));
      border:1px solid rgba(255,255,255,0.14);
      box-shadow:0 14px 48px rgba(${accentCss},0.45),0 0 0 1px rgba(255,255,255,0.06) inset;
      transition:transform .35s cubic-bezier(.16,1,.3,1),box-shadow .35s;
      display:grid;place-items:center;overflow:visible;
    }
    #sarah-launcher:hover{transform:scale(1.08) translateY(-3px);box-shadow:0 20px 56px rgba(${accentCss},0.55),0 0 40px rgba(${accentCss},0.2)}
    #sarah-launcher.open{transform:scale(.92);box-shadow:0 8px 32px rgba(${accentCss},0.35)}
    #sarah-launcher.thinking .sarah-bot-eye{animation:sarah-eye-think .5s ease-in-out infinite alternate}
    @keyframes sarah-eye-think{from{opacity:.5;transform:scaleY(.6)}to{opacity:1;transform:scaleY(1)}}
    .sarah-launcher-orbit{
      position:absolute;border-radius:50%;pointer-events:none;
      border:1px solid rgba(${accentCss},0.3);
    }
    .sarah-launcher-orbit-1{inset:3px;animation:sarah-orbit-spin 9s linear infinite}
    .sarah-launcher-orbit-2{
      inset:-8px;border-style:dashed;border-color:rgba(${accentCss},0.25);
      animation:sarah-orbit-spin 14s linear infinite reverse;
    }
    .sarah-launcher-orbit-3{
      inset:-14px;border:1px solid rgba(255,255,255,0.06);
      animation:sarah-orbit-spin 20s linear infinite;
    }
    .sarah-launcher-pulse{
      position:absolute;inset:-4px;border-radius:50%;
      background:radial-gradient(circle,rgba(${accentCss},0.25),transparent 70%);
      animation:sarah-launcher-breathe 3s ease-in-out infinite;z-index:0;
    }
    @keyframes sarah-launcher-breathe{0%,100%{opacity:.5;transform:scale(1)}50%{opacity:1;transform:scale(1.06)}}
    .sarah-launcher-bot{position:relative;z-index:1;display:grid;place-items:center}
    @media(max-width:480px){
      #sarah-panel{bottom:0;${config.position === "left" ? "left:0" : "right:0"};width:100vw;height:100vh;max-height:100vh;border-radius:0}
      #sarah-nudge{bottom:96px;width:calc(100vw - 32px)}
    }
    @media(prefers-reduced-motion:reduce){
      #sarah-panel,#sarah-nudge,.sarah-bubble,.sarah-launcher-orbit,.sarah-bot-ring,.sarah-status-dot,.sarah-launcher-pulse{animation:none!important;transition:none!important}
    }
  `;

  const miniBot = botFaceSvg("mini", 22);

  const root = document.createElement("div");
  root.id = "sarah-widget";
  root.innerHTML = `
    <style>${styles}</style>
    <div id="sarah-nudge" class="sarah-glass">
      <p id="sarah-nudge-text"></p>
      <div class="sarah-nudge-actions">
        <button type="button" id="sarah-dismiss" class="sarah-btn-ghost">Dismiss</button>
        <button type="button" id="sarah-open-nudge" class="sarah-btn-primary">Chat</button>
      </div>
    </div>
    <div id="sarah-panel" class="sarah-glass">
      <div id="sarah-header">
        <canvas id="sarah-ambient" aria-hidden="true"></canvas>
        <button type="button" id="sarah-close" aria-label="Close chat">×</button>
        <div class="sarah-header-inner">
          <div class="sarah-header-row">
            <div class="sarah-avatar" aria-hidden="true">${headerBot}</div>
            <div>
              <div class="sarah-header-row" style="gap:8px">
                <span class="sarah-header-title">${esc(config.title)}</span>
                <span id="sarah-owner-badge" style="display:none">OWNER</span>
              </div>
              <div id="sarah-subtitle"><span class="sarah-status-dot"></span><span id="sarah-status-text">Reading website…</span></div>
            </div>
          </div>
        </div>
      </div>
      <div id="sarah-chips"></div>
      <div id="sarah-messages"></div>
      <div id="sarah-typing"><div class="sarah-typing-bubble"><span></span><span></span><span></span></div></div>
      <form id="sarah-form">
        <textarea id="sarah-input" rows="1" placeholder="Ask about this website…"></textarea>
        <button id="sarah-send" type="submit" aria-label="Send">↑</button>
      </form>
    </div>
    <button id="sarah-launcher" type="button" aria-label="Open Sarah AI assistant">
      <span class="sarah-launcher-pulse" aria-hidden="true"></span>
      <span class="sarah-launcher-orbit sarah-launcher-orbit-1" aria-hidden="true"></span>
      <span class="sarah-launcher-orbit sarah-launcher-orbit-2" aria-hidden="true"></span>
      <span class="sarah-launcher-orbit sarah-launcher-orbit-3" aria-hidden="true"></span>
      <span class="sarah-launcher-bot" aria-hidden="true">${launcherBot}</span>
    </button>
  `;
  document.body.appendChild(root);

  subtitleEl = root.querySelector("#sarah-status-text");
  nudgeEl = root.querySelector("#sarah-nudge");
  chipsEl = root.querySelector("#sarah-chips");
  messagesEl = root.querySelector("#sarah-messages");
  input = root.querySelector("#sarah-input");
  sendBtn = root.querySelector("#sarah-send");
  panel = root.querySelector("#sarah-panel");
  typingEl = root.querySelector("#sarah-typing");
  ambientCanvas = root.querySelector("#sarah-ambient");

  function esc(t) {
    return String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }

  function setStatus(text) {
    if (subtitleEl) subtitleEl.textContent = text;
  }

  function updateNudge() {
    root.querySelector("#sarah-nudge-text").textContent = state.pageProfile.nudge;
    nudgeEl.classList.toggle("visible", !state.open && state.nudgeDismissedPath !== state.pathname);
  }

  function renderChips() {
    chipsEl.innerHTML = state.pageProfile.chips
      .map((c) => `<button type="button" class="sarah-chip" data-chip="${esc(c)}">${esc(c)}</button>`)
      .join("");
  }

  function renderMessages() {
    if (!state.messages.length) {
      messagesEl.innerHTML = `<div class="sarah-msg-row assistant"><div class="sarah-msg-bot">${miniBot}</div><div class="sarah-bubble assistant empty">${esc(state.pageProfile.nudge)}</div></div>`;
    } else {
      messagesEl.innerHTML = state.messages
        .filter((m) => m.content || m.role === "user")
        .map((m) => {
          if (m.role === "assistant") {
            return `<div class="sarah-msg-row assistant"><div class="sarah-msg-bot">${miniBot}</div><div class="sarah-bubble assistant">${esc(m.content)}</div></div>`;
          }
          return `<div class="sarah-bubble user">${esc(m.content)}</div>`;
        })
        .join("");
    }
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function setTyping(on) {
    if (typingEl) typingEl.classList.toggle("visible", on);
  }

  function setOpen(open) {
    state.open = open;
    panel.classList.toggle("open", open);
    const launcher = root.querySelector("#sarah-launcher");
    if (launcher) launcher.classList.toggle("open", open);
    if (open) {
      nudgeEl.classList.remove("visible");
      renderMessages();
      input.focus();
    } else {
      setTyping(false);
      updateNudge();
    }
  }

  function resizeInput() {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
  }

  /* Ambient header FX — Canvas 2D (all browsers) + optional WebGPU when data-fx="true" */
  let ambientStop = null;
  async function initAmbientFx() {
    if (!ambientCanvas || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const header = root.querySelector("#sarah-header");
    const resize = () => {
      ambientCanvas.width = header.offsetWidth;
      ambientCanvas.height = header.offsetHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    if (config.premiumFx && navigator.gpu) {
      try {
        ambientStop = await startWebGpuAmbient(ambientCanvas, accentRgb, resize);
        return;
      } catch {
        /* fall back to canvas 2d */
      }
    }
    ambientStop = startCanvas2dAmbient(ambientCanvas, accentRgb, resize);
  }

  function startCanvas2dAmbient(canvas, rgb, resize) {
    const ctx = canvas.getContext("2d");
    if (!ctx) return () => {};
    let t = 0;
    let raf = 0;
    const draw = () => {
      resize();
      const { width: w, height: h } = canvas;
      ctx.clearRect(0, 0, w, h);
      const g1 = ctx.createRadialGradient(
        w * (0.3 + Math.sin(t * 0.7) * 0.15),
        h * (0.4 + Math.cos(t * 0.5) * 0.2),
        0,
        w * 0.5,
        h * 0.5,
        w * 0.8
      );
      g1.addColorStop(0, `rgba(${rgb.r},${rgb.g},${rgb.b},0.35)`);
      g1.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = g1;
      ctx.fillRect(0, 0, w, h);
      const g2 = ctx.createRadialGradient(
        w * (0.75 + Math.cos(t * 0.6) * 0.1),
        h * (0.2 + Math.sin(t * 0.4) * 0.15),
        0,
        w * 0.5,
        h * 0.3,
        w * 0.6
      );
      g2.addColorStop(0, "rgba(99,102,241,0.2)");
      g2.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = g2;
      ctx.fillRect(0, 0, w, h);
      t += 0.016;
      raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(raf);
  }

  async function startWebGpuAmbient(canvas, rgb, resize) {
    const adapter = await navigator.gpu.requestAdapter({ powerPreference: "low-power" });
    if (!adapter) throw new Error("no adapter");
    const device = await adapter.requestDevice();
    const ctx = canvas.getContext("webgpu");
    if (!ctx) throw new Error("no webgpu context");
    const format = navigator.gpu.getPreferredCanvasFormat();
    let t = 0;
    let raf = 0;

    const shader = device.createShaderModule({
      code: `
        struct U { t: f32, accent: vec3f, pad: f32 }
        @group(0) @binding(0) var<uniform> u: U;
        @vertex fn vs(@builtin(vertex_index) i: u32) -> @builtin(position) vec4f {
          var p = array(vec2f(-1,-1), vec2f(3,-1), vec2f(-1,3));
          return vec4f(p[i], 0, 1);
        }
        @fragment fn fs(@builtin(position) pos: vec4f) -> @location(0) vec4f {
          let uv = pos.xy / vec2f(800.0, 120.0);
          let wave = sin(uv.x * 6.0 + u.t) * cos(uv.y * 4.0 - u.t * 0.7);
          let glow = smoothstep(0.2, 1.0, 1.0 - length(uv - vec2f(0.55 + sin(u.t)*0.08, 0.45)));
          return vec4f(u.accent * glow * 0.55 + vec3f(wave * 0.03), glow * 0.45);
        }
      `,
    });
    const layout = device.createBindGroupLayout({
      entries: [{ binding: 0, visibility: GPUShaderStage.FRAGMENT, buffer: { type: "uniform" } }],
    });
    const pipeline = device.createRenderPipeline({
      layout: device.createPipelineLayout({ bindGroupLayouts: [layout] }),
      vertex: { module: shader, entryPoint: "vs" },
      fragment: { module: shader, entryPoint: "fs", targets: [{ format }] },
      primitive: { topology: "triangle-list" },
    });
    const buf = device.createBuffer({ size: 16, usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST });
    const bind = device.createBindGroup({
      layout,
      entries: [{ binding: 0, resource: { buffer: buf } }],
    });

    const frame = () => {
      resize();
      ctx.configure({ device, format, alphaMode: "premultiplied" });
      const data = new Float32Array([t, rgb.r / 255, rgb.g / 255, rgb.b / 255]);
      device.queue.writeBuffer(buf, 0, data);
      const enc = device.createCommandEncoder();
      const pass = enc.beginRenderPass({
        colorAttachments: [{
          view: ctx.getCurrentTexture().createView(),
          clearValue: { r: 0, g: 0, b: 0, a: 0 },
          loadOp: "clear",
          storeOp: "store",
        }],
      });
      pass.setPipeline(pipeline);
      pass.setBindGroup(0, bind);
      pass.draw(3);
      pass.end();
      device.queue.submit([enc.finish()]);
      t += 0.02;
      raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(raf);
  }

  /* ─── Lead capture: visitor emails become leads for the site owner ─── */
  const Leads = {
    emailIn(text) {
      const m = text.match(/[^\s@]+@[^\s@]+\.[^\s@]{2,}/);
      return m ? m[0] : null;
    },

    async capture(email, message) {
      try {
        const res = await fetch(`${apiBase}/api/lead`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Client-Id": config.clientId,
          },
          body: JSON.stringify({ email, message, page: state.pathname }),
        });
        return res.ok;
      } catch {
        return false;
      }
    },

    async list() {
      const res = await fetch(`${apiBase}/api/leads`, {
        headers: {
          "X-Client-Id": config.clientId,
          "X-Admin-Token": adminToken,
        },
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Could not load leads");
      if (!data.leads.length) return "No leads yet. Visitors who share an email in chat are saved here automatically.";
      const lines = data.leads.map((l) => {
        const when = new Date(l.at).toLocaleString();
        return `• ${l.email} — ${when}${l.page ? ` (${l.page})` : ""}${l.message ? `\n  "${l.message.slice(0, 80)}"` : ""}`;
      });
      return `You have ${data.count} lead(s). Latest:\n${lines.join("\n")}`;
    },

    async exportCsv() {
      const res = await fetch(`${apiBase}/api/leads`, {
        headers: {
          "X-Client-Id": config.clientId,
          "X-Admin-Token": adminToken,
        },
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Could not export leads");
      if (!data.leads.length) return "No leads to export yet.";
      const rows = [["email", "name", "message", "page", "date"]];
      for (const l of data.leads) {
        rows.push([
          l.email,
          l.name || "",
          (l.message || "").replace(/"/g, '""'),
          l.page || "",
          new Date(l.at).toISOString(),
        ]);
      }
      const csv = rows.map((r) => r.map((c) => `"${c}"`).join(",")).join("\n");
      return `Exported ${data.leads.length} lead(s). Copy this CSV:\n\n${csv}`;
    },
  };

  async function handleSubmit(text) {
    const q = text.trim();
    if (!q || state.sending) return;

    state.messages.push({ role: "user", content: q });
    saveSession();
    renderMessages();

    state.sending = true;
    sendBtn.disabled = true;
    root.querySelector("#sarah-launcher")?.classList.add("thinking");
    const assistant = { role: "assistant", content: "" };
    state.messages.push(assistant);
    renderMessages();
    setTyping(true);

    let reply;
    if (state.ownerMode) {
      if (/^export\s+(my\s+)?leads?$/i.test(q)) {
        try {
          reply = await Leads.exportCsv();
        } catch (error) {
          reply = `Could not export leads: ${error.message}`;
        }
      } else if (/^(show|list)\s+(my\s+)?leads?$/i.test(q)) {
        try {
          reply = await Leads.list();
        } catch (error) {
          reply = `Could not load leads: ${error.message}`;
        }
      } else {
        const cmd = SiteControl.parseCommand(q);
        if (cmd.ok) {
          try {
            await SiteControl.save(cmd.mutations);
            reply = `${cmd.reply} Changes are live for all visitors.`;
          } catch (error) {
            reply = `Could not save: ${error.message}`;
          }
        } else {
          reply = cmd.reply;
        }
      }
    } else {
      const wantsSiteEdit =
        /(?:remove|hide|delete|change|update|edit|set|rename|restore|undo|revert|show|bring\s+back)\b.+(?:website|site|page|header|top|hours?|timing|price|color|section|changes?|panel)/i.test(q) ||
        (/(?:opening|closing).*(?:hours?|timing|time)/i.test(q) && /(?:remove|hide|delete|take\s+off|restore|show|bring\s+back)/i.test(q)) ||
        /(?:remove|hide|delete|take\s+off|restore|undo).*(?:opening|closing|business)?\s*(?:hours?|timing|time)/i.test(q);
      if (wantsSiteEdit) {
        reply =
          `I can update your website in owner mode only. Open your admin link or add ?sarah_admin=YOUR-TOKEN to the URL, then try:\n• hide opening hours\n• restore all changes\n• show top bar`;
      } else {
        const email = Leads.emailIn(q);
        if (email) {
          const saved = await Leads.capture(email, q);
          reply = saved
            ? `Thanks! I've passed your details (${email}) to the ${config.siteName} team — they'll follow up soon. Anything else I can help with meanwhile?`
            : `Thanks! I noted your email (${email}). If you don't hear back, please use the contact page too.`;
        } else {
          reply = Brain.answer(q);
          learnFromExchange(q, reply);
        }
      }
    }

    let firstToken = true;
    await streamReply(reply, (token) => {
      if (firstToken) {
        setTyping(false);
        firstToken = false;
      }
      assistant.content += token;
      renderMessages();
    });

    setTyping(false);

    saveSession();
    state.sending = false;
    sendBtn.disabled = false;
    root.querySelector("#sarah-launcher")?.classList.remove("thinking");
    input.focus();
  }

  function installPageListener() {
    const notify = () => applyPageContext(location.pathname);
    window.addEventListener("popstate", notify);
    window.addEventListener("hashchange", notify);
    ["pushState", "replaceState"].forEach((method) => {
      const orig = history[method];
      history[method] = function (...args) {
        const out = orig.apply(this, args);
        notify();
        return out;
      };
    });
    notify();
  }

  root.querySelector("#sarah-launcher").onclick = () => setOpen(!state.open);
  root.querySelector("#sarah-open-nudge").onclick = () => setOpen(true);
  root.querySelector("#sarah-close").onclick = () => setOpen(false);
  root.querySelector("#sarah-dismiss").onclick = () => {
    state.nudgeDismissedPath = state.pathname;
    updateNudge();
  };
  root.querySelector("#sarah-form").onsubmit = (e) => {
    e.preventDefault();
    handleSubmit(input.value);
    input.value = "";
    resizeInput();
  };
  input.addEventListener("input", resizeInput);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      root.querySelector("#sarah-form").requestSubmit();
    }
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && state.open) setOpen(false);
  });
  chipsEl.onclick = (e) => {
    const chip = e.target.closest("[data-chip]");
    if (!chip) return;
    setOpen(true);
    handleSubmit(chip.dataset.chip);
  };

  /* ─── Boot ─── */
  SiteBrain.indexDocument();
  installPageListener();
  renderChips();
  renderMessages();
  updateNudge();

  if (state.ownerMode) {
    const badge = root.querySelector("#sarah-owner-badge");
    if (badge) badge.style.display = "inline-block";
    input.placeholder = "Owner: rename bot, set prices, paste raw data…";
    setStatus("Owner control mode — changes apply site-wide");
    if (!state.messages.length) {
      state.messages.push({
        role: "assistant",
        content:
          "Owner mode active. Try:\n• hide opening hours\n• restore all changes\n• rename bot to Alex\n• set color to #22c55e\n• show leads\n• Paste FAQ or pricing (no prefix needed)",
      });
      saveSession();
    }
  }

  SiteControl.load().then(() => {
    if (!state.ownerMode) {
      setStatus(`Ready · ${state.siteIndex.chunks.length} sections indexed`);
    }
  });

  MetaStorage.write(MetaStorage.siteKey, state.siteIndex);

  queueMicrotask(() => {
    SiteBrain.crawlBackground().catch(() => {});
    initAmbientFx().catch(() => {});
  });
})();
