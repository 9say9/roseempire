/* ==========================================================================
   Rose Empire Catalog Application Logic
   ========================================================================== */

// 1. Product Dataset — 3 Mattress Protectors + 4 Pillow Types (cotton / polyester × goose / duck)
const products = [
    // ---- MATTRESS PROTECTORS ----
    {
        id: 'protector-wqmp',
        title: 'WQMP – Waterproof Quilted Mattress Protector',
        category: 'protectors',
        tag: 'Bestseller',
        tagClass: '',
        image: 'assets/mattress_protector.png',
        desc: 'The ultimate combination of protection and comfort. A soft quilted top layer paired with our 100% waterproof TPU backing that is completely silent. Machine washable and OEKO-TEX certified.',
        specs: [
            'Type: Waterproof Quilted Mattress Protector (WQMP)',
            'Top Layer: Soft quilted microfiber surface (150 GSM)',
            'Backing: 100% Silent Waterproof TPU membrane',
            'Certification: OEKO-TEX Standard 100 Certified',
            'Fit: Deep elasticated skirt – fits up to 40cm mattress depth',
            'Washable: Machine washable at 60°C'
        ],
        moq: 20,
        boxLabel: '1 trade box = 20 pieces',
        basePrice: 6.01,
        sizes: [
            { name: 'Pillow Pair',              price: 5.44 },
            { name: 'Single (90×190cm)',        price: 6.01 },
            { name: '4ft / Small Double (120×190cm)', price: 6.91 },
            { name: 'Double (135×190cm)',       price: 7.25 },
            { name: 'King (150×200cm)',         price: 7.88 },
            { name: 'Super King (180×200cm)',   price: 8.97 }
        ],
        highlights: ['100% Waterproof', 'Quilted Top', 'OEKO-TEX Certified', 'Silent TPU Backing']
    },
    {
        id: 'protector-qmp',
        title: 'QMP – Quilted Mattress Protector',
        category: 'protectors',
        tag: 'Essential',
        tagClass: '',
        image: 'assets/mattress_protector.png',
        desc: 'A premium non-waterproof quilted protector for everyday comfort and hygiene. Breathable polycotton shell with a soft microfiber quilted fill. Ideal for homes and guest houses.',
        specs: [
            'Type: Quilted Mattress Protector (QMP)',
            'Top Layer: Soft quilted polycotton surface',
            'Fill: Lightweight microfiber padding (120 GSM)',
            'Backing: Breathable non-waterproof polycotton base',
            'Hypoallergenic: Dust mite and allergen resistant',
            'Washable: Machine washable at 60°C'
        ],
        moq: 20,
        boxLabel: '1 trade box = 20 pieces',
        basePrice: 5.40,
        sizes: [
            { name: 'Pillow Pair',              price: 4.74 },
            { name: 'Single (90×190cm)',        price: 5.40 },
            { name: '4ft / Small Double (120×190cm)', price: 5.95 },
            { name: 'Double (135×190cm)',       price: 6.19 },
            { name: 'King (150×200cm)',         price: 6.54 },
            { name: 'Super King (180×200cm)',   price: 7.21 }
        ],
        highlights: ['Quilted Surface', 'Breathable', 'Hypoallergenic', 'Polycotton Shell']
    },
    {
        id: 'protector-terry',
        title: 'Terry Waterproof Mattress Protector',
        category: 'protectors',
        tag: 'Hotel Grade',
        tagClass: 'tag-gold',
        image: 'assets/mattress_protector.png',
        desc: 'Classic terry towelling surface with a 100% waterproof backing. Highly absorbent, soft underfoot, and incredibly durable — the preferred choice for hotels and care homes.',
        specs: [
            'Type: Terry Towelling Waterproof Mattress Protector',
            'Surface: 100% Cotton Terry towelling top layer',
            'Backing: 100% Waterproof PU/TPU membrane',
            'Absorbency: High-absorbent cotton loop pile surface',
            'Fit: Elasticated skirt fits mattresses up to 35cm deep',
            'Durability: Industrial-laundry resistant – up to 60°C wash'
        ],
        moq: 20,
        boxLabel: '1 trade box = 20 pieces',
        basePrice: 5.20,
        sizes: [
            { name: 'Pillow Pair',              price: 4.40 },
            { name: 'Cot',                      price: 4.40 },
            { name: 'Single (90×190cm)',        price: 5.20 },
            { name: '4ft / Small Double (120×190cm)', price: 5.60 },
            { name: 'Double (135×190cm)',       price: 5.70 },
            { name: 'King (150×200cm)',         price: 6.30 },
            { name: 'Super King (180×200cm)',   price: 6.85 }
        ],
        highlights: ['Terry Cotton Surface', '100% Waterproof', 'Highly Absorbent', 'Hotel Grade']
    },

    // ---- PILLOWS — Premium cotton shell (higher price) ----
    {
        id: 'pillow-cotton-goose',
        title: 'Cotton Shell · Goose Feather & Down (2-Piece)',
        category: 'pillows',
        pillowGroup: 'cotton',
        shellMaterial: 'cotton',
        fillType: 'goose',
        tag: 'Luxury',
        tagClass: 'tag-gold',
        image: 'assets/down_pillows.png',
        desc: 'Our premium cotton range. Hotel-quality goose feather and down inside a 233-thread-count 100% cotton down-proof cover. Double-needle stitched edges with elegant gold piping.',
        specs: [
            'Sold as: Pair of 2 pillows per piece',
            'Shell: 100% Down-Proof Cotton (233 Thread Count)',
            'Filling: 85% White Goose Feather, 15% Soft Goose Down',
            'Firmness: Medium-firm loft for all sleep positions',
            'Edges: Gold piping with reinforced double stitching',
            'Safety: Sterilised fill – dust-mite and feather-poke resistant'
        ],
        moq: 20,
        boxLabel: '1 trade box = 20 pieces',
        basePrice: 10.50,
        sizes: [
            { name: 'Standard (50×75cm) – 2 Piece',  price: 10.50  },
            { name: 'King Size (50×90cm) – 2 Piece',  price: 13.50 }
        ],
        highlights: ['Cotton Shell', 'Goose Feather & Down', '233TC Cotton', 'Set of 2 Pieces']
    },
    {
        id: 'pillow-cotton-duck',
        title: 'Cotton Shell · Duck Feather & Down (2-Piece)',
        category: 'pillows',
        pillowGroup: 'cotton',
        shellMaterial: 'cotton',
        fillType: 'duck',
        tag: 'Premium',
        tagClass: '',
        image: 'assets/down_pillows.png',
        desc: 'Premium cotton cover with soft duck feather and down filling. The same 233TC down-proof cotton shell as our luxury goose line, with excellent loft at a lower fill cost.',
        specs: [
            'Sold as: Pair of 2 pillows per piece',
            'Shell: 100% Down-Proof Cotton (233 Thread Count)',
            'Filling: 80% Duck Feather, 20% Soft Duck Down',
            'Firmness: Medium loft – suitable for all sleep styles',
            'Hypoallergenic: Fully cleansed filling',
            'Care: Machine washable at 40°C'
        ],
        moq: 20,
        boxLabel: '1 trade box = 20 pieces',
        basePrice: 9.50,
        sizes: [
            { name: 'Standard (50×75cm) – 2 Piece',  price: 9.50  },
            { name: 'King Size (50×90cm) – 2 Piece',  price: 12.00 }
        ],
        highlights: ['Cotton Shell', 'Duck Feather & Down', '233TC Cotton', 'Set of 2 Pieces']
    },

    // ---- PILLOWS — Value polyester shell (lower price) ----
    {
        id: 'pillow-polyester-goose',
        title: 'Polyester Shell · Goose Feather & Down (2-Piece)',
        category: 'pillows',
        pillowGroup: 'polyester',
        shellMaterial: 'polyester',
        fillType: 'goose',
        tag: 'Premium',
        tagClass: '',
        image: 'assets/down_pillows.png',
        desc: 'Trade-value goose feather and down pillows with a smooth down-proof polyester shell. Natural goose loft and support at a lower shell cost — ideal for high-volume hospitality programmes.',
        specs: [
            'Sold as: Pair of 2 pillows per piece',
            'Shell: Soft Down-Proof Polyester Cover',
            'Filling: 85% White Goose Feather, 15% Soft Goose Down',
            'Firmness: Medium-firm loft for all sleep positions',
            'Breathable: Lightweight polyester shell keeps pillow cool',
            'Care: Machine washable at 40°C'
        ],
        moq: 20,
        boxLabel: '1 trade box = 20 pieces',
        basePrice: 9.00,
        sizes: [
            { name: 'Standard (50×75cm) – 2 Piece',  price: 9.00  },
            { name: 'King Size (50×90cm) – 2 Piece',  price: 11.50  }
        ],
        highlights: ['Polyester Shell', 'Goose Feather & Down', 'Trade Value', 'Set of 2 Pieces']
    },
    {
        id: 'pillow-polyester-duck',
        title: 'Polyester Shell · Duck Feather & Down (2-Piece)',
        category: 'pillows',
        pillowGroup: 'polyester',
        shellMaterial: 'polyester',
        fillType: 'duck',
        tag: 'Value',
        tagClass: '',
        image: 'assets/down_pillows.png',
        desc: 'Our best-value pillow line. Soft duck feather and down in a smooth down-proof polyester shell. Great loft and medium firmness for B&Bs, hotels, and budget-conscious retail buyers.',
        specs: [
            'Sold as: Pair of 2 pillows per piece',
            'Shell: Soft Down-Proof Polyester Cover',
            'Filling: 80% Duck Feather, 20% Soft Duck Down',
            'Firmness: Medium loft – suitable for all sleep styles',
            'Hypoallergenic: Fully cleansed filling',
            'Care: Machine washable at 40°C'
        ],
        moq: 20,
        boxLabel: '1 trade box = 20 pieces',
        basePrice: 8.50,
        sizes: [
            { name: 'Standard (50×75cm) – 2 Piece',  price: 8.50  },
            { name: 'King Size (50×90cm) – 2 Piece',  price: 11.00  }
        ],
        highlights: ['Polyester Shell', 'Duck Feather & Down', 'Best Value', 'Set of 2 Pieces']
    }
];

