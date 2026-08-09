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

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function safeProductId(id) {
    const s = String(id || '');
    return /^[a-z0-9_-]+$/i.test(s) ? s : '';
}

async function loadCatalog() {
    const grid = document.getElementById("products-grid");
    if (grid) {
        grid.innerHTML = '<div class="no-results">' + roseIcon('spinner', true) + '<h3>Loading catalog…</h3></div>';
    }
    try {
        const res = await fetch(CATALOG_URL + "?v=20260809c");
        if (!res.ok) throw new Error("HTTP " + res.status);
        catalogData = await res.json();
        products = catalogData.products || [];
        window.RoseEmpireCatalog = catalogData;
    } catch (err) {
        console.error("Catalog load failed:", err);
        if (grid) {
            grid.innerHTML = '<div class="no-results"><svg class="ico" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><use href="assets/icons.svg#warn"></use></svg><h3>Could not load product catalog</h3><p>Refresh the page or contact info@roseempire.co.uk</p></div>';
        }
        products = [];
    }
}

function getSizeMeta(product, sizeIndex) {
    const size = product?.sizes?.[sizeIndex];
    if (!size) {
        return { name: '', price: 0, wasPrice: 0, moq: 20, piecesPerBox: 20 };
    }
    const name = size.name || '';
    let piecesPerBox = Number(size.piecesPerBox) || Number(product.piecesPerBox) || 0;
    if (!piecesPerBox) {
        if (product.category === 'pillows') piecesPerBox = 5;
        else if (/pillow/i.test(name)) piecesPerBox = 40;
        else piecesPerBox = 20;
    }
    const moq = Number(size.moq) || piecesPerBox;
    return {
        name,
        price: Number(size.price) || 0,
        wasPrice: Number(size.wasPrice) || 0,
        moq,
        piecesPerBox,
    };
}

/** Featured was/now price for promo cards (prefers Single / promo.example*). */
function getPromoDisplayPrice(product) {
    const promo = product?.promo;
    if (!promo) return null;
    const exampleWas = Number(promo.exampleWas) || 0;
    const exampleNow = Number(promo.exampleNow) || 0;
    if (exampleWas > exampleNow && exampleNow > 0) {
        return {
            was: exampleWas,
            now: exampleNow,
            sizeLabel: promo.exampleSize || '',
            save: Math.round((exampleWas - exampleNow) * 100) / 100,
            badge: promo.badge || promo.label || 'Sale',
            detail: promo.detail || '',
            headline: promo.headline || promo.label || 'Sale',
        };
    }
    const withWas = (product.sizes || []).find((s) => Number(s.wasPrice) > Number(s.price));
    if (!withWas) return null;
    const was = Number(withWas.wasPrice);
    const now = Number(withWas.price);
    return {
        was,
        now,
        sizeLabel: withWas.name || '',
        save: Math.round((was - now) * 100) / 100,
        badge: promo.badge || promo.label || 'Sale',
        detail: promo.detail || '',
        headline: promo.headline || promo.label || 'Sale',
    };
}

function snapToBoxes(pieces, piecesPerBox) {
    const box = Math.max(1, piecesPerBox || 20);
    const qty = Math.max(box, parseInt(pieces, 10) || box);
    return Math.ceil(qty / box) * box;
}

function boxesFromPieces(pieces, piecesPerBox) {
    const box = Math.max(1, piecesPerBox || 20);
    return Math.max(1, Math.round((parseInt(pieces, 10) || box) / box));
}

function buildDetailGallery(product) {
    // Keep size page simple: one main product photo only.
    const src = product.image || (product.gallery && product.gallery[0]) || '';
    const fallback = `https://placehold.co/400x300/0d1f3c/ffffff?text=${encodeURIComponent(product.title)}`;
    return `<img src="${src}" alt="${product.title}" class="detail-gallery-main"
              onerror="this.src='${fallback}'">`;
}

function renderDetailBasketPreview() {
    const el = document.getElementById('detail-basket-preview');
    if (!el) return;
    if (!cart.length) {
        el.innerHTML = `<p class="detail-basket-empty">Basket empty — add sizes below. Full boxes only.</p>`;
        return;
    }
    const rows = cart.map((item, idx) => {
        const boxes = boxesFromPieces(item.quantity, item.piecesPerBox || item.moq || 20);
        const perBox = item.piecesPerBox || item.moq || 20;
        return `<li>
            <span><strong>${item.title}</strong> · ${item.sizeName}</span>
            <span>${boxes} box${boxes === 1 ? '' : 'es'} (${item.quantity} pcs · ${perBox}/box)</span>
            <button type="button" class="detail-basket-remove" onclick="removeFromCart(${idx}); refreshOpenDetailBasket();" aria-label="Remove">×</button>
        </li>`;
    }).join('');
    el.innerHTML = `
        <h4 class="detail-basket-title">In your basket</h4>
        <ul class="detail-basket-list">${rows}</ul>`;
}

function refreshOpenDetailBasket() {
    renderDetailBasketPreview();
    const viewBtn = modalDetailBody?.querySelector('[data-view-basket]');
    if (viewBtn) {
        viewBtn.textContent = `View Basket (${cart.length} size${cart.length === 1 ? '' : 's'})`;
    }
    updateCartBadge();
}


// ==========================================================================
// Application State
// ==========================================================================
const CART_STORAGE_KEY = 're-quote-cart-v1';
let cart = [];
let currentFilter = 'all';
let currentSearch = '';

function loadCart() {
    try {
        const raw = localStorage.getItem(CART_STORAGE_KEY);
        const parsed = raw ? JSON.parse(raw) : [];
        if (!Array.isArray(parsed)) {
            cart = [];
            return;
        }
        cart = parsed
            .filter((item) => item && item.productId && item.sizeName)
            .map((item) => {
                let piecesPerBox = parseInt(item.piecesPerBox, 10) || 0;
                if (!piecesPerBox) {
                    if (item.category === 'pillows') piecesPerBox = 5;
                    else if (/pillow/i.test(item.sizeName || '')) piecesPerBox = 40;
                    else piecesPerBox = 20;
                }
                const moq = parseInt(item.moq, 10) || piecesPerBox;
                return {
                    ...item,
                    piecesPerBox,
                    moq,
                    quantity: snapToBoxes(item.quantity, piecesPerBox),
                };
            });
        saveCart();
    } catch {
        cart = [];
    }
}

function saveCart() {
    try {
        localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
    } catch {
        /* ignore quota / private mode */
    }
}

function clearCart() {
    cart = [];
    saveCart();
    updateCartBadge();
    renderCartItems();
}

