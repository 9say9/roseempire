/**
 * Rose Empire — lightweight conversion events for B2B funnels.
 * Pushes to dataLayer (GA4-ready) and CustomEvent for future tools.
 *
 * Events: quote_open | catalog_download | add_to_quote | rfq_submit | tel_click
 */
(function () {
  "use strict";

  window.dataLayer = window.dataLayer || [];

  function gaId() {
    const cfg = window.RoseEmpireConfig || {};
    const fromConfig = String(cfg.gaMeasurementId || "").trim();
    if (fromConfig) return fromConfig;
    const meta = document.querySelector('meta[name="ga-measurement-id"]');
    return String((meta && meta.getAttribute("content")) || "").trim();
  }

  function ensureGtag() {
    const id = gaId();
    if (!id || !/^G-[A-Z0-9]+$/i.test(id)) return;
    if (typeof window.gtag === "function" && window.__reGaLoaded) return;

    window.dataLayer = window.dataLayer || [];
    window.gtag = function () {
      window.dataLayer.push(arguments);
    };
    window.gtag("js", new Date());
    window.gtag("config", id, { send_page_view: true });

    if (!document.getElementById("re-ga4-script")) {
      const s = document.createElement("script");
      s.id = "re-ga4-script";
      s.async = true;
      s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(id);
      document.head.appendChild(s);
    }
    window.__reGaLoaded = true;
  }

  function pagePath() {
    try {
      return window.location.pathname || "/";
    } catch (_) {
      return "/";
    }
  }

  function track(eventName, params) {
    if (!eventName) return;
    const payload = Object.assign(
      {
        event: eventName,
        page_path: pagePath(),
        page_location: String(window.location.href || ""),
      },
      params || {}
    );

    window.dataLayer.push(payload);

    try {
      window.dispatchEvent(
        new CustomEvent("roseempire:conversion", { detail: payload })
      );
    } catch (_) {
      /* ignore */
    }

    if (typeof window.gtag === "function") {
      try {
        window.gtag("event", eventName, payload);
      } catch (_) {
        /* ignore */
      }
    }
  }

  function inferCatalogDownload(href) {
    const h = String(href || "").toLowerCase();
    return (
      h.includes("rose-empire-wholesale-catalog.pdf") ||
      (h.includes("catalog") && h.endsWith(".pdf"))
    );
  }

  function bindClicks(root) {
    const scope = root || document;
    scope.addEventListener(
      "click",
      function (e) {
        const el = e.target && e.target.closest
          ? e.target.closest("a, button, [data-track]")
          : null;
        if (!el) return;

        const trackName = el.getAttribute("data-track");
        const href = el.getAttribute("href") || "";

        if (trackName) {
          track(trackName, {
            link_text: (el.textContent || "").trim().slice(0, 80),
            link_url: href,
          });
          return;
        }

        if (href.indexOf("tel:") === 0) {
          track("tel_click", { phone: href.replace(/^tel:/i, "") });
          return;
        }

        if (el.hasAttribute("download") && inferCatalogDownload(href)) {
          track("catalog_download", { link_url: href });
        }
      },
      true
    );
  }

  window.RoseEmpireTrack = {
    event: track,
    quoteOpen: function (source) {
      track("quote_open", { source: source || "unknown" });
    },
    catalogDownload: function (source) {
      track("catalog_download", { source: source || "unknown" });
    },
    addToQuote: function (meta) {
      track("add_to_quote", meta || {});
    },
    rfqSubmit: function (meta) {
      track("rfq_submit", meta || {});
    },
    telClick: function (phone) {
      track("tel_click", { phone: phone || "" });
    },
  };

  function boot() {
    ensureGtag();
    bindClicks(document);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
