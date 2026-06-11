/* ==========================================================================
   Rose Empire Catalog Application Logic
   ========================================================================== */

// 1. Product catalog — loaded from catalog-data.json (single source of truth for site + bots)
let products = [];
let catalogData = null;

const CATALOG_URL = (location.hostname === "localhost" || location.hostname === "127.0.0.1")
    ? "catalog-data.json"
    : ((typeof RoseEmpireConfig !== "undefined" && RoseEmpireConfig.siteUrl)
        ? RoseEmpireConfig.siteUrl.replace(/\/$/, "") + "/catalog-data.json"
        : "catalog-data.json");

async function loadCatalog() {
    const grid = document.getElementById("products-grid");
    if (grid) {
        grid.innerHTML = '<div class="no-results"><i class="fa-solid fa-spinner fa-spin"></i><h3>Loading catalog…</h3></div>';
    }
    try {
        const res = await fetch(CATALOG_URL + "?v=" + encodeURIComponent(new Date().toISOString().slice(0, 10)));
        if (!res.ok) throw new Error("HTTP " + res.status);
        catalogData = await res.json();
        products = catalogData.products || [];
        window.RoseEmpireCatalog = catalogData;
    } catch (err) {
        console.error("Catalog load failed:", err);
        if (grid) {
            grid.innerHTML = '<div class="no-results"><i class="fa-solid fa-circle-exclamation"></i><h3>Could not load product catalog</h3><p>Refresh the page or contact info@roseempire.co.uk</p></div>';
        }
        products = [];
    }
}