// DOM Elements
const productsGrid      = document.getElementById('products-grid');
const filterTabs        = document.getElementById('filter-tabs');
const searchInput       = document.getElementById('catalog-search');
const cartToggleBtn     = document.getElementById('cart-toggle-btn');
const cartDrawer        = document.getElementById('cart-drawer');
const cartCloseBtn      = document.getElementById('cart-close-btn');
const drawerOverlay     = document.getElementById('drawer-overlay');
const cartBadgeCount    = document.getElementById('cart-badge-count');
const cartDrawerItems   = document.getElementById('cart-drawer-items');
const summaryUniqueCount= document.getElementById('summary-unique-count');
const summaryTotalPacks = document.getElementById('summary-total-packs');
const summaryTotalPrice = document.getElementById('summary-total-price');
const proceedQuoteBtn   = document.getElementById('proceed-quote-btn');
const stripeCheckoutBtn = document.getElementById('stripe-checkout-btn');
const themeToggle       = document.getElementById('theme-toggle');
const productDetailModal= document.getElementById('product-detail-modal');
const modalDetailBody   = document.getElementById('modal-detail-body');
const modalCloseDetail  = document.getElementById('modal-close-detail');
const rfqFormModal      = document.getElementById('rfq-form-modal');
const modalCloseRfq     = document.getElementById('modal-close-rfq');
const rfqForm           = document.getElementById('rfq-submission-form');
const rfqBackBtn        = document.getElementById('rfq-back-btn');

// ==========================================================================
// Icons (local SVG sprite — no Font Awesome)
// ==========================================================================
function setSvgIcon(container, name, spin) {
    if (!container) return;
    const svg = container.querySelector('svg') || container;
    if (!svg || svg.tagName !== 'svg') return;
    let use = svg.querySelector('use');
    if (!use) {
        use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
        svg.appendChild(use);
    }
    use.setAttribute('href', `assets/icons.svg#${name}`);
    svg.classList.toggle('ico-spin', Boolean(spin));
}

function roseIcon(name, spin) {
    const cls = spin ? 'ico ico-spin' : 'ico';
    return `<svg class="${cls}" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><use href="assets/icons.svg#${name}"></use></svg>`;
}

// ==========================================================================
// Theme Setup
// ==========================================================================
function initTheme() {
    const saved = localStorage.getItem('re-theme') || 'light';
    document.body.classList.remove('light-mode', 'dark-mode');
    document.body.classList.add(saved === 'dark' ? 'dark-mode' : 'light-mode');
    setSvgIcon(themeToggle, saved === 'dark' ? 'sun' : 'moon');
}

themeToggle.addEventListener('click', () => {
    const isDark = document.body.classList.contains('dark-mode');
    document.body.classList.toggle('dark-mode', !isDark);
    document.body.classList.toggle('light-mode', isDark);
    setSvgIcon(themeToggle, isDark ? 'moon' : 'sun');
    localStorage.setItem('re-theme', isDark ? 'light' : 'dark');
});

// ==========================================================================
// Catalog Rendering
// ==========================================================================
function renderProducts() {
    productsGrid.innerHTML = '';

    const filtered = products.filter(p => {
        const catOk   = currentFilter === 'all' || p.category === currentFilter;
        const q       = currentSearch.toLowerCase();
        const searchOk = !q ||
            p.title.toLowerCase().includes(q) ||
            p.desc.toLowerCase().includes(q) ||
            p.highlights.some(h => h.toLowerCase().includes(q));
        return catOk && searchOk;
    });

    if (filtered.length === 0) {
        productsGrid.innerHTML = `
            <div class="no-results">
                <svg class="ico" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><use href="assets/icons.svg#info"></use></svg>
                <h3>No products found</h3>
                <p>Try clearing your search or changing the category filter.</p>
            </div>`;
        return;
    }

    filtered.forEach((product, i) => {
        const card = document.createElement('div');
        card.className = 'product-card animate-in';
        card.style.animationDelay = `${i * 0.06}s`;

        const promo = getPromoDisplayPrice(product);
        const priceHtml = promo
            ? `<div class="price-stack">
                    <span class="price-was">Was £${promo.was.toFixed(2)}</span>
                    <span class="price-value price-value--sale">£${promo.now.toFixed(2)}/pc</span>
                    <span class="price-save">${escapeHtml(promo.detail || ('Save £' + promo.save.toFixed(2)))}</span>
               </div>`
            : `<span class="price-value">£${Number(product.basePrice || 0).toFixed(2)}/pc</span>`;
        const promoBanner = promo
            ? `<div class="product-promo-banner" role="status"><span>${escapeHtml(promo.badge)}</span><span>${escapeHtml(promo.headline)}</span></div>`
            : '';
        const tagLabel = product.promo?.badge || product.tag;
        const pid = safeProductId(product.id);
        if (!pid) return;

        card.innerHTML = `
            <div class="product-image-container${promo ? ' product-image-container--sale' : ''}">
                <span class="product-tag">${escapeHtml(tagLabel)}</span>
                <img src="${escapeHtml(product.image)}" alt="${escapeHtml(product.title)}"
                     onerror="this.src='https://placehold.co/400x300/0d1f3c/ffffff?text=${encodeURIComponent(product.title)}'">
                ${promoBanner}
            </div>
            <div class="product-info">
                <h3 class="product-title">${escapeHtml(product.title)}</h3>
                <p class="product-desc">${escapeHtml(product.desc)}</p>
                <div class="product-specs">
                    ${(product.highlights || []).slice(0, 3).map(h => `<span class="spec-badge">${escapeHtml(h)}</span>`).join('')}
                </div>
                <div class="product-pricing-moq">
                    <div class="moq-box-badge"><svg class="ico" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><use href="assets/icons.svg#box"></use></svg> ${escapeHtml(product.boxLabel || product.moq + ' pieces min.')}</div>
                    <div class="product-pricing-row">
                    <div class="pricing-info">
                        <span class="moq-label">Min. Order (MOQ)</span>
                        <span class="price-value">${Number(product.moq) || 20} Pieces</span>
                    </div>
                    <div class="pricing-info" style="text-align:right">
                        <span class="moq-label">${promo ? escapeHtml(promo.sizeLabel ? promo.sizeLabel + ' now' : 'Sale from') : 'From'}</span>
                        ${priceHtml}
                    </div>
                    </div>
                </div>
                <div class="product-actions">
                    <button class="btn btn-navy-sm btn-block" onclick="openProductDetail('${pid}')">
                        <svg class="ico" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><use href="assets/icons.svg#cart"></use></svg> View sizes &amp; add
                    </button>
                </div>
            </div>`;

        productsGrid.appendChild(card);
    });
}

function setCategoryFilter(category) {
    currentFilter = category;
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.toggle('active', tab.getAttribute('data-category') === category);
    });
    renderProducts();
}

searchInput.addEventListener('input', e => {
    currentSearch = e.target.value;
    renderProducts();
});

filterTabs.addEventListener('click', e => {
    if (e.target.classList.contains('filter-tab')) {
        setCategoryFilter(e.target.getAttribute('data-category'));
    }
});

