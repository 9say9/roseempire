/**
 * Rose Empire — site-wide URLs
 */
(function () {
    // LIVE checkout — do not switch this to localhost; that broke payments before.
    // Local Flask does not need Stripe keys when this worker is used.
    const cloudflareCheckoutApi = 'https://rose-empire-checkout.adeelcolchester.workers.dev';

    window.RoseEmpireConfig = {
        siteUrl: 'https://www.roseempire.co.uk',
        linkedInCompanyUrl: 'https://www.linkedin.com/company/rose-empire-wholesale-home-textiles',
        linkedInPersonalUrl: 'https://www.linkedin.com/in/rose-empire-wholesale',
        email: 'info@roseempire.co.uk',
        phone: '+447999988450',
        phoneDisplay: '+44 7999 988450',
        checkoutApiUrl: cloudflareCheckoutApi,
        sarahApiBase: 'https://rose-empire-sarah.adeelcolchester.workers.dev'
    };
})();
