/* ==========================================================================
   Rose Empire — Quote Request List volume pricing + checkout totals
   ========================================================================== */

const QuotePricing = {
    TIERS: [
        { minPacks: 1, maxPacks: 49, discountPercent: 0, label: 'Standard rate (1–49 pieces)' },
        { minPacks: 50, maxPacks: 199, discountPercent: 10, label: '10% volume discount (50–199 pieces)' },
        { minPacks: 200, maxPacks: Infinity, discountPercent: 20, label: '20% premium volume discount (200+ pieces)', premiumBadge: true }
    ],

    getTotalPacks(cart) {
        return cart.reduce((sum, item) => sum + (parseInt(item.quantity, 10) || 0), 0);
    },

    cartGrossSubtotal(cart) {
        if (!cart || !cart.length) return 0;
        return cart.reduce((sum, item) => {
            const qty = parseInt(item.quantity, 10) || 0;
            const unit = Number(item.unitPrice) || 0;
            return sum + qty * unit;
        }, 0);
    },

    getTier(totalPacks) {
        if (totalPacks >= 200) return this.TIERS[2];
        if (totalPacks >= 50) return this.TIERS[1];
        return this.TIERS[0];
    },

    calculate(cart) {
        const totalPacks = this.getTotalPacks(cart);
        const tier = this.getTier(totalPacks);
        const grossSubtotal = this.cartGrossSubtotal(cart);
        const discountAmount = grossSubtotal * (tier.discountPercent / 100);
        const estimatedSubtotal = grossSubtotal - discountAmount;

        return {
            totalPacks,
            grossSubtotal,
            discountPercent: tier.discountPercent,
            discountAmount,
            estimatedSubtotal,
            tierLabel: tier.label,
            showPremiumBadge: Boolean(tier.premiumBadge),
            hasDiscount: tier.discountPercent > 0
        };
    },

    calculateFullCheckout(cart, shippingRegionId) {
        const product = this.calculate(cart);
        const shipping = ShippingLogistics.calculate(shippingRegionId, product.totalPacks);
        const netExVat = product.estimatedSubtotal + shipping.logisticsCost;
        const vatRate = 0.2;
        const vatAmount = netExVat * vatRate;
        const grandTotalIncVat = netExVat + vatAmount;

        return {
            ...product,
            ...shipping,
            netExVat,
            vatRate,
            vatAmount,
            grandTotalIncVat
        };
    },

    /** @deprecated Use calculateFullCheckout — kept for PDF callers passing shipping separately */
    calculateWithVat(cart, shippingRegionId) {
        return this.calculateFullCheckout(cart, shippingRegionId || 'mainland');
    },

    formatGBP(amount) {
        return `£${Number(amount).toFixed(2)}`;
    },

    lineTotal(quantity, unitPrice) {
        return (parseInt(quantity, 10) || 0) * (Number(unitPrice) || 0);
    }
};