// ==========================================================================
// Quote Cart
// ==========================================================================
function setCartDrawerOpen(isOpen, source) {
    const opening = Boolean(isOpen) && !cartDrawer.classList.contains('open');
    cartDrawer.classList.toggle('open', isOpen);
    drawerOverlay.classList.toggle('open', isOpen);
    document.body.classList.toggle('cart-drawer-open', isOpen);
    if (opening && window.RoseEmpireTrack?.quoteOpen) {
        window.RoseEmpireTrack.quoteOpen(source || 'cart_drawer');
    }

    // Live Sarah widget uses max z-index and can sit over the cart footer.
    // Hide it while checkout is open so email/Stripe match localhost clickability.
    document.querySelectorAll('#sarah-widget, #sarah-launcher, #sarah-nudge, #sarah-panel').forEach((el) => {
        if (isOpen) {
            el.style.setProperty('display', 'none', 'important');
            el.style.setProperty('pointer-events', 'none', 'important');
            el.style.setProperty('visibility', 'hidden', 'important');
        } else {
            el.style.removeProperty('display');
            el.style.removeProperty('pointer-events');
            el.style.removeProperty('visibility');
        }
    });

    if (isOpen) {
        // Show basket items first — not the delivery form.
        requestAnimationFrame(() => {
            const scroll = document.getElementById('cart-drawer-scroll');
            if (scroll) scroll.scrollTop = 0;
            const body = document.getElementById('cart-drawer-items');
            if (body) body.scrollTop = 0;
        });
    }
}

function toggleCartDrawer() {
    setCartDrawerOpen(!cartDrawer.classList.contains('open'));
}

cartToggleBtn.addEventListener('click', toggleCartDrawer);
cartCloseBtn.addEventListener('click', toggleCartDrawer);
drawerOverlay.addEventListener('click', () => setCartDrawerOpen(false));

function updateCartBadge() {
    const total = cart.reduce((a, i) => a + i.quantity, 0);
    cartBadgeCount.textContent = total;
}

function renderCartItems() {
    if (cart.length === 0) {
        cartDrawerItems.innerHTML = `
            <div class="empty-cart-message">
                <svg class="ico" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><use href="assets/icons.svg#folder"></use></svg>
                <p><strong>Your quote list is empty</strong></p>
                <ol class="empty-cart-steps">
                    <li>Browse the wholesale catalog</li>
                    <li>Add full boxes by size</li>
                    <li>Request a quote or pay by card</li>
                </ol>
                <div class="empty-cart-actions">
                    <button type="button" class="btn btn-gold btn-sm" onclick="setCartDrawerOpen(false); document.getElementById('catalog-section')?.scrollIntoView({behavior:'smooth'});">
                        Browse catalog
                    </button>
                    <a href="assets/Rose-Empire-Wholesale-Catalog.pdf?v=20260802h" class="btn btn-outline-dark btn-sm" download data-track="catalog_download">
                        Download catalog
                    </a>
                </div>
                ${quickEnquiryFormHTML('empty-quote-drawer')}
            </div>`;
        proceedQuoteBtn.disabled = true;
        if (stripeCheckoutBtn) stripeCheckoutBtn.disabled = true;
        QuoteRequestPricingUI.resetSummary();
        return;
    }

    cartDrawerItems.innerHTML = '';

    cart.forEach((item, idx) => {
        const unit = item.unitPrice || 0;
        const lineTotal = QuotePricing.lineTotal(item.quantity, unit);
        const perBox = item.piecesPerBox || item.moq || 20;
        const boxes = boxesFromPieces(item.quantity, perBox);
        const belowMOQ = item.quantity < (item.moq || perBox);

        const div = document.createElement('div');
        div.className = 'cart-item';
        div.innerHTML = `
            <button class="cart-item-remove" onclick="removeFromCart(${idx})" aria-label="Remove">
                <svg class="ico" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><use href="assets/icons.svg#trash"></use></svg>
            </button>
            <div class="cart-item-image">
                <img src="${item.image}" alt="${item.title}"
                     onerror="this.src='https://placehold.co/100/0d1f3c/ffffff?text=RE'">
            </div>
            <div class="cart-item-details">
                <h4 class="cart-item-title">${item.title}</h4>
                <div class="cart-item-meta">
                    <div>Size: <strong>${item.sizeName}</strong></div>
                    <div>Wholesale rate: <strong>${QuotePricing.formatGBP(unit)}/piece</strong></div>
                    <div>Box: <strong>${perBox} pcs</strong> · full boxes only</div>
                </div>
                <div class="cart-item-controls">
                    <div class="qty-selector">
                        <button class="qty-btn" type="button" onclick="adjustCartQty(${idx}, -1)">-1 box</button>
                        <input type="number" class="qty-input" value="${item.quantity}" min="${perBox}"
                               step="${perBox}" data-cart-idx="${idx}" aria-label="Piece quantity" readonly>
                        <button class="qty-btn" type="button" onclick="adjustCartQty(${idx}, 1)">+1 box</button>
                    </div>
                    <div class="cart-item-total">${QuotePricing.formatGBP(lineTotal)}<small style="display:block;font-weight:600;opacity:.7">${boxes} box${boxes === 1 ? '' : 'es'}</small></div>
                </div>
                ${belowMOQ ? `
                <div class="moq-warning" style="grid-column:1/-1">
                    <svg class="ico" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><use href="assets/icons.svg#warn"></use></svg> Below 1 box (${perBox} pcs)
                </div>` : ''}
            </div>`;
        cartDrawerItems.appendChild(div);
    });

    CheckoutTotalsUI.refresh(cart);

    const hasMOQFail = cart.some(i => i.quantity < (i.moq || i.piecesPerBox || 20));
    proceedQuoteBtn.disabled = hasMOQFail;
    proceedQuoteBtn.textContent = hasMOQFail
        ? 'Resolve box quantity warnings'
        : 'Proceed to Request Quote';
    if (stripeCheckoutBtn) stripeCheckoutBtn.disabled = false;
}

function showCheckoutBanner(type, message) {
    let banner = document.getElementById('checkout-status-banner');
    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'checkout-status-banner';
        banner.setAttribute('role', 'status');
        banner.className = 'checkout-status-banner';
        document.body.prepend(banner);
    }
    banner.className = `checkout-status-banner checkout-status-banner--${type}`;
    banner.textContent = message;
    banner.hidden = false;
    window.setTimeout(() => {
        banner.hidden = true;
    }, 10000);
}

function getCheckoutEmail() {
    const cartEmail = document.getElementById('cart-checkout-email');
    const rfqEmail = document.getElementById('rfq-email');
    const fromCart = cartEmail ? cartEmail.value.trim() : '';
    const fromRfq = rfqEmail ? rfqEmail.value.trim() : '';
    return fromCart || fromRfq;
}

function getCheckoutShippingRegion() {
    const cartShip = document.getElementById('cart-shipping-region');
    const rfqShip = document.getElementById('rfq-shipping-region');
    if (cartShip && cartShip.value) return cartShip.value;
    if (rfqShip && rfqShip.value) return rfqShip.value;
    return 'mainland';
}

