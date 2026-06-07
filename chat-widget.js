/**
 * Rose Empire — floating chat widget (Alex retail / Sarah wholesale)
 */
(function () {
    'use strict';

    function getChatApiUrl() {
        if (typeof RoseEmpireConfig !== 'undefined' && RoseEmpireConfig.chatApiUrl) {
            return RoseEmpireConfig.chatApiUrl;
        }
        const isLocal =
            location.hostname === 'localhost' || location.hostname === '127.0.0.1';
        return isLocal ? 'http://127.0.0.1:5000/api/chat' : '/api/chat';
    }

    const AGENTS = {
        alex: {
            context: 'alex',
            name: 'Alex',
            role: 'Retail Assistant',
            label: 'Alex (Retail Assistant)',
            greeting:
                "Hi! I'm Alex, your Rose Empire retail assistant. Ask me about mattress protectors, pillows, sizes, materials, or care instructions.",
            placeholder: 'Ask about products, sizes, or care…',
            avatarIcon: 'fa-bag-shopping',
        },
        sarah: {
            context: 'sarah',
            name: 'Sarah',
            role: 'Wholesale Representative',
            label: 'Sarah (Wholesale Representative)',
            greeting:
                "Hello! I'm Sarah, your Rose Empire wholesale representative. I can help with trade pricing, MOQs, and qualifying your bulk order — tell me about your facility and volume needs.",
            placeholder: 'Describe your business and order volume…',
            avatarIcon: 'fa-building',
        },
    };

    const RETAIL_HASHES = ['#catalog-section', '#products', '#retail', '#shop'];
    const WHOLESALE_HASHES = ['#hero', '#manufacturer', '#faq', '#footer', '#wholesale'];

    function detectPageContext() {
        const explicit = document.body.dataset.page;
        if (explicit === 'retail' || explicit === 'alex') return 'alex';
        if (explicit === 'wholesale' || explicit === 'sarah') return 'sarah';

        const path = window.location.pathname.toLowerCase();
        const hash = window.location.hash.toLowerCase();

        if (
            path.includes('/retail') ||
            path.endsWith('retail.html') ||
            path.includes('/shop') ||
            hash.includes('retail') ||
            hash.includes('catalog') ||
            hash.includes('product') ||
            RETAIL_HASHES.some((segment) => hash === segment || hash.startsWith(segment + '-'))
        ) {
            return 'alex';
        }

        if (
            path.includes('/wholesale') ||
            path.endsWith('wholesale.html') ||
            path.includes('/b2b') ||
            hash.includes('wholesale') ||
            WHOLESALE_HASHES.some((segment) => hash === segment)
        ) {
            return 'sarah';
        }

        return path.endsWith('index.html') || path === '/' || path.endsWith('/') ? 'sarah' : 'alex';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatMessage(text) {
        return escapeHtml(text).replace(/\n/g, '<br>');
    }

    class RoseEmpireChat {
        constructor() {
            this.contextKey = detectPageContext();
            this.agent = AGENTS[this.contextKey];
            this.isOpen = false;
            this.isSending = false;
            this.history = [];

            this.buildWidget();
            this.bindEvents();
            this.addBotMessage(this.agent.greeting);
        }

        buildWidget() {
            const root = document.createElement('div');
            root.className = 'chat-widget';
            root.id = 're-chat-widget';
            root.innerHTML = `
                <button type="button" class="chat-widget-toggle" id="chat-toggle" aria-label="Open chat with ${this.agent.label}" aria-expanded="false">
                    <i class="fa-solid fa-comments"></i>
                    <span class="chat-widget-toggle-label">${escapeHtml(this.agent.label)}</span>
                </button>
                <div class="chat-widget-panel" id="chat-panel" role="dialog" aria-label="${this.agent.label}" hidden>
                    <header class="chat-widget-header">
                        <div class="chat-widget-agent">
                            <span class="chat-widget-avatar" aria-hidden="true"><i class="fa-solid ${this.agent.avatarIcon}"></i></span>
                            <div>
                                <strong class="chat-widget-name">${escapeHtml(this.agent.label)}</strong>
                                <span class="chat-widget-role">${escapeHtml(this.agent.role)}</span>
                            </div>
                        </div>
                        <button type="button" class="chat-widget-close" id="chat-close" aria-label="Close chat">
                            <i class="fa-solid fa-xmark"></i>
                        </button>
                    </header>
                    <div class="chat-widget-messages" id="chat-messages" aria-live="polite"></div>
                    <form class="chat-widget-form" id="chat-form">
                        <textarea
                            id="chat-input"
                            class="chat-widget-input"
                            rows="1"
                            placeholder="${escapeHtml(this.agent.placeholder)}"
                            aria-label="Message"
                            maxlength="2000"
                        ></textarea>
                        <button type="submit" class="chat-widget-send" id="chat-send" aria-label="Send message">
                            <i class="fa-solid fa-paper-plane"></i>
                        </button>
                    </form>
                </div>
            `;
            document.body.appendChild(root);

            this.root = root;
            this.toggleBtn = root.querySelector('#chat-toggle');
            this.toggleLabel = root.querySelector('.chat-widget-toggle-label');
            this.panel = root.querySelector('#chat-panel');
            this.messagesEl = root.querySelector('#chat-messages');
            this.form = root.querySelector('#chat-form');
            this.input = root.querySelector('#chat-input');
            this.sendBtn = root.querySelector('#chat-send');
            this.closeBtn = root.querySelector('#chat-close');
            this.nameEl = root.querySelector('.chat-widget-name');
            this.roleEl = root.querySelector('.chat-widget-role');
            this.avatarEl = root.querySelector('.chat-widget-avatar i');
        }

        bindEvents() {
            this.toggleBtn.addEventListener('click', () => this.toggle());
            this.closeBtn.addEventListener('click', () => this.close());
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
            this.input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            window.addEventListener('hashchange', () => {
                const nextContext = detectPageContext();
                if (nextContext !== this.contextKey) {
                    this.switchAgent(nextContext);
                }
            });
        }

        switchAgent(contextKey) {
            this.contextKey = contextKey;
            this.agent = AGENTS[contextKey];
            this.history = [];

            this.toggleBtn.setAttribute('aria-label', `Open chat with ${this.agent.label}`);
            this.toggleLabel.textContent = this.agent.label;
            this.panel.setAttribute('aria-label', this.agent.label);
            this.nameEl.textContent = this.agent.label;
            this.roleEl.textContent = this.agent.role;
            this.avatarEl.className = `fa-solid ${this.agent.avatarIcon}`;
            this.input.placeholder = this.agent.placeholder;

            this.messagesEl.innerHTML = '';
            this.addBotMessage(this.agent.greeting);
        }

        toggle() {
            this.isOpen ? this.close() : this.open();
        }

        open() {
            this.isOpen = true;
            this.panel.hidden = false;
            this.toggleBtn.setAttribute('aria-expanded', 'true');
            this.input.focus();
        }

        close() {
            this.isOpen = false;
            this.panel.hidden = true;
            this.toggleBtn.setAttribute('aria-expanded', 'false');
        }

        scrollToBottom() {
            this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
        }

        appendMessage(role, text, isLoading) {
            const msg = document.createElement('div');
            msg.className = `chat-message chat-message--${role}${isLoading ? ' chat-message--loading' : ''}`;
            msg.innerHTML = isLoading
                ? '<span class="chat-typing"><i></i><i></i><i></i></span>'
                : formatMessage(text);
            this.messagesEl.appendChild(msg);
            this.scrollToBottom();
            return msg;
        }

        addBotMessage(text) {
            this.appendMessage('bot', text, false);
        }

        async sendMessage() {
            const text = this.input.value.trim();
            if (!text || this.isSending) return;

            this.input.value = '';
            this.isSending = true;
            this.sendBtn.disabled = true;
            this.appendMessage('user', text, false);
            const loadingEl = this.appendMessage('bot', '', true);

            const apiUrl = getChatApiUrl();
            if (!apiUrl) {
                loadingEl.classList.remove('chat-message--loading');
                loadingEl.innerHTML = formatMessage(
                    'Chat is not configured on this GitHub Pages preview yet. ' +
                        'Run start_chat_server.bat locally for Alex and Sarah, or deploy the Cloudflare chat worker (see GITHUB_PAGES.md). ' +
                        'Email info@roseempire.co.uk or call +44 7999 988450 for trade quotes.'
                );
                this.isSending = false;
                this.sendBtn.disabled = false;
                return;
            }

            try {
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: text,
                        context: this.agent.context,
                        history: this.history.slice(-10),
                    }),
                });

                const data = await response.json().catch(() => ({}));

                if (!response.ok) {
                    throw new Error(data.error || `Server error (${response.status})`);
                }

                const reply = data.reply || 'Sorry, I could not generate a response.';
                loadingEl.classList.remove('chat-message--loading');
                loadingEl.innerHTML = formatMessage(reply);

                this.history.push({ role: 'user', content: text });
                this.history.push({ role: 'assistant', content: reply });
            } catch (err) {
                loadingEl.classList.remove('chat-message--loading');
                const onLocal =
                    location.hostname === '127.0.0.1' ||
                    location.hostname === 'localhost';
                const onGitHub =
                    location.hostname.endsWith('.github.io') ||
                    location.hostname === 'roseempire.co.uk' ||
                    location.hostname === 'www.roseempire.co.uk';
                const hint = onLocal
                    ? 'Double-click start_chat_server.bat, keep that window open, then open http://127.0.0.1:5000 (not a file:// or GitHub Pages link).'
                    : onGitHub
                      ? 'Live chat needs the Cloudflare worker — run deploy_chat_worker.bat, set cloudflareChatApi in site-config.js, then deploy-github.bat. Email info@roseempire.co.uk for quotes meanwhile.'
                      : 'This live site is static only — the chat API must run on a hosted server. For now, test locally: run start_chat_server.bat and open http://127.0.0.1:5000';
                loadingEl.innerHTML = formatMessage(
                    `Unable to reach the chat server. ${hint} (${err.message})`
                );
            } finally {
                this.isSending = false;
                this.sendBtn.disabled = false;
                this.scrollToBottom();
            }
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => new RoseEmpireChat());
    } else {
        new RoseEmpireChat();
    }
})();
