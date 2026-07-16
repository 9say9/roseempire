/* ==========================================================================
   Rose Empire — UK logistics estimates by destination & pack volume
   ========================================================================== */

const ShippingLogistics = {
    REGIONS: {
        mainland: {
            id: 'mainland',
            label: 'UK Mainland (Standard Freight)',
            flatUpToPacks: 50,
            flatFee: 15,
            perPackOver: 0.5
        },
        highlands: {
            id: 'highlands',
            label: 'Scottish Highlands (Extended Route)',
            flatUpToPacks: 50,
            flatFee: 28,
            perPackOver: 0.85
        },
        northern_ireland: {
            id: 'northern_ireland',
            label: 'Northern Ireland (Sea Freight)',
            flatUpToPacks: 50,
            flatFee: 55,
            perPackOver: 1.2
        }
    },

    getRegion(regionId) {
        return this.REGIONS[regionId] || this.REGIONS.mainland;
    },

    /**
     * Flat fee up to N packs, then per-pack surcharge (e.g. Mainland £15 ≤50 packs, +£0.50/pack after).
     */
    calculate(regionId, totalPacks) {
        const region = this.getRegion(regionId);
        const packs = Math.max(0, parseInt(totalPacks, 10) || 0);

        if (packs === 0) {
            return {
                regionId: region.id,
                regionLabel: region.label,
                logisticsCost: 0,
                breakdown: 'Select products to estimate freight.'
            };
        }

        let logisticsCost = region.flatFee;
        const fmt = (n) => `£${Number(n).toFixed(2)}`;
        let breakdown = `${fmt(region.flatFee)} base (up to ${region.flatUpToPacks} pieces)`;

        if (packs > region.flatUpToPacks) {
            const extraPacks = packs - region.flatUpToPacks;
            const surcharge = extraPacks * region.perPackOver;
            logisticsCost += surcharge;
            breakdown += ` + ${extraPacks} × ${fmt(region.perPackOver)}/piece`;
        }

        return {
            regionId: region.id,
            regionLabel: region.label,
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
            hint.textContent = totals.totalPacks > 0
                ? `Freight estimate: ${totals.breakdown} → ${QuotePricing.formatGBP(totals.logisticsCost)}`
                : '';
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

        panel.classList.remove('checkout-totals-panel--empty');
        setText('checkout-total-packs', String(totals.totalPacks));
        setText('checkout-gross', QuotePricing.formatGBP(totals.grossSubtotal));
        setText('checkout-product-net', QuotePricing.formatGBP(totals.estimatedSubtotal));
        setText('checkout-logistics-label', `Logistics (${totals.regionLabel}):`);
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
