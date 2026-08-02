/**
 * Rose Empire — B2B conversion tracking (GA4 + dataLayer).
 *
 * Primary events:
 *   quote_click          — Request-a-quote button / link clicks
 *   contact_form_start   — first interaction with a contact/enquiry form
 *   contact_form_submit  — successful contact/enquiry/RFQ submit
 *   catalog_download     — trade catalog PDF download
 *   phone_click          — tel: link clicks
 *   email_click          — mailto: link clicks
 *
 * Also kept for funnel detail: add_to_quote | quote_open
 *
 * Placement: load after site-config.js on every public page.
 *   <script src="site-config.js" defer></script>
 *   <script src="conversion-analytics.js" defer></script>
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
        // GA4 prefers flat params; drop nested `event` key collision
        const gaParams = Object.assign({}, payload);
        delete gaParams.event;
        window.gtag("event", eventName, gaParams);
      } catch (_) {
        /* ignore */
      }
    }
  }

  function linkText(el) {
    return (el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 80);
  }

  function inferCatalogDownload(href) {
    const h = String(href || "").toLowerCase();
    return (
      h.includes("rose-empire-wholesale-catalog.pdf") ||
      (h.includes("catalog") && h.endsWith(".pdf"))
    );
  }

  function isQuoteControl(el) {
    if (!el) return false;
    if (el.getAttribute("data-track") === "quote_click") return true;
    if (el.id === "cart-toggle-btn" || el.id === "hero-request-quote" || el.id === "proceed-quote-btn") {
      return true;
    }
    if (el.classList && el.classList.contains("mobile-quote-bar-btn--primary")) return true;
    const href = el.getAttribute("href") || "";
    if (/[?&]openQuote=1\b/i.test(href) || href.indexOf("#get-quote") !== -1) return true;
    const text = linkText(el).toLowerCase();
    if (el.tagName === "BUTTON" || el.tagName === "A") {
      if (text === "request a quote" || text === "get a quote") return true;
    }
    return false;
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

        // Explicit data-track wins (except we still normalise known aliases)
        if (trackName && trackName !== "quote_click") {
          if (trackName === "tel_click") {
            track("phone_click", {
              phone: href.replace(/^tel:/i, ""),
              link_text: linkText(el),
            });
            return;
          }
          track(trackName, {
            link_text: linkText(el),
            link_url: href,
          });
          // Fall through for quote_click + tel/mailto/catalog inference when needed
          if (trackName === "catalog_download") return;
        }

        if (isQuoteControl(el)) {
          track("quote_click", {
            source: el.id || el.getAttribute("data-from") || trackName || "quote_cta",
            link_text: linkText(el),
            link_url: href,
          });
        }

        if (href.indexOf("tel:") === 0) {
          track("phone_click", {
            phone: href.replace(/^tel:/i, ""),
            link_text: linkText(el),
          });
          return;
        }

        if (href.indexOf("mailto:") === 0) {
          const email = href.replace(/^mailto:/i, "").split("?")[0];
          track("email_click", {
            email: email,
            link_text: linkText(el),
          });
          return;
        }

        if (el.hasAttribute("download") && inferCatalogDownload(href)) {
          track("catalog_download", {
            link_url: href,
            link_text: linkText(el),
          });
        }
      },
      true
    );
  }

  /** First focus/input on a contact form → contact_form_start (once per form). */
  function bindFormStarts(root) {
    const scope = root || document;
    scope.addEventListener(
      "focusin",
      function (e) {
        const field = e.target;
        if (!field || !field.closest) return;
        const form = field.closest(
          "form.quick-enquiry-form, form#rfq-submission-form, form[data-track-form='contact']"
        );
        if (!form || form.getAttribute("data-re-form-started") === "1") return;
        if (field.name === "website") return; // honeypot
        form.setAttribute("data-re-form-started", "1");
        const formId = form.id || form.className.split(/\s+/).find(Boolean) || "contact_form";
        track("contact_form_start", {
          form_id: formId,
          source: form.getAttribute("data-form-source") || formId,
        });
      },
      true
    );
  }

  window.RoseEmpireTrack = {
    event: track,

    quoteClick: function (source) {
      track("quote_click", { source: source || "unknown" });
    },
    /** Fired when the quote drawer actually opens */
    quoteOpen: function (source) {
      track("quote_open", { source: source || "unknown" });
    },

    contactFormStart: function (meta) {
      track("contact_form_start", meta || {});
    },
    contactFormSubmit: function (meta) {
      track("contact_form_submit", meta || {});
    },

    catalogDownload: function (source) {
      track("catalog_download", { source: source || "unknown" });
    },

    phoneClick: function (phone) {
      track("phone_click", { phone: phone || "" });
    },
    emailClick: function (email) {
      track("email_click", { email: email || "" });
    },

    addToQuote: function (meta) {
      track("add_to_quote", meta || {});
    },

    /** @deprecated use contactFormSubmit — kept so older call sites still work */
    rfqSubmit: function (meta) {
      track("contact_form_submit", Object.assign({ form_type: "rfq" }, meta || {}));
    },
    /** @deprecated use phoneClick */
    telClick: function (phone) {
      track("phone_click", { phone: phone || "" });
    },
  };

  function boot() {
    ensureGtag();
    bindClicks(document);
    bindFormStarts(document);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
