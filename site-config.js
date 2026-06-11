/**
 * Rose Empire — site-wide URLs (update LinkedIn URL after creating your company page)
 */
(function () {
    const host = window.location.hostname;
    const isLocal = host === 'localhost' || host === '127.0.0.1';
    const isGitHubPreview = host.endsWith('.github.io');
    const isProductionDomain =
        host === 'www.roseempire.co.uk' || host === 'roseempire.co.uk';

    // After `deploy_chat_worker.bat`, set your workers.dev URL here (or leave empty).
    const cloudflareChatApi = 'https://rose-empire-chat.adeelcolchester.workers.dev/api/chat';

    function chatApiUrl() {
        if (isLocal) return 'http://127.0.0.1:5000/api/chat';
        if (cloudflareChatApi) return cloudflareChatApi;
        if (isGitHubPreview || isProductionDomain) return 'https://rose-empire-chat.adeelcolchester.workers.dev/api/chat';
        return '/api/chat';
    }

    window.RoseEmpireConfig = {
        siteUrl: 'https://www.roseempire.co.uk',
        linkedInCompanyUrl: 'https://www.linkedin.com/company/rose-empire-wholesale-home-textiles',
        linkedInPersonalUrl: 'https://www.linkedin.com/in/rose-empire-wholesale',
        email: 'info@roseempire.co.uk',
        phone: '+447999988450',
        phoneDisplay: '+44 7999 988450',
        chatApiUrl: chatApiUrl()
    };
})();
