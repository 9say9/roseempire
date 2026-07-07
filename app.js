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

function buildDetailGallery(product) {
    const imgs = (product.gallery && product.gallery.length) ? product.gallery : [product.image];
    const fallback = `https://placehold.co/400x300/0d1f3c/ffffff?text=${encodeURIComponent(product.title)}`;
    return imgs.map((src, i) =>
        `<img src="${src}" alt="${product.title}" class="${i === 0 ? 'detail-gallery-main' : 'detail-gallery-extra'}"
              onerror="this.src='${fallback}'">`
    ).join('');
}


// ==========================================================================
// Application State
// ==========================================================================
let cart = [];
let currentFilter = 'all';
let currentSearch = '';

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
// Theme Setup
// ==========================================================================
function initTheme() {
    const saved = localStorage.getItem('re-theme') || 'light';
    document.body.classList.remove('light-mode', 'dark-mode');
    document.body.classList.add(saved === 'dark' ? 'dark-mode' : 'light-mode');
    themeToggle.querySelector('i').className = saved === 'dark'
        ? 'fa-solid fa-sun'
        : 'fa-solid fa-moon';
}

themeToggle.addEventListener('click', () => {
    const isDark = document.body.classList.contains('dark-mode');
    document.body.classList.toggle('dark-mode', !isDark);
    document.body.classList.toggle('light-mode', isDark);
    themeToggle.querySelector('i').className = isDark
        ? 'fa-solid fa-moon'
        : 'fa-solid fa-sun';
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
                <i class="fa-solid fa-circle-info"></i>
                <h3>No products found</h3>
                <p>Try clearing your search or changing the category filter.</p>
            </div>`;
        return;
    }

    filtered.forEach((product, i) => {
        const card = document.createElement('div');
        card.className = 'product-card animate-in';
        card.style.animationDelay = `${i * 0.06}s`;

        card.innerHTML = `
            <div class="product-image-container">
                <span class="product-tag ${product.tagClass || ''}">${product.tag}</span>
                <img src="${product.image}" alt="${product.title}"
                     onerror="this.src='https://placehold.co/400x300/0d1f3c/ffffff?text=${encodeURIComponent(product.title)}'">
            </div>
            <div class="product-info">
                <h3 class="product-title">${product.title}</h3>
                <p class="product-desc">${product.desc}</p>
                <div class="product-specs">
                    ${product.highlights.slice(0, 3).map(h => `<span class="spec-badge">${h}</span>`).join('')}
                </div>
                <div class="product-pricing-moq">
                    <div class="moq-box-badge"><i class="fa-solid fa-box-open"></i> ${product.boxLabel || product.moq + ' pieces min.'}</div>
                    <div class="product-pricing-row">
                    <div class="pricing-info">
                        <span class="moq-label">Min. Order (MOQ)</span>
                        <span class="price-value">${product.moq} Pieces</span>
                    </div>
                    <div class="pricing-info" style="text-align:right">
                        <span class="moq-label">From</span>
                        <span class="price-value">£${product.basePrice.toFixed(2)}/pc</span>
                    </div>
                    </div>
                </div>
                <div class="product-actions">
                    <button class="btn btn-navy-sm btn-block" onclick="openProductDetail('${product.id}')">
                        <i class="fa-solid fa-magnifying-glass-plus"></i> View Details &amp; Quote
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
function toggleCartDrawer() {
    cartDrawer.classList.toggle('open');
    drawerOverlay.classList.toggle('open');
}

cartToggleBtn.addEventListener('click', toggleCartDrawer);
cartCloseBtn.addEventListener('click', toggleCartDrawer);
drawerOverlay.addEventListener('click', toggleCartDrawer);

function updateCartBadge() {
    const total = cart.reduce((a, i) => a + i.quantity, 0);
    cartBadgeCount.textContent = total;
}

function renderCartItems() {
    if (cart.length === 0) {
        cartDrawerItems.innerHTML = `
            <div class="empty-cart-message">
                <i class="fa-solid fa-folder-open"></i>
                <p>Your Quote Request List is empty.</p>
                <p>Browse our catalog and add products to start compiling your wholesale quote.</p>
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
        const belowMOQ  = item.quantity < item.moq;

        const div = document.createElement('div');
        div.className = 'cart-item';
        div.innerHTML = `
            <button class="cart-item-remove" onclick="removeFromCart(${idx})" aria-label="Remove">
                <i class="fa-solid fa-trash-can"></i>
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
                    <div>MOQ: <strong>${item.moq} pieces min.</strong></div>
                </div>
                <div class="cart-item-controls">
                    <div class="qty-selector">
                        <button class="qty-btn" type="button" onclick="adjustCartQty(${idx}, -10)">-10</button>
                        <input type="number" class="qty-input" value="${item.quantity}" min="1"
                               data-cart-idx="${idx}" aria-label="Piece quantity">
                        <button class="qty-btn" type="button" onclick="adjustCartQty(${idx}, 10)">+10</button>
                    </div>
                    <div class="cart-item-total">${QuotePricing.formatGBP(lineTotal)}</div>
                </div>
                ${belowMOQ ? `
                <div class="moq-warning" style="grid-column:1/-1">
                    <i class="fa-solid fa-circle-exclamation"></i> Below MOQ of ${item.moq} pieces
                </div>` : ''}
            </div>`;
        cartDrawerItems.appendChild(div);

        const qtyInput = div.querySelector('.qty-input');
        qtyInput.addEventListener('input', () => setCartQty(idx, qtyInput.value));
        qtyInput.addEventListener('change', () => setCartQty(idx, qtyInput.value));
    });

    CheckoutTotalsUI.refresh(cart);

    const hasMOQFail = cart.some(i => i.quantity < i.moq);
    proceedQuoteBtn.disabled = hasMOQFail;
    proceedQuoteBtn.textContent = hasMOQFail
        ? 'Resolve MOQ Warnings to Proceed'
        : 'Proceed to Request Quote';
    if (stripeCheckoutBtn) stripeCheckoutBtn.disabled = false;
}

async function startStripeCheckout() {
    if (!cart.length) {
        alert('Add products to your quote list before starting checkout.');
        return;
    }

    const checkoutBase = (window.RoseEmpireConfig && window.RoseEmpireConfig.checkoutApiUrl) || '';
    const checkoutUrl = checkoutBase ? `${checkoutBase.replace(/\/$/, '')}/api/checkout/create` : '/api/checkout/create';
    const shippingSelect = document.getElementById('rfq-shipping-region');
    const shippingRegion = shippingSelect ? shippingSelect.value : 'mainland';
    const emailField = document.getElementById('rfq-email');

    if (stripeCheckoutBtn) {
        stripeCheckoutBtn.disabled = true;
        stripeCheckoutBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Preparing checkout…';
    }

    try {
        const response = await fetch(checkoutUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                items: cart,
                domain: window.location.origin,
                shippingRegion,
                customerEmail: emailField ? emailField.value.trim() : ''
            })
        });
        const data = await response.json();
        if (!response.ok || data.status !== 'success') {
            throw new Error(data.message || 'Stripe checkout is unavailable right now.');
        }
        window.location.href = data.url;
    } catch (err) {
        console.error(err);
        alert(err.message || 'Stripe checkout could not be started. Please try again or contact info@roseempire.co.uk.');
    } finally {
        if (stripeCheckoutBtn) {
            stripeCheckoutBtn.disabled = false;
            stripeCheckoutBtn.innerHTML = '<i class="fa-solid fa-credit-card"></i> Secure Stripe Checkout';
        }
    }
}

function addToCart(productId, sizeIndex, quantity) {
    const product = products.find(p => p.id === productId);
    const size    = product.sizes[sizeIndex];
    const existing= cart.findIndex(i => i.productId === productId && i.sizeName === size.name);

    if (existing > -1) {
        cart[existing].quantity += parseInt(quantity, 10);
        cart[existing].unitPrice = size.price;
    } else {
        cart.push({
            productId: product.id,
            title:     product.title,
            image:     product.image,
            category:  product.category,
            sizeName:  size.name,
            unitPrice: size.price,
            quantity:  parseInt(quantity, 10),
            moq:       product.moq
        });
    }

    updateCartBadge();
    renderCartItems();
    closeModal();
    setTimeout(() => {
        cartDrawer.classList.add('open');
        drawerOverlay.classList.add('open');
    }, 150);
}

function removeFromCart(idx) {
    cart.splice(idx, 1);
    updateCartBadge();
    renderCartItems();
}

function adjustCartQty(idx, amt) {
    cart[idx].quantity = Math.max(1, cart[idx].quantity + amt);
    renderCartItems();
    updateCartBadge();
}

function setCartQty(idx, val) {
    cart[idx].quantity = Math.max(1, parseInt(val) || 1);
    renderCartItems();
    updateCartBadge();
}

// ==========================================================================
// Product Detail Modal
// ==========================================================================
function openProductDetail(productId) {
    const p = products.find(x => x.id === productId);
    if (!p) return;

    const specsHTML = p.specs.map(s =>
        `<li><i class="fa-solid fa-circle-check"></i> ${s}</li>`
    ).join('');

    const sizePickerHTML = p.sizes.map((s, i) => `
        <button type="button" class="detail-size-option${i === 0 ? ' active' : ''}"
                data-size-index="${i}" onclick="selectDetailSize(${i})">
            <span class="detail-size-name">${s.name}</span>
            <span class="detail-size-price">£${s.price.toFixed(2)}/pc</span>
        </button>`).join('');

    // Extra feature section per product type
    let extraHTML = '';
    if (p.id === 'protector-wqmp') {
        extraHTML = `
        <div class="layers-container">
            <h4>WQMP — 3-Layer Construction</h4>
            <div class="layer-list">
                <div class="layer-item"><span class="layer-num">1</span><strong>Quilted Top:</strong> Ultra-soft brushed microfiber surface.</div>
                <div class="layer-item"><span class="layer-num">2</span><strong>Fill:</strong> 150 GSM microfiber padding for comfort.</div>
                <div class="layer-item"><span class="layer-num">3</span><strong>Barrier:</strong> 100% silent waterproof TPU backing.</div>
                <div class="layer-item"><span class="layer-num">4</span><strong>Fit:</strong> Deep elasticated fitted skirt — up to 40cm mattress depth.</div>
            </div>
        </div>`;
    } else if (p.id === 'protector-qmp') {
        extraHTML = `
        <div class="layers-container">
            <h4>QMP — Quilted Construction</h4>
            <div class="layer-list">
                <div class="layer-item"><span class="layer-num">1</span><strong>Top:</strong> Quilted polycotton surface for softness.</div>
                <div class="layer-item"><span class="layer-num">2</span><strong>Fill:</strong> 120 GSM lightweight microfiber padding.</div>
                <div class="layer-item"><span class="layer-num">3</span><strong>Base:</strong> Breathable polycotton backing (non-waterproof).</div>
                <div class="layer-item"><span class="layer-num">4</span><strong>Fit:</strong> Deep elasticated fitted skirt — up to 35cm mattress depth.</div>
            </div>
        </div>`;
    } else if (p.id === 'protector-terry') {
        extraHTML = `
        <div class="layers-container">
            <h4>Terry — 2-Layer Construction</h4>
            <div class="layer-list">
                <div class="layer-item"><span class="layer-num">1</span><strong>Surface:</strong> 100% Cotton Terry loop pile — soft & highly absorbent.</div>
                <div class="layer-item"><span class="layer-num">2</span><strong>Barrier:</strong> 100% Waterproof PU/TPU membrane backing.</div>
                <div class="layer-item"><span class="layer-num">3</span><strong>Fit:</strong> Deep elasticated fitted skirt on every size — up to 35cm depth.</div>
            </div>
        </div>`;
    } else if (p.category === 'pillows') {
        extraHTML = `
        <div class="layers-container">
            <h4>Goose Feather &amp; Duck Down Fill</h4>
            <div class="layer-list">
                <div class="layer-item"><i class="fa-solid fa-feather gold-text"></i> <strong>Goose:</strong> 85% white goose feather, 15% soft goose down.</div>
                <div class="layer-item"><i class="fa-solid fa-feather gold-text"></i> <strong>Duck:</strong> 80% duck feather, 20% soft duck down.</div>
                <div class="layer-item"><i class="fa-solid fa-ruler gold-text"></i> Standard size only (50×75cm) — pair of 2 pillows per piece.</div>
                <div class="layer-item"><i class="fa-solid fa-box-open gold-text"></i> Specify goose or duck fill when requesting your quote.</div>
            </div>
        </div>`;
    }

    modalDetailBody.innerHTML = `
        <div class="detail-gallery">
            ${buildDetailGallery(p)}
        </div>
        <div class="detail-info">
            <span class="detail-category">${p.category === 'protectors' ? 'Mattress Protector' : 'Luxury Pillow'}</span>
            <h2 class="detail-title">${p.title}</h2>
            <p class="detail-desc">${p.desc}</p>

            ${extraHTML}

            <div class="detail-specs-list">
                <h4>Specifications &amp; Features:</h4>
                <ul>${specsHTML}</ul>
            </div>

            <div class="detail-purchase-controls">
                <div class="form-group detail-size-group">
                    <label>Select Size</label>
                    <div class="detail-size-picker" id="detail-size-picker">
                        ${sizePickerHTML}
                    </div>
                    <input type="hidden" id="detail-size-index" value="0">
                    <p class="detail-moq-hint">MOQ <strong>${p.moq} pieces</strong> per size — one full trade box.</p>
                </div>
                <div class="form-group detail-qty-group">
                    <label for="detail-qty-input">Pieces Qty</label>
                    <div class="qty-selector" style="height:42px">
                        <button class="qty-btn" type="button" onclick="adjustDetailQty(-10)">-10</button>
                        <input type="number" id="detail-qty-input" class="qty-input"
                               value="${p.moq}" min="${p.moq}" style="height:42px">
                        <button class="qty-btn" type="button" onclick="adjustDetailQty(10)">+10</button>
                    </div>
                </div>
            </div>

            <div style="margin-top:20px">
                <button class="btn btn-gold btn-block" onclick="triggerAddToCart('${p.id}')">
                    <i class="fa-solid fa-cart-plus"></i> Add to Quote Request
                </button>
            </div>
        </div>`;

    productDetailModal.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function selectDetailSize(index) {
    const picker = document.getElementById('detail-size-picker');
    const hidden = document.getElementById('detail-size-index');
    if (!picker || !hidden) return;

    picker.querySelectorAll('.detail-size-option').forEach((btn, i) => {
        btn.classList.toggle('active', i === index);
    });
    hidden.value = String(index);
}

function adjustDetailQty(amount) {
    const input  = document.getElementById('detail-qty-input');
    const minVal = parseInt(input.getAttribute('min')) || 1;
    input.value  = Math.max(minVal, (parseInt(input.value) || minVal) + amount);
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
    cartDrawer.classList.remove('open');
    drawerOverlay.classList.remove('open');
    setTimeout(() => {
        rfqFormModal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }, 200);
});

if (stripeCheckoutBtn) {
    stripeCheckoutBtn.addEventListener('click', startStripeCheckout);
}

rfqBackBtn.addEventListener('click', () => {
    rfqFormModal.classList.remove('open');
    setTimeout(() => {
        cartDrawer.classList.add('open');
        drawerOverlay.classList.add('open');
    }, 200);
});

// ==========================================================================
// Quote / Invoice Generation
// ==========================================================================
rfqForm.addEventListener('submit', e => {
    e.preventDefault();

    const details = {
        name:    document.getElementById('rfq-name').value,
        company: document.getElementById('rfq-company').value,
        email:   document.getElementById('rfq-email').value,
        phone:   document.getElementById('rfq-phone').value,
        address: document.getElementById('rfq-address').value,
        shippingRegion: document.getElementById('rfq-shipping-region').value,
        shippingLabel: ShippingLogistics.getRegion(document.getElementById('rfq-shipping-region').value).label,
        notes:   document.getElementById('rfq-notes').value || 'No special notes.'
    };

    const btnText   = document.getElementById('btn-text');
    const btnLoader = document.getElementById('btn-loader');
    const submitBtn = document.getElementById('rfq-submit-submit-btn');

    btnText.classList.add('hidden');
    btnLoader.classList.remove('hidden');
    submitBtn.disabled = true;

    setTimeout(() => {
        try {
            const cartSnapshot = cart.map(item => ({ ...item }));
            const result = RoseEmpireQuotePDF.generate(details, cartSnapshot);
            prepareQuoteEmail(details, cartSnapshot, result.pricing);

            cart = [];
            updateCartBadge();
            renderCartItems();
            closeModal();

            alert(
                'Your wholesale quote PDF has been downloaded as "Rose Empire Wholesale Quote.pdf". ' +
                'An email draft to info@roseempire.co.uk will open next — attach the PDF before sending.'
            );
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
    mobileNavToggle.querySelector('i').className = 'fa-solid fa-bars';
}

if (mobileNavToggle && navMenuEl) {
    mobileNavToggle.addEventListener('click', () => {
        const open = navMenuEl.classList.toggle('nav-menu--open');
        mobileNavToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        mobileNavToggle.querySelector('i').className = open
            ? 'fa-solid fa-xmark'
            : 'fa-solid fa-bars';
    });

    navMenuEl.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => closeMobileNav());
    });
}

// ==========================================================================
// Initialise
// ==========================================================================
document.addEventListener('DOMContentLoaded', async () => {
    const checkoutState = new URLSearchParams(window.location.search).get('checkout');
    if (checkoutState === 'success') {
        alert('Stripe checkout completed. Our team will confirm your wholesale order shortly.');
    } else if (checkoutState === 'cancel') {
        alert('Stripe checkout was cancelled. Your quote request list is still available if you want to continue by email.');
    }

    initTheme();
    await loadCatalog();
    renderProducts();
    updateCartBadge();
    QuoteRequestPricingUI.resetSummary();
    CheckoutTotalsUI.bindShippingSelect(() => CheckoutTotalsUI.refresh(cart));
    renderCartItems();
});
