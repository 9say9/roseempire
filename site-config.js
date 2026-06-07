/**
 * Rose Empire — site-wide URLs (update LinkedIn URL after creating your company page)
 */
(function () {
    const host = window.location.hostname;
    const isLocal = host === 'localhost' || host === '127.0.0.1';
    const isGitHubPages = host.endsWith('.github.io');

    function chatApiUrl() {
        if (isLocal) return 'http://127.0.0.1:5000/api/chat';
        if (isGitHubPages) {
            // Optional: set after deploying cloudflare/worker (see GITHUB_PAGES.md).
            return window.RoseEmpireChatApi || null;
        }
        return '/api/chat';
    }

    window.RoseEmpireConfig = {
        siteUrl: isGitHubPages
            ? 'https://' + host + window.location.pathname.replace(/\/[^/]*$/, '/')
            : 'https://www.roseempire.co.uk',
        linkedInCompanyUrl: 'https://www.linkedin.com/company/rose-empire-wholesale-home-textiles',
        linkedInPersonalUrl: 'https://www.linkedin.com/in/rose-empire-wholesale',
        email: 'info@roseempire.co.uk',
        phone: '+447999988450',
        phoneDisplay: '+44 7999 988450',
        chatApiUrl: chatApiUrl()
    };
})();
