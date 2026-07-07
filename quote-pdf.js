/* ==========================================================================
   Rose Empire — Pro-Forma Quote PDF (jsPDF)
   ========================================================================== */

const RoseEmpireQuotePDF = {
    FILE_NAME: 'Rose Empire Wholesale Quote.pdf',
    _jspdfLoading: null,
    BRAND: {
        navy: [13, 31, 60],
        gold: [201, 164, 68],
        muted: [90, 106, 133],
        line: [216, 221, 232],
        green: [22, 163, 74]
    },

    categoryLabel(category) {
        if (category === 'protectors') return 'Mattress Protectors';
        if (category === 'pillows') return 'Pillows';
        return 'Wholesale Textiles';
    },

    async ensureJsPdf() {
        if (window.jspdf && window.jspdf.jsPDF) return;
        if (!this._jspdfLoading) {
            this._jspdfLoading = new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.2/jspdf.umd.min.js';
                script.crossOrigin = 'anonymous';
                script.referrerPolicy = 'no-referrer';
                script.onload = () => resolve();
                script.onerror = () => reject(new Error('jsPDF library failed to load.'));
                document.head.appendChild(script);
            });
        }
        return this._jspdfLoading;
    },

    async generate(client, cartItems) {
        await this.ensureJsPdf();
        if (!window.jspdf || !window.jspdf.jsPDF) {
            throw new Error('jsPDF library is not loaded.');
        }
        if (!cartItems || cartItems.length === 0) {
            throw new Error('Quote cart is empty.');
        }

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' });
        const pageW = doc.internal.pageSize.getWidth();
        const pageH = doc.internal.pageSize.getHeight();
        const margin = 14;
        const contentW = pageW - margin * 2;

        const pricing = QuotePricing.calculateFullCheckout(
            cartItems,
            client.shippingRegion || 'mainland'
        );
        const invoiceNum = 'RE-' + Math.floor(100000 + Math.random() * 900000);
        const dateStr = new Date().toLocaleDateString('en-GB', {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });
        const validUntil = new Date();
        validUntil.setDate(validUntil.getDate() + 30);
        const validStr = validUntil.toLocaleDateString('en-GB', {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });

        let y = this._drawHeader(doc, pageW, margin, invoiceNum, dateStr, validStr);
        y = this._drawBuyerBlock(doc, margin, contentW, y, client, pricing);
        y = this._drawItemsTable(doc, margin, contentW, pageW, pageH, y, cartItems);
        y = this._drawTotals(doc, margin, contentW, pageW, y, pricing, client);
        this._drawFooter(doc, pageW, pageH, margin);

        doc.save(this.FILE_NAME);
        return { invoiceNum, pricing };
    },

    _drawHeader(doc, pageW, margin, invoiceNum, dateStr, validStr) {
        const { navy, gold } = this.BRAND;
        doc.setFillColor(...navy);
        doc.rect(0, 0, pageW, 42, 'F');
        doc.setFillColor(...gold);
        doc.rect(0, 42, pageW, 2.5, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(22);
        doc.text('ROSE EMPIRE', margin, 16);
        doc.setFontSize(8);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...gold);
        doc.text('WHOLESALE HOME TEXTILES', margin, 22);

        doc.setTextColor(220, 228, 240);
        doc.setFontSize(8);
        const rightX = pageW - margin;
        doc.text('Unit 4, Manchester Wholesale Centre', rightX, 12, { align: 'right' });
        doc.text('Manchester, United Kingdom', rightX, 17, { align: 'right' });
        doc.text('info@roseempire.co.uk  |  +44 7999 988450', rightX, 22, { align: 'right' });

        let y = 52;
        doc.setTextColor(...navy);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(16);
        doc.text('PRO-FORMA INVOICE', margin, y);
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);
        doc.setTextColor(...this.BRAND.muted);
        doc.text('Rose Empire Wholesale Quote — subject to confirmation', margin, y + 6);

        y += 14;
        doc.setFontSize(9);
        doc.setTextColor(40, 40, 40);
        doc.setFont('helvetica', 'bold');
        doc.text('Quote Reference:', margin, y);
        doc.setFont('helvetica', 'normal');
        doc.text(invoiceNum, margin + 32, y);
        doc.setFont('helvetica', 'bold');
        doc.text('Issue Date:', margin + 95, y);
        doc.setFont('helvetica', 'normal');
        doc.text(dateStr, margin + 115, y);
        y += 5;
        doc.setFont('helvetica', 'bold');
        doc.text('Valid Until:', margin, y);
        doc.setFont('helvetica', 'normal');
        doc.text(validStr, margin + 32, y);

        return y + 10;
    },

    _drawBuyerBlock(doc, margin, contentW, y, client, pricing) {
        const { navy, line } = this.BRAND;
        doc.setFillColor(248, 250, 252);
        doc.setDrawColor(...line);
        doc.roundedRect(margin, y, contentW, 38, 2, 2, 'FD');

        doc.setTextColor(...navy);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(10);
        doc.text('BILL TO — BUSINESS DETAILS', margin + 5, y + 8);

        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);
        doc.setTextColor(50, 50, 50);
        const col2 = margin + contentW / 2;
        let row = y + 15;
        doc.setFont('helvetica', 'bold');
        doc.text('Company:', margin + 5, row);
        doc.setFont('helvetica', 'normal');
        doc.text(doc.splitTextToSize(client.company || '—', contentW / 2 - 22), margin + 24, row);
        row += 5;
        doc.setFont('helvetica', 'bold');
        doc.text('Contact:', margin + 5, row);
        doc.setFont('helvetica', 'normal');
        doc.text(client.name || '—', margin + 24, row);
        row += 5;
        doc.setFont('helvetica', 'bold');
        doc.text('Email:', margin + 5, row);
        doc.setFont('helvetica', 'normal');
        doc.text(client.email || '—', margin + 24, row);

        row = y + 15;
        doc.setFont('helvetica', 'bold');
        doc.text('Phone:', col2, row);
        doc.setFont('helvetica', 'normal');
        doc.text(client.phone || '—', col2 + 18, row);
        row += 5;
        doc.setFont('helvetica', 'bold');
        doc.text('UK Shipping:', col2, row);
        doc.setFont('helvetica', 'normal');
        doc.text(client.shippingLabel || pricing.regionLabel || 'UK Mainland', col2 + 26, row);
        row += 5;
        doc.setFont('helvetica', 'bold');
        doc.text('Delivery:', col2, row);
        doc.setFont('helvetica', 'normal');
        const addrLines = doc.splitTextToSize(client.address || '—', contentW / 2 - 22);
        doc.text(addrLines, col2 + 20, row);

        return y + 48;
    },

    _drawItemsTable(doc, margin, contentW, pageW, pageH, startY, cartItems) {
        const { navy, gold, line, muted } = this.BRAND;
        const col = {
            product: margin + 2,
            category: margin + 72,
            size: margin + 108,
            qty: margin + 145,
            unit: margin + 162,
            line: margin + 178
        };

        let y = startY;
        doc.setFillColor(...navy);
        doc.rect(margin, y, contentW, 8, 'F');
        doc.setTextColor(255, 255, 255);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(7.5);
        doc.text('PRODUCT', col.product, y + 5.5);
        doc.text('CATEGORY', col.category, y + 5.5);
        doc.text('SIZE', col.size, y + 5.5);
        doc.text('QTY', col.qty, y + 5.5);
        doc.text('UNIT', col.unit, y + 5.5);
        doc.text('LINE TOTAL', col.line, y + 5.5, { align: 'right' });
        y += 8;

        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8);

        cartItems.forEach((item, index) => {
            if (y > pageH - 55) {
                doc.addPage();
                y = 20;
            }

            const rowH = 12;
            if (index % 2 === 0) {
                doc.setFillColor(248, 250, 252);
                doc.rect(margin, y, contentW, rowH, 'F');
            }

            doc.setDrawColor(...line);
            doc.setLineWidth(0.1);
            doc.line(margin, y + rowH, margin + contentW, y + rowH);

            doc.setTextColor(30, 30, 30);
            const titleLines = doc.splitTextToSize(item.title, 68);
            doc.text(titleLines.slice(0, 2), col.product, y + 4);

            doc.setTextColor(...muted);
            doc.text(this.categoryLabel(item.category), col.category, y + 4);
            doc.text(doc.splitTextToSize(item.sizeName, 34).slice(0, 1), col.size, y + 4);
            doc.setTextColor(30, 30, 30);
            doc.text(String(item.quantity), col.qty, y + 4);
            const unit = Number(item.unitPrice) || 0;
            doc.text(QuotePricing.formatGBP(unit), col.unit, y + 4);
            doc.setFont('helvetica', 'bold');
            doc.text(QuotePricing.formatGBP(QuotePricing.lineTotal(item.quantity, unit)), col.line, y + 4, {
                align: 'right'
            });
            doc.setFont('helvetica', 'normal');

            y += rowH;
        });

        doc.setDrawColor(...gold);
        doc.setLineWidth(0.4);
        doc.line(margin, y + 2, margin + contentW, y + 2);

        return y + 8;
    },

    _drawTotals(doc, margin, contentW, pageW, y, pricing, client) {
        const { navy, gold, green, muted, line } = this.BRAND;
        const boxW = 88;
        const boxX = pageW - margin - boxW;

        if (y > 240) {
            doc.addPage();
            y = 20;
        }

        doc.setDrawColor(...line);
        doc.setLineWidth(0.2);
        let boxH = 62;
        if (pricing.hasDiscount) boxH += 10;
        doc.roundedRect(boxX, y, boxW, boxH, 2, 2, 'S');

        let ty = y + 8;
        const labelX = boxX + 5;
        const valueX = boxX + boxW - 5;

        const addRow = (label, value, bold, color) => {
            doc.setFont('helvetica', bold ? 'bold' : 'normal');
            doc.setFontSize(8.5);
            doc.setTextColor(...(color || [50, 50, 50]));
            doc.text(label, labelX, ty);
            doc.text(value, valueX, ty, { align: 'right' });
            ty += 6;
        };

        addRow('Gross Subtotal (ex VAT):', QuotePricing.formatGBP(pricing.grossSubtotal), false);

        if (pricing.hasDiscount) {
            doc.setTextColor(...green);
            addRow(
                `Volume Discount (${pricing.discountPercent}%):`,
                '-' + QuotePricing.formatGBP(pricing.discountAmount),
                true,
                green
            );
            if (pricing.showPremiumBadge) {
                doc.setFontSize(6.5);
                doc.text('Premium Volume Discount Applied', labelX, ty);
                ty += 5;
            }
        }

        addRow('Product Subtotal (ex VAT):', QuotePricing.formatGBP(pricing.estimatedSubtotal), false);

        const logisticsLabel = `Logistics (${(pricing.regionLabel || '').slice(0, 28)}):`;
        addRow(logisticsLabel, QuotePricing.formatGBP(pricing.logisticsCost), false);

        addRow('Net Subtotal (ex VAT):', QuotePricing.formatGBP(pricing.netExVat), true, navy);

        doc.setDrawColor(...line);
        doc.line(boxX + 4, ty, boxX + boxW - 4, ty);
        ty += 5;

        doc.setFont('helvetica', 'bold');
        doc.setFontSize(9);
        doc.setTextColor(...navy);
        doc.text('UK VAT (20%):', labelX, ty);
        doc.text(QuotePricing.formatGBP(pricing.vatAmount), valueX, ty, { align: 'right' });
        ty += 7;

        doc.setFillColor(...navy);
        doc.roundedRect(boxX, ty - 2, boxW, 10, 1, 1, 'F');
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(10);
        doc.text('ESTIMATED TOTAL (inc. VAT):', labelX + 2, ty + 5);
        doc.setTextColor(...gold);
        doc.text(QuotePricing.formatGBP(pricing.grandTotalIncVat), valueX - 2, ty + 5, { align: 'right' });

        y = Math.max(y + 58, ty + 18);

        if (client.notes && client.notes !== 'No special notes.') {
            doc.setTextColor(...muted);
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(8);
            doc.text('Buyer Notes:', margin, y);
            doc.setFont('helvetica', 'normal');
            const noteLines = doc.splitTextToSize(client.notes, contentW - 10);
            doc.text(noteLines, margin, y + 5);
            y += 5 + noteLines.length * 4;
        }

        doc.setFontSize(7);
        doc.setTextColor(...muted);
        doc.text(
            'Pro-forma quote. Logistics estimated from UK destination & piece volume. Prices in GBP. VAT at 20%.',
            margin,
            y
        );

        return y;
    },

    _drawFooter(doc, pageW, pageH, margin) {
        const y = pageH - 12;
        doc.setDrawColor(...this.BRAND.line);
        doc.line(margin, y - 4, pageW - margin, y - 4);
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(7);
        doc.setTextColor(...this.BRAND.muted);
        doc.text(
            'Rose Empire Wholesale Home Textiles — Manchester, United Kingdom — www.roseempire.co.uk',
            pageW / 2,
            y,
            { align: 'center' }
        );
    }
};