function getCartShippingAddress() {
    const val = (id) => (document.getElementById(id)?.value || '').trim();
    return {
        name: val('cart-ship-name'),
        company: val('cart-ship-company'),
        phone: val('cart-ship-phone'),
        line1: val('cart-ship-line1'),
        line2: val('cart-ship-line2'),
        city: val('cart-ship-city'),
        postcode: val('cart-ship-postcode').toUpperCase(),
        region: getCheckoutShippingRegion(),
    };
}

function formatShippingAddressBlock(addr) {
    return [
        addr.name,
        addr.company,
        addr.line1,
        addr.line2,
        addr.city,
        addr.postcode,
        addr.phone ? `Tel: ${addr.phone}` : '',
    ].filter(Boolean).join('\n');
}

function validateCartShippingAddress(addr) {
    if (!addr.name) return { ok: false, field: 'cart-ship-name', message: 'Enter the delivery contact name.' };
    if (!addr.phone || addr.phone.length < 7) return { ok: false, field: 'cart-ship-phone', message: 'Enter a delivery phone number.' };
    if (!addr.line1) return { ok: false, field: 'cart-ship-line1', message: 'Enter delivery address line 1.' };
    if (!addr.city) return { ok: false, field: 'cart-ship-city', message: 'Enter the town / city.' };
    if (!addr.postcode || addr.postcode.length < 5) {
        return { ok: false, field: 'cart-ship-postcode', message: 'Enter a valid UK postcode.' };
    }
    return { ok: true };
}

function syncCartAddressToRfq(addr, email) {
    const setIf = (id, value) => {
        const el = document.getElementById(id);
        if (el && value) el.value = value;
    };
    setIf('rfq-email', email);
    setIf('rfq-name', addr.name);
    setIf('rfq-company', addr.company);
    setIf('rfq-phone', addr.phone);
    setIf('rfq-shipping-region', addr.region);
    const addressEl = document.getElementById('rfq-address');
    if (addressEl) addressEl.value = formatShippingAddressBlock(addr);
}

// ==========================================================================
// Lead capture — server-side RFQ / enquiry delivery (worker /api/rfq)
// ==========================================================================
async function submitLeadToServer(payload) {
    const base = (window.RoseEmpireConfig && window.RoseEmpireConfig.checkoutApiUrl) || '';
    if (!base) return { ok: false };
    try {
        const resp = await fetch(`${base.replace(/\/$/, '')}/api/rfq`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await resp.json().catch(() => ({}));
        return { ok: resp.ok && data.status === 'success', data };
    } catch (err) {
        console.error('Lead submit failed', err);
        return { ok: false };
    }
}

function setDeliveryPanelOpen(open) {
    const details = document.getElementById('cart-delivery-details');
    if (details) details.open = Boolean(open);
}

/** Quick enquiry forms (empty quote drawer + footer). Returns false to stop native submit. */
async function handleQuickEnquiry(form, source) {
    const val = (name) => (form.querySelector(`[name="${name}"]`)?.value || '').trim();
    const name = val('name');
    const email = val('email');
    if (!name || !email || !email.includes('@')) {
        alert('Please enter your name and a valid email so we can reply.');
        return false;
    }

    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn ? btn.textContent : '';
    if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }

    const payload = {
        leadType: 'quick_enquiry',
        name,
        company: val('company'),
        email,
        phone: val('phone'),
        notes: val('message'),
        website: val('website'), // honeypot
        source: `roseempire.co.uk ${source}`,
    };

    const result = await submitLeadToServer(payload);
    if (btn) { btn.disabled = false; btn.textContent = originalText; }

    if (result.ok) {
        if (window.RoseEmpireTrack?.contactFormSubmit) {
            window.RoseEmpireTrack.contactFormSubmit({
                form_type: 'quick_enquiry',
                source: source || 'unknown',
            });
        }
        form.reset();
        form.innerHTML = '<p class="quick-enquiry-success">Thanks — your enquiry is with our sales team. We reply within 1 business day.</p>';
    } else {
        const subject = encodeURIComponent(`Wholesale enquiry — ${payload.company || name}`);
        const body = encodeURIComponent(
            `Name: ${name}\nCompany: ${payload.company}\nPhone: ${payload.phone}\n\n${payload.notes}`
        );
        window.location.href = `mailto:info@roseempire.co.uk?subject=${subject}&body=${body}`;
    }
    return false;
}
window.handleQuickEnquiry = handleQuickEnquiry;

function quickEnquiryFormHTML(source) {
    return `
        <form class="quick-enquiry-form" data-form-source="${source}" data-track-form="contact"
              onsubmit="event.preventDefault(); handleQuickEnquiry(this, '${source}');">
            <p class="quick-enquiry-title">Or send a quick enquiry — no sizes needed:</p>
            <input type="text" name="name" placeholder="Your name *" autocomplete="name" required>
            <input type="text" name="company" placeholder="Company / facility" autocomplete="organization">
            <input type="email" name="email" placeholder="Work email *" autocomplete="email" required>
            <input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px">
            <textarea name="message" rows="2" placeholder="e.g. 60 single Terry protectors for a 20-room hotel"></textarea>
            <button type="submit" class="btn btn-gold btn-sm btn-block">Send enquiry</button>
        </form>`;
}

async function startStripeCheckout() {
    if (!cart.length) {
        showCheckoutBanner('error', 'Add products to your quote list before starting checkout.');
        return;
    }

    const checkoutBase = (window.RoseEmpireConfig && window.RoseEmpireConfig.checkoutApiUrl) || '';
    const checkoutUrl = checkoutBase ? `${checkoutBase.replace(/\/$/, '')}/api/checkout/create` : '/api/checkout/create';
    const shippingRegion = getCheckoutShippingRegion();
    const customerEmail = getCheckoutEmail();
    const cartEmailField = document.getElementById('cart-checkout-email');
    const shippingAddress = getCartShippingAddress();

    if (!customerEmail || !customerEmail.includes('@')) {
        setDeliveryPanelOpen(true);
        showCheckoutBanner('error', 'Enter your email in the delivery details, then try again.');
        cartEmailField?.focus();
        return;
    }

    const addressCheck = validateCartShippingAddress(shippingAddress);
    if (!addressCheck.ok) {
        setDeliveryPanelOpen(true);
        showCheckoutBanner('error', addressCheck.message);
        document.getElementById(addressCheck.field)?.focus();
        return;
    }

    syncCartAddressToRfq(shippingAddress, customerEmail);

    if (stripeCheckoutBtn) {
        stripeCheckoutBtn.disabled = true;
        stripeCheckoutBtn.innerHTML = '<svg class="ico ico-spin" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><use href="assets/icons.svg#spinner"></use></svg> Preparing checkout…';
    }

    try {
        const response = await fetch(checkoutUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                items: cart,
                domain: window.location.origin,
                shippingRegion,
                customerEmail,
                shippingAddress,
            })
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok || data.status !== 'success' || !data.url) {
            throw new Error(data.message || 'Stripe checkout is unavailable right now.');
        }
        window.location.href = data.url;
    } catch (err) {
        console.error(err);
        showCheckoutBanner(
            'error',
            err.message || 'Stripe checkout could not be started. Contact info@roseempire.co.uk.'
        );
    } finally {
        if (stripeCheckoutBtn) {
            stripeCheckoutBtn.disabled = false;
            stripeCheckoutBtn.innerHTML = '<svg class="ico" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><use href="assets/icons.svg#card"></use></svg> Secure Stripe Checkout';
        }
    }
}

