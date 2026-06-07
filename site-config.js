/**
 * Rose Empire — site-wide URLs (update LinkedIn URL after creating your company page)
 */
(function () {
    const host = window.location.hostname;
    const isLocal = host === 'localhost' || host === '127.0.0.1';

    window.RoseEmpireConfig = {
        siteUrl: 'https://www.roseempire.co.uk',
        linkedInCompanyUrl: 'https://www.linkedin.com/company/rose-empire-wholesale-home-textiles',
        linkedInPersonalUrl: 'https://www.linkedin.com/in/rose-empire-wholesale',
        email: 'info@roseempire.co.uk',
        phone: '+447999988450',
        phoneDisplay: '+44 7999 988450',
        // Local: Flask server. Live (Netlify): same-origin HTTPS function via /api/chat redirect.
        chatApiUrl: isLocal ? 'http://127.0.0.1:5000/api/chat' : '/api/chat'
    };
})();
