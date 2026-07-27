/* ==========================================================================
   Rose Empire — UK shipping by region (per trade box)
   Mainland £10 · Scotland & Northern Ireland £15
   ========================================================================== */

const ShippingLogistics = {
    PIECES_PER_BOX: 20,
    FEE_PER_BOX_DEFAULT: 10,

    REGIONS: {
        mainland: {
            id: 'mainland',
            label: 'UK Mainland',
            feePerBox: 10
        },
        highlands: {
            id: 'highlands',
            label: 'Scotland',
            feePerBox: 15
        },
        northern_ireland: {
            id: 'northern_ireland',
            label: 'Northern Ireland',
            feePerBox: 15
        }
    },

    getRegion(regionId) {
        return this.REGIONS[regionId] || this.REGIONS.mainland;
    },

    feePerBox(regionId) {
        const region = this.getRegion(regionId);
        return Number(region.feePerBox) || this.FEE_PER_BOX_DEFAULT;
    },

    /** One trade box = 20 pieces. Partial boxes still count as one box for shipping. */
    boxCountFromPieces(totalPacks) {
        const packs = Math.max(0, parseInt(totalPacks, 10) || 0);
        return packs > 0 ? Math.ceil(packs / this.PIECES_PER_BOX) : 0;
    },

    /** Charge per cart line using that line's pieces-per-box (20 / 40 / 5). */
    boxCountFromCart(cart) {
        if (!cart || !cart.length) return 0;
        return cart.reduce((n, item) => {
            const qty = Math.max(0, parseInt(item.quantity, 10) || 0);
            if (qty <= 0) return n;
            const perBox = Math.max(1, parseInt(item.piecesPerBox, 10) || parseInt(item.moq, 10) || 20);
            return n + Math.ceil(qty / perBox);
        }, 0);
    },

    /**
     * Shipping = region fee × trade boxes.
     * Mainland £10 · Scotland & Northern Ireland £15.
     */
    calculate(regionId, totalPacks, cart) {
        const region = this.getRegion(regionId);
        const fee = this.feePerBox(regionId);
        const boxes = cart && cart.length
            ? this.boxCountFromCart(cart)
            : this.boxCountFromPieces(totalPacks);

        if (boxes === 0) {
            return {
                regionId: region.id,
                regionLabel: region.label,
                feePerBox: fee,
                boxCount: 0,
                logisticsCost: 0,
                breakdown: `Add products to calculate shipping (Mainland £10 / Scotland & NI £15 per box).`
            };
        }

        const logisticsCost = boxes * fee;
        const fmt = (n) => `£${Number(n).toFixed(2)}`;
        const breakdown = `${boxes} box${boxes === 1 ? '' : 'es'} × ${fmt(fee)} (${region.label})`;

        return {
            regionId: region.id,
            regionLabel: region.label,
            feePerBox: fee,
            boxCount: boxes,
            logisticsCost,
            breakdown
        };
    }
};

/** Shared checkout totals — cart drawer + RFQ form (before submit). */
const CheckoutTotalsUI = (function () {
    let defaultRegion = 'mainland';

    function getSelectedRegion() {
        const cartSelect = document.getElementById('cart-shipping-region');
        if (cartSelect && cartSelect.value) return cartSelect.value;
        const select = document.getElementById('rfq-shipping-region');
        return select ? select.value : defaultRegion;
    }

    function setSelectedRegion(regionId) {
        defaultRegion = regionId;
        const cartSelect = document.getElementById('cart-shipping-region');
        if (cartSelect) cartSelect.value = regionId;
        const select = document.getElementById('rfq-shipping-region');
        if (select) select.value = regionId;
    }

    function setText(id, text) {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    }

    function toggle(id, show) {
        const el = document.getElementById(id);
        if (el) el.classList.toggle('hidden', !show);
    }

    function refresh(cart) {
        const regionId = getSelectedRegion();
        const empty = !cart || cart.length === 0;

        if (empty) {
            QuoteRequestPricingUI.resetSummary();
            updateCheckoutPanel(null);
            return null;
        }

        const totals = QuotePricing.calculateFullCheckout(cart, regionId);
        QuoteRequestPricingUI.update(cart, totals);

        const hint = document.getElementById('rfq-shipping-hint');
        if (hint) {
            hint.textContent = totals.boxCount > 0
                ? `Shipping: ${totals.breakdown} = ${QuotePricing.formatGBP(totals.logisticsCost)}`
                : 'Mainland £10 / Scotland & Northern Ireland £15 per trade box.';
        }

        updateCheckoutPanel(totals);
        return totals;
    }

    function updateCheckoutPanel(totals) {
        const panel = document.getElementById('checkout-totals-panel');
        if (!panel) return;

        if (!totals) {
            panel.classList.add('checkout-totals-panel--empty');
            setText('checkout-total-packs', '0');
            setText('checkout-gross', QuotePricing.formatGBP(0));
            setText('checkout-product-net', QuotePricing.formatGBP(0));
            setText('checkout-logistics', QuotePricing.formatGBP(0));
            setText('checkout-net-ex-vat', QuotePricing.formatGBP(0));
            setText('checkout-vat', QuotePricing.formatGBP(0));
            setText('checkout-grand-total', QuotePricing.formatGBP(0));
            toggle('checkout-discount-row', false);
            return;
        }

        const fee = totals.feePerBox || ShippingLogistics.feePerBox(totals.regionId);
        panel.classList.remove('checkout-totals-panel--empty');
        setText('checkout-total-packs', String(totals.totalPacks));
        setText('checkout-gross', QuotePricing.formatGBP(totals.grossSubtotal));
        setText('checkout-product-net', QuotePricing.formatGBP(totals.estimatedSubtotal));
        setText(
            'checkout-logistics-label',
            `Shipping (${totals.boxCount} box${totals.boxCount === 1 ? '' : 'es'} × £${fee}):`
        );
        setText('checkout-logistics', QuotePricing.formatGBP(totals.logisticsCost));
        setText('checkout-net-ex-vat', QuotePricing.formatGBP(totals.netExVat));
        setText('checkout-vat', QuotePricing.formatGBP(totals.vatAmount));
        setText('checkout-grand-total', QuotePricing.formatGBP(totals.grandTotalIncVat));

        toggle('checkout-discount-row', totals.hasDiscount);
        if (totals.hasDiscount) {
            setText('checkout-discount-label', `Volume discount (${totals.discountPercent}%):`);
            setText('checkout-discount-amount', `-${QuotePricing.formatGBP(totals.discountAmount)}`);
        }
        toggle('checkout-premium-badge', totals.showPremiumBadge);
    }

    function bindShippingSelect(onRefresh) {
        ['cart-shipping-region', 'rfq-shipping-region'].forEach((id) => {
            const select = document.getElementById(id);
            if (!select || select.dataset.bound === '1') return;
            select.dataset.bound = '1';
            select.addEventListener('change', () => {
                setSelectedRegion(select.value);
                onRefresh();
            });
        });
    }

    return { refresh, bindShippingSelect, getSelectedRegion, setSelectedRegion };
})();