function addToCart(productId, sizeIndex, quantity, { keepModalOpen = true } = {}) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    const meta = getSizeMeta(product, sizeIndex);
    if (!meta.name) return;
    const piecesPerBox = meta.piecesPerBox;
    const qty = snapToBoxes(quantity, piecesPerBox);
    const sizeName = meta.name;
    const existing = cart.findIndex(i => i.productId === productId && i.sizeName === sizeName);

    if (existing > -1) {
        cart[existing].quantity = snapToBoxes(cart[existing].quantity + qty, piecesPerBox);
        cart[existing].unitPrice = meta.price;
        cart[existing].moq = meta.moq;
        cart[existing].piecesPerBox = piecesPerBox;
    } else {
        cart.push({
            productId: product.id,
            title:     product.title,
            image:     product.image,
            category:  product.category,
            sizeName,
            unitPrice: meta.price,
            quantity:  qty,
            moq:       meta.moq,
            piecesPerBox,
        });
    }

    saveCart();
    updateCartBadge();
    renderCartItems();
    refreshOpenDetailBasket();

    if (window.RoseEmpireTrack?.addToQuote) {
        window.RoseEmpireTrack.addToQuote({
            product_id: product.id,
            size_name: sizeName,
            quantity: qty,
            unit_price: meta.price,
        });
    }

    if (keepModalOpen && productDetailModal.classList.contains('open')) {
        showAddToast(sizeName, qty, piecesPerBox);
        return;
    }

    closeModal();
    setTimeout(() => setCartDrawerOpen(true), 120);
}

function showAddToast(sizeName, qty, piecesPerBox) {
    let toast = document.getElementById('cart-add-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'cart-add-toast';
        toast.className = 'cart-add-toast';
        toast.setAttribute('role', 'status');
        document.body.appendChild(toast);
    }
    const boxes = boxesFromPieces(qty, piecesPerBox);
    toast.innerHTML = `
        <strong>✓ ${sizeName}</strong> added — ${boxes} box${boxes === 1 ? '' : 'es'} (${qty} pcs).
        <span>Add another size, or <button type="button" class="cart-add-toast-link" id="cart-add-toast-view">Review quote</button></span>`;
    toast.classList.add('visible');
    const viewBtn = document.getElementById('cart-add-toast-view');
    if (viewBtn) {
        viewBtn.onclick = () => {
            toast.classList.remove('visible');
            closeModal();
            setCartDrawerOpen(true, 'add_toast');
        };
    }
    clearTimeout(showAddToast._timer);
    showAddToast._timer = setTimeout(() => toast.classList.remove('visible'), 4500);
}

function removeFromCart(idx) {
    cart.splice(idx, 1);
    saveCart();
    updateCartBadge();
    renderCartItems();
    refreshOpenDetailBasket();
}

function adjustCartQty(idx, boxDelta) {
    const item = cart[idx];
    if (!item) return;
    const perBox = item.piecesPerBox || item.moq || 20;
    const boxes = Math.max(1, boxesFromPieces(item.quantity, perBox) + boxDelta);
    item.quantity = boxes * perBox;
    saveCart();
    renderCartItems();
    updateCartBadge();
    refreshOpenDetailBasket();
}

function setCartQty(idx, val) {
    const item = cart[idx];
    if (!item) return;
    const perBox = item.piecesPerBox || item.moq || 20;
    item.quantity = snapToBoxes(val, perBox);
    saveCart();
    renderCartItems();
    updateCartBadge();
    refreshOpenDetailBasket();
}

// ==========================================================================
// Product Detail Modal
// ==========================================================================
function openProductDetail(productId) {
    const p = products.find(x => x.id === productId);
    if (!p) return;

    // Prefer promo example size (e.g. Single) so Trade Sale was/now is obvious.
    let defaultIdx = 0;
    const exampleSize = String(p.promo?.exampleSize || '').toLowerCase();
    if (exampleSize) {
        const found = (p.sizes || []).findIndex((s) =>
            String(s.name || '').toLowerCase().includes(exampleSize)
        );
        if (found >= 0) defaultIdx = found;
    }

    const sizePickerHTML = p.sizes.map((s, i) => {
        const meta = getSizeMeta(p, i);
        const priceLine = meta.wasPrice > meta.price
            ? `<span class="detail-size-price detail-size-price--sale">
                    <span class="price-was">Was £${meta.wasPrice.toFixed(2)}</span>
                    <strong class="price-now">£${meta.price.toFixed(2)}/pc</strong>
                    <span class="price-box-meta">${meta.piecesPerBox}/box</span>
               </span>`
            : `<span class="detail-size-price">£${meta.price.toFixed(2)}/pc · ${meta.piecesPerBox}/box</span>`;
        return `
        <button type="button" class="detail-size-option${i === defaultIdx ? ' active' : ''}"
                data-size-index="${i}" onclick="selectDetailSize(${i}, '${safeProductId(p.id)}')">
            <span class="detail-size-name">${escapeHtml(meta.name)}</span>
            ${priceLine}
        </button>`;
    }).join('');

    const first = getSizeMeta(p, defaultIdx);
    const shortDesc = escapeHtml((p.desc || '').split('.')[0] + '.');
    const topSpecs = (p.highlights || []).slice(0, 3)
        .map((h) => `<span class="spec-badge">${escapeHtml(h)}</span>`)
        .join('');
    const promo = getPromoDisplayPrice(p);
    const promoNote = promo
        ? `<div class="detail-promo-note" role="status">
                <strong>${escapeHtml(promo.badge)}</strong>
                <span>${escapeHtml(promo.headline)} — ${escapeHtml(promo.detail)}. Example: ${escapeHtml(promo.sizeLabel || 'Single')} <span class="price-was">£${promo.was.toFixed(2)}</span> <strong>£${promo.now.toFixed(2)}</strong></span>
           </div>`
        : '';

    modalDetailBody.innerHTML = `
        <div class="detail-gallery detail-gallery--simple">
            ${buildDetailGallery(p)}
            <div id="detail-basket-preview" class="detail-basket-preview" aria-live="polite"></div>
        </div>
        <div class="detail-info">
            <span class="detail-category">${p.category === 'protectors' ? 'Mattress Protector' : 'Pillow'}</span>
            <h2 class="detail-title">${escapeHtml(p.title)}</h2>
            ${promoNote}
            <p class="detail-desc">${shortDesc}</p>
            <div class="product-specs detail-simple-specs">${topSpecs}</div>
            <p class="detail-moq-hint" id="detail-box-hint">
                Full boxes only — this size is <strong>${first.piecesPerBox} pcs / box</strong>
                (order 1, 2, 3… boxes). We do not open boxes.
            </p>

            <div class="detail-purchase-controls">
                <div class="form-group detail-size-group">
                    <label>1. Choose size</label>
                    <div class="detail-size-picker" id="detail-size-picker">
                        ${sizePickerHTML}
                    </div>
                    <input type="hidden" id="detail-size-index" value="${defaultIdx}">
                    <input type="hidden" id="detail-product-id" value="${safeProductId(p.id)}">
                    <input type="hidden" id="detail-box-size" value="${first.piecesPerBox}">
                </div>
                <div class="form-group detail-qty-group">
                    <label for="detail-qty-input">2. Boxes / pieces</label>
                    <div class="qty-selector qty-selector--boxes" style="height:42px">
                        <button class="qty-btn" type="button" onclick="adjustDetailQty(-1)">-1 box</button>
                        <input type="number" id="detail-qty-input" class="qty-input"
                               value="${first.moq}" min="${first.moq}" step="${first.piecesPerBox}"
                               style="height:42px" readonly>
                        <button class="qty-btn" type="button" onclick="adjustDetailQty(1)">+1 box</button>
                    </div>
                    <p class="detail-box-readout" id="detail-box-readout">1 box = ${first.piecesPerBox} pcs</p>
                </div>
            </div>

            <div class="detail-add-actions">
                <button class="btn btn-gold btn-block" type="button" onclick="triggerAddToCart('${safeProductId(p.id)}')">
                    <svg class="ico" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><use href="assets/icons.svg#cart"></use></svg>
                    Add to quote
                </button>
                <button class="btn btn-outline-dark btn-block" type="button" data-view-basket
                        onclick="closeModal(); setCartDrawerOpen(true, 'detail_view_quote')">
                    Review quote (${cart.length || 0})
                </button>
            </div>
        </div>`;

    productDetailModal.classList.add('open');
    document.body.style.overflow = 'hidden';
    renderDetailBasketPreview();
    updateDetailBoxReadout();
}