const PILLOW_GROUP_LABELS = {
    cotton: {
        title: 'Premium Cotton Shell Pillows',
        desc: '233-thread-count down-proof cotton cover — our luxury wholesale range'
    },
    polyester: {
        title: 'Value Polyester Shell Pillows',
        desc: 'Down-proof polyester cover — excellent trade value for high-volume orders'
    }
};

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

    let lastPillowGroup = null;

    filtered.forEach((product, i) => {
        if (product.pillowGroup && product.pillowGroup !== lastPillowGroup) {
            lastPillowGroup = product.pillowGroup;
            const group = PILLOW_GROUP_LABELS[product.pillowGroup];
            const header = document.createElement('div');
            header.className = 'catalog-subsection-header animate-in';
            header.style.animationDelay = `${i * 0.06}s`;
            header.innerHTML = `
                <h3>${group.title}</h3>
                <p>${group.desc}</p>`;
            productsGrid.appendChild(header);
        }

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
            </div>
        </div>`;
    } else if (p.id === 'protector-terry') {
        extraHTML = `
        <div class="layers-container">
            <h4>Terry — 2-Layer Construction</h4>
            <div class="layer-list">
                <div class="layer-item"><span class="layer-num">1</span><strong>Surface:</strong> 100% Cotton Terry loop pile — soft & highly absorbent.</div>
                <div class="layer-item"><span class="layer-num">2</span><strong>Barrier:</strong> 100% Waterproof PU/TPU membrane backing.</div>
            </div>
        </div>`;
    } else if (p.category === 'pillows') {
        const shellLabel = p.shellMaterial === 'cotton' ? 'Premium cotton shell' : 'Value polyester shell';
        const fillLabel = p.fillType === 'goose'
            ? '85% White Goose Feather, 15% Soft Goose Down'
            : '80% Duck Feather, 20% Soft Duck Down';
        const shellDetail = p.shellMaterial === 'cotton'
            ? '233TC down-proof cotton — prevents feather poke'
            : 'Breathable down-proof polyester — keeps pillow cool';
        extraHTML = `
        <div class="layers-container">
            <h4>${p.shellMaterial === 'cotton' ? 'Cotton' : 'Polyester'} Shell · ${p.fillType === 'goose' ? 'Goose' : 'Duck'} Fill</h4>
            <div class="layer-list">
                <div class="layer-item"><i class="fa-solid fa-layer-group gold-text"></i> ${shellLabel} — ${shellDetail}.</div>
                <div class="layer-item"><i class="fa-solid fa-feather gold-text"></i> ${fillLabel} for natural loft.</div>
                <div class="layer-item"><i class="fa-solid fa-box-open gold-text"></i> Sold as a pair of 2 pillows per wholesale piece.</div>
            </div>
        </div>`;
    }

    modalDetailBody.innerHTML = `
        <div class="detail-gallery">
            <img src="${p.image}" alt="${p.title}"
                 onerror="this.src='https://placehold.co/400x300/0d1f3c/ffffff?text=${encodeURIComponent(p.title)}'">
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
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    renderProducts();
    updateCartBadge();
    QuoteRequestPricingUI.resetSummary();
    CheckoutTotalsUI.bindShippingSelect(() => CheckoutTotalsUI.refresh(cart));
    renderCartItems();
});