const QuoteRequestPricingUI = (function () {
    let els = null;

    function cacheElements() {
        if (els) return els;
        els = {
            uniqueCount: document.getElementById('summary-unique-count'),
            totalPacks: document.getElementById('summary-total-packs'),
            grossSubtotal: document.getElementById('summary-gross-subtotal'),
            discountRow: document.getElementById('summary-discount-row'),
            discountLabel: document.getElementById('summary-discount-label'),
            discountAmount: document.getElementById('summary-discount-amount'),
            productNet: document.getElementById('summary-product-net'),
            shippingRow: document.getElementById('summary-shipping-row'),
            shippingLabel: document.getElementById('summary-shipping-label'),
            shippingAmount: document.getElementById('summary-shipping-amount'),
            netExVat: document.getElementById('summary-net-ex-vat'),
            vatAmount: document.getElementById('summary-vat-amount'),
            totalPrice: document.getElementById('summary-total-price'),
            volumeBadge: document.getElementById('summary-volume-badge'),
            tierHint: document.getElementById('volume-tier-hint')
        };
        return els;
    }

    function resetSummary() {
        const e = cacheElements();
        if (!e.uniqueCount) return;

        e.uniqueCount.textContent = '0';
        e.totalPacks.textContent = '0';
        if (e.grossSubtotal) e.grossSubtotal.textContent = QuotePricing.formatGBP(0);
        if (e.discountRow) e.discountRow.classList.add('hidden');
        if (e.productNet) e.productNet.textContent = QuotePricing.formatGBP(0);
        if (e.shippingRow) e.shippingRow.classList.add('hidden');
        if (e.netExVat) e.netExVat.textContent = QuotePricing.formatGBP(0);
        if (e.vatAmount) e.vatAmount.textContent = QuotePricing.formatGBP(0);
        e.totalPrice.textContent = QuotePricing.formatGBP(0);
        if (e.volumeBadge) {
            e.volumeBadge.textContent = '';
            e.volumeBadge.classList.add('hidden');
        }
        if (e.tierHint) {
            e.tierHint.textContent = 'Size-specific wholesale rates · 50+ pieces = 10% off · 200+ = 20% off';
        }
    }

    function update(cart, totals) {
        const e = cacheElements();
        if (!e.totalPrice) return;

        if (!cart || cart.length === 0 || !totals) {
            resetSummary();
            return;
        }

        e.uniqueCount.textContent = String(cart.length);
        e.totalPacks.textContent = String(totals.totalPacks);

        if (e.grossSubtotal) {
            e.grossSubtotal.textContent = QuotePricing.formatGBP(totals.grossSubtotal);
        }

        if (e.discountRow) {
            if (totals.hasDiscount) {
                e.discountRow.classList.remove('hidden');
                e.discountLabel.textContent = `Volume discount (${totals.discountPercent}%):`;
                e.discountAmount.textContent = `-${QuotePricing.formatGBP(totals.discountAmount)}`;
            } else {
                e.discountRow.classList.add('hidden');
            }
        }

        if (e.productNet) {
            e.productNet.textContent = QuotePricing.formatGBP(totals.estimatedSubtotal);
        }

        if (e.shippingRow && e.shippingLabel && e.shippingAmount) {
            e.shippingRow.classList.remove('hidden');
            e.shippingLabel.textContent = `Est. Logistics (${totals.regionLabel}):`;
            e.shippingAmount.textContent = QuotePricing.formatGBP(totals.logisticsCost);
        }

        if (e.netExVat) {
            e.netExVat.textContent = QuotePricing.formatGBP(totals.netExVat);
        }
        if (e.vatAmount) {
            e.vatAmount.textContent = QuotePricing.formatGBP(totals.vatAmount);
        }

        e.totalPrice.textContent = QuotePricing.formatGBP(totals.grandTotalIncVat);

        if (e.volumeBadge) {
            if (totals.showPremiumBadge) {
                e.volumeBadge.textContent = 'Premium Volume Discount Applied!';
                e.volumeBadge.classList.remove('hidden');
            } else {
                e.volumeBadge.textContent = '';
                e.volumeBadge.classList.add('hidden');
            }
        }

        if (e.tierHint) {
            if (totals.showPremiumBadge) {
                e.tierHint.textContent = `${totals.tierLabel} · ${totals.breakdown}`;
                e.tierHint.classList.add('tier-hint--premium');
            } else if (totals.hasDiscount) {
                e.tierHint.textContent = totals.tierLabel;
                e.tierHint.classList.remove('tier-hint--premium');
            } else if (totals.totalPacks < 50) {
                const packsToNext = 50 - totals.totalPacks;
                e.tierHint.textContent = `${packsToNext} more piece${packsToNext === 1 ? '' : 's'} to unlock 10% off.`;
                e.tierHint.classList.remove('tier-hint--premium');
            } else {
                e.tierHint.textContent = totals.tierLabel;
                e.tierHint.classList.remove('tier-hint--premium');
            }
        }

        return totals;
    }

    return { update, resetSummary, cacheElements };
})();