function selectDetailSize(index, productId) {
    const picker = document.getElementById('detail-size-picker');
    const hidden = document.getElementById('detail-size-index');
    if (!picker || !hidden) return;

    picker.querySelectorAll('.detail-size-option').forEach((btn, i) => {
        btn.classList.toggle('active', i === index);
    });
    hidden.value = String(index);

    const product = products.find((x) => x.id === (productId || document.getElementById('detail-product-id')?.value));
    if (!product) return;
    const meta = getSizeMeta(product, index);
    const boxField = document.getElementById('detail-box-size');
    const qtyInput = document.getElementById('detail-qty-input');
    const hint = document.getElementById('detail-box-hint');
    if (boxField) boxField.value = String(meta.piecesPerBox);
    if (qtyInput) {
        qtyInput.value = String(meta.moq);
        qtyInput.min = String(meta.moq);
        qtyInput.step = String(meta.piecesPerBox);
    }
    if (hint) {
        hint.innerHTML = `Full boxes only — this size is <strong>${meta.piecesPerBox} pcs / box</strong> (order 1, 2, 3… boxes). We do not open boxes.`;
    }
    updateDetailBoxReadout();
}

function updateDetailBoxReadout() {
    const qtyInput = document.getElementById('detail-qty-input');
    const boxField = document.getElementById('detail-box-size');
    const readout = document.getElementById('detail-box-readout');
    if (!qtyInput || !boxField || !readout) return;
    const perBox = parseInt(boxField.value, 10) || 20;
    const pcs = snapToBoxes(qtyInput.value, perBox);
    qtyInput.value = String(pcs);
    const boxes = boxesFromPieces(pcs, perBox);
    readout.textContent = `${boxes} box${boxes === 1 ? '' : 'es'} = ${pcs} pcs (${perBox} pcs per box)`;
}

function adjustDetailQty(boxDelta) {
    const input = document.getElementById('detail-qty-input');
    const boxField = document.getElementById('detail-box-size');
    if (!input) return;
    const perBox = parseInt(boxField?.value, 10) || parseInt(input.step, 10) || 20;
    const boxes = Math.max(1, boxesFromPieces(input.value, perBox) + boxDelta);
    input.value = String(boxes * perBox);
    updateDetailBoxReadout();
}

function triggerAddToCart(productId) {
    const sizeIndex = document.getElementById('detail-size-index');
    const qtyInput   = document.getElementById('detail-qty-input');
    addToCart(productId, parseInt(sizeIndex.value, 10), parseInt(qtyInput.value, 10));
}

function closeModal() {
    productDetailModal.classList.remove('open');
    rfqFormModal.classList.remove('open');
    document.body.style.overflow = '';
}

modalCloseDetail.addEventListener('click', closeModal);
modalCloseRfq.addEventListener('click', closeModal);
window.addEventListener('click', e => {
    if (e.target === productDetailModal || e.target === rfqFormModal) closeModal();
});

// Cart → RFQ flow
proceedQuoteBtn.addEventListener('click', () => {
    // Quote requests are soft: full delivery address is only needed for card payment.
    const customerEmail = getCheckoutEmail();
    const shippingAddress = getCartShippingAddress();
    const addressCheck = validateCartShippingAddress(shippingAddress);

    if (addressCheck.ok || customerEmail) {
        syncCartAddressToRfq(shippingAddress, customerEmail);
    }
    setCartDrawerOpen(false);
    setTimeout(() => {
        rfqFormModal.classList.add('open');
        document.body.style.overflow = 'hidden';
        if (typeof CheckoutTotalsUI !== 'undefined') CheckoutTotalsUI.refresh(cart);
    }, 200);
});

if (stripeCheckoutBtn) {
    stripeCheckoutBtn.addEventListener('click', startStripeCheckout);
}

rfqBackBtn.addEventListener('click', () => {
    rfqFormModal.classList.remove('open');
    document.body.style.overflow = '';
    setTimeout(() => setCartDrawerOpen(true), 200);
});

// ==========================================================================
// Quote / Invoice Generation
// ==========================================================================
rfqForm.addEventListener('submit', e => {
    e.preventDefault();

    // Address is optional for quote requests — sales confirm it before invoicing.
    const addressEl = document.getElementById('rfq-address');
    let address = (addressEl?.value || '').trim();
    if (!address) {
        const cartAddr = getCartShippingAddress();
        address = formatShippingAddressBlock(cartAddr);
        if (addressEl && address) addressEl.value = address;
    }
    if (!address) address = 'To be confirmed with our sales team';

    const details = {
        name:    document.getElementById('rfq-name').value,
        company: document.getElementById('rfq-company').value,
        email:   document.getElementById('rfq-email').value,
        phone:   document.getElementById('rfq-phone').value,
        address,
        shippingRegion: document.getElementById('rfq-shipping-region').value,
        shippingLabel: ShippingLogistics.getRegion(document.getElementById('rfq-shipping-region').value).label,
        notes:   document.getElementById('rfq-notes').value || 'No special notes.',
        website: (document.getElementById('rfq-website')?.value || '').trim(),
    };

    const btnText   = document.getElementById('btn-text');
    const btnLoader = document.getElementById('btn-loader');
    const submitBtn = document.getElementById('rfq-submit-submit-btn');

    btnText.classList.add('hidden');
    btnLoader.classList.remove('hidden');
    submitBtn.disabled = true;

    setTimeout(async () => {
        try {
            if (details.website) {
                // Honeypot filled — pretend success, do not notify or clear cart.
                closeModal();
                alert('Done — your quote request is with our sales team.');
                return;
            }

            const cartSnapshot = cart.map(item => ({ ...item }));
            const result = await RoseEmpireQuotePDF.generate(details, cartSnapshot);
            const pricing = result.pricing.vatAmount != null
                ? result.pricing
                : QuotePricing.calculateFullCheckout(cartSnapshot, details.shippingRegion || 'mainland');

            // Deliver the lead server-side so nothing depends on the buyer's email client.
            const lead = await submitLeadToServer({
                leadType: 'rfq',
                name: details.name,
                company: details.company,
                email: details.email,
                phone: details.phone,
                address: details.address,
                shippingLabel: details.shippingLabel,
                notes: details.notes,
                website: details.website,
                source: 'roseempire.co.uk rfq-form',
                items: cartSnapshot.map(i => ({
                    title: i.title,
                    sizeName: i.sizeName,
                    quantity: i.quantity,
                    unitPrice: i.unitPrice,
                })),
                totals: {
                    totalPacks: pricing.totalPacks,
                    grandTotalIncVat: pricing.grandTotalIncVat,
                },
            });

            if (lead.ok) {
                if (window.RoseEmpireTrack?.contactFormSubmit) {
                    window.RoseEmpireTrack.contactFormSubmit({
                        form_type: 'rfq',
                        source: 'rfq-form',
                        item_count: cartSnapshot.length,
                        total_pieces: cartSnapshot.reduce((a, i) => a + i.quantity, 0),
                        shipping_region: details.shippingRegion,
                    });
                }
                cart = [];
                saveCart();
                updateCartBadge();
                renderCartItems();
                closeModal();
                alert(
                    'Done — your quote request is with our sales team and your PDF quote has been downloaded. ' +
                    'We reply within 1 business day to ' + details.email + '.'
                );
            } else {
                // Keep the cart so nothing is lost; fall back to an email draft.
                prepareQuoteEmail(details, cartSnapshot, pricing);
                closeModal();
                alert(
                    'Your PDF quote has been downloaded. We could not reach our server, so an email draft to ' +
                    'info@roseempire.co.uk will open next — please send it (attach the PDF). Your quote list is kept.'
                );
            }
        } catch (err) {
            console.error(err);
            alert('Could not generate the quote PDF. Please try again or contact us at info@roseempire.co.uk.');
        } finally {
            btnText.classList.remove('hidden');
            btnLoader.classList.add('hidden');
            submitBtn.disabled = false;
        }
    }, 600);
});

function prepareQuoteEmail(client, cartSnapshot, pricing) {
    const vatPricing = pricing.vatAmount != null
        ? pricing
        : QuotePricing.calculateFullCheckout(cartSnapshot, client.shippingRegion || 'mainland');

    let body = `Hello Rose Empire Sales Team,\n\nPlease find my wholesale quote request (PDF attached):\n\n`;
    body += `Name: ${client.name}\nCompany: ${client.company}\nEmail: ${client.email}\nPhone: ${client.phone}\nAddress: ${client.address}\n\nItems Requested:\n`;
    cartSnapshot.forEach(i => {
        const rate = i.unitPrice || 0;
        body += `- ${i.title} (${RoseEmpireQuotePDF.categoryLabel(i.category)} / ${i.sizeName}): ${i.quantity} pieces @ ${QuotePricing.formatGBP(rate)}/piece\n`;
    });
    body += `\nEst. Total Pieces: ${vatPricing.totalPacks}\n`;
    body += `Gross Subtotal (ex VAT): ${QuotePricing.formatGBP(vatPricing.grossSubtotal)}\n`;
    if (vatPricing.hasDiscount) {
        body += `Volume Discount (${vatPricing.discountPercent}%): -${QuotePricing.formatGBP(vatPricing.discountAmount)}\n`;
    }
    body += `UK Shipping: ${client.shippingLabel || vatPricing.regionLabel}\n`;
    body += `Product Subtotal (ex VAT): ${QuotePricing.formatGBP(vatPricing.estimatedSubtotal)}\n`;
    body += `Est. Logistics: ${QuotePricing.formatGBP(vatPricing.logisticsCost)}\n`;
    body += `Net Subtotal (ex VAT): ${QuotePricing.formatGBP(vatPricing.netExVat)}\n`;
    body += `UK VAT (20%): ${QuotePricing.formatGBP(vatPricing.vatAmount)}\n`;
    body += `Estimated Total (inc. VAT): ${QuotePricing.formatGBP(vatPricing.grandTotalIncVat)}\n`;
    if (vatPricing.showPremiumBadge) body += `Premium Volume Discount Applied!\n`;
    body += `Notes: ${client.notes}\n\nThank you,\n${client.name}`;

    const mailtoHref = `mailto:info@roseempire.co.uk?subject=${encodeURIComponent('Wholesale Quote Request – ' + client.company)}&body=${encodeURIComponent(body)}`;
    setTimeout(() => { window.location.href = mailtoHref; }, 900);
}

// ==========================================================================
// Mobile Navigation
// ==========================================================================
const mobileNavToggle = document.getElementById('mobile-nav-toggle');
const navMenuEl         = document.getElementById('nav-menu');

function closeMobileNav() {
    if (!navMenuEl || !mobileNavToggle) return;
    navMenuEl.classList.remove('nav-menu--open');
    mobileNavToggle.setAttribute('aria-expanded', 'false');
    setSvgIcon(mobileNavToggle, 'bars');
}

if (mobileNavToggle && navMenuEl) {
    mobileNavToggle.addEventListener('click', () => {
        const open = navMenuEl.classList.toggle('nav-menu--open');
        mobileNavToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        setSvgIcon(mobileNavToggle, open ? 'xmark' : 'bars');
    });

    navMenuEl.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => closeMobileNav());
    });
}

// ==========================================================================
// Initialise
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const checkoutState = params.get('checkout');
    if (checkoutState === 'success') {
        showCheckoutBanner(
            'success',
            'Stripe payment received. A receipt email is on its way — we will confirm your wholesale order shortly.'
        );
        clearCart();
        const clean = new URL(window.location.href);
        clean.searchParams.delete('checkout');
        window.history.replaceState({}, '', clean.pathname + clean.search + clean.hash);
    } else if (checkoutState === 'cancel') {
        showCheckoutBanner(
            'info',
            'Stripe checkout was cancelled. Your quote list is still available — continue by email or try again.'
        );
        const clean = new URL(window.location.href);
        clean.searchParams.delete('checkout');
        window.history.replaceState({}, '', clean.pathname + clean.search + clean.hash);
    }

    initTheme();
    loadCart();
    updateCartBadge();
    QuoteRequestPricingUI.resetSummary();
    CheckoutTotalsUI.bindShippingSelect(() => CheckoutTotalsUI.refresh(cart));
    renderCartItems();

    // Deep-link straight to a product: /?openProduct=protector-terry&from=hotels
    const openProduct = params.get('openProduct');
    if (openProduct) {
        // Catalog loads async on idle — poll briefly until the product exists.
        let attempts = 0;
        const tryOpen = () => {
            attempts += 1;
            if (products.some(p => p.id === openProduct)) {
                document.getElementById('catalog-section')?.scrollIntoView();
                openProductDetail(openProduct);
                const clean = new URL(window.location.href);
                clean.searchParams.delete('openProduct');
                clean.searchParams.delete('from');
                window.history.replaceState({}, '', clean.pathname + clean.search + clean.hash);
            } else if (attempts < 30) {
                setTimeout(tryOpen, 250);
            }
        };
        setTimeout(tryOpen, 300);
    }

    // Deep-link from sector pages: /?openQuote=1&from=hotels-hero
    const openQuote = params.get('openQuote') === '1' || window.location.hash === '#get-quote';
    if (openQuote) {
        const from = params.get('from') || 'deep_link';
        setTimeout(() => {
            setCartDrawerOpen(true, from);
            const clean = new URL(window.location.href);
            clean.searchParams.delete('openQuote');
            clean.searchParams.delete('from');
            if (clean.hash === '#get-quote') clean.hash = '';
            window.history.replaceState({}, '', clean.pathname + clean.search + clean.hash);
        }, 350);
    }

    const sarahOpenBtn = document.getElementById('sarah-open-btn');
    if (sarahOpenBtn) {
        sarahOpenBtn.addEventListener('click', () => {
            if (window.RoseEmpireSarah?.open) {
                window.RoseEmpireSarah.open();
                return;
            }
            const launcher = document.getElementById('sarah-launcher');
            const panel = document.getElementById('sarah-panel');
            if (launcher) {
                launcher.click();
                return;
            }
            if (panel) {
                panel.classList.toggle('open');
            }
        });
    }

    const startCatalog = () => {
        loadCatalog().finally(() => {
            renderProducts();
        });
    };

    if ('requestIdleCallback' in window) {
        requestIdleCallback(startCatalog, { timeout: 1500 });
    } else {
        setTimeout(startCatalog, 250);
    }

    initTrustVideos();
});

/**
 * Performance-safe trust videos:
 * - poster only until click
 * - preload="none"
 * - sources attached when near viewport (or on click)
 * - no autoplay
 */
function initTrustVideos() {
    const nodes = document.querySelectorAll('[data-video-lazy]');
    if (!nodes.length) return;

    const cfgVideos = (typeof RoseEmpireConfig !== 'undefined' && RoseEmpireConfig.videos) || {};

    const resolveSources = (el) => {
        const key = (el.getAttribute('data-mp4') || '').split('/').pop()?.replace(/\.mp4$/i, '') || '';
        const override = cfgVideos[key] || cfgVideos['warehouse-tour'] || null;
        return {
            mp4: (override && override.mp4) || el.getAttribute('data-mp4') || '',
            webm: (override && override.webm) || el.getAttribute('data-webm') || '',
            poster: (override && override.poster) || el.getAttribute('data-poster') || '',
            posterFallback: el.getAttribute('data-poster-fallback') || '',
        };
    };

    const probeUrl = async (url) => {
        if (!url) return false;
        try {
            const res = await fetch(url, { method: 'HEAD', cache: 'no-cache' });
            return res.ok;
        } catch (_) {
            return false;
        }
    };

    const ensurePoster = async (el, sources) => {
        const img = el.querySelector('.trust-video-poster');
        if (!img) return;
        if (sources.poster && sources.poster !== img.getAttribute('src')) {
            const ok = await probeUrl(sources.poster);
            if (ok) {
                img.src = sources.poster;
                return;
            }
        }
        if (sources.posterFallback && !img.getAttribute('src')) {
            img.src = sources.posterFallback;
        }
    };

    const attachSources = (video, sources) => {
        video.innerHTML = '';
        if (sources.webm) {
            const sWebm = document.createElement('source');
            sWebm.src = sources.webm;
            sWebm.type = 'video/webm';
            video.appendChild(sWebm);
        }
        if (sources.mp4) {
            const sMp4 = document.createElement('source');
            sMp4.src = sources.mp4;
            sMp4.type = 'video/mp4';
            video.appendChild(sMp4);
        }
    };

    const prepareNearViewport = async (el) => {
        if (el.dataset.videoPrepared === '1') return;
        el.dataset.videoPrepared = '1';
        const sources = resolveSources(el);
        await ensurePoster(el, sources);
        const mp4Ok = await probeUrl(sources.mp4);
        if (!mp4Ok && !(sources.mp4 || '').startsWith('http')) {
            el.classList.add('is-unavailable');
            const badge = el.querySelector('.trust-video-play-badge');
            if (badge) badge.textContent = 'Video coming soon';
            const btn = el.querySelector('.trust-video-play');
            if (btn) btn.disabled = true;
            el.dataset.videoMissing = '1';
        }
    };

    const playOnClick = async (el) => {
        if (el.dataset.videoMissing === '1') return;
        const sources = resolveSources(el);
        const frame = el.querySelector('.trust-video-frame');
        if (!frame) return;

        let video = frame.querySelector('video');
        if (!video) {
            video = document.createElement('video');
            video.setAttribute('controls', '');
            video.setAttribute('playsinline', '');
            video.setAttribute('preload', 'none');
            video.setAttribute('controlslist', 'nodownload');
            if (sources.poster) video.setAttribute('poster', sources.poster);
            attachSources(video, sources);
            frame.appendChild(video);
        }

        el.classList.add('is-playing');
        try {
            video.load();
            await video.play();
        } catch (err) {
            console.warn('Video play blocked or failed', err);
        }

        if (typeof trackEvent === 'function') {
            trackEvent('trust_video_play', { title: el.getAttribute('data-title') || 'warehouse-video' });
        } else if (window.dataLayer) {
            window.dataLayer.push({ event: 'trust_video_play', title: el.getAttribute('data-title') || 'warehouse-video' });
        }
    };

    nodes.forEach((el) => {
        const btn = el.querySelector('.trust-video-play');
        if (btn) {
            btn.addEventListener('click', () => {
                playOnClick(el);
            });
        }

        if ('IntersectionObserver' in window) {
            const io = new IntersectionObserver(
                (entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            prepareNearViewport(el);
                            io.disconnect();
                        }
                    });
                },
                { rootMargin: '240px 0px' }
            );
            io.observe(el);
        } else {
            prepareNearViewport(el);
        }
    });
}