// ============================================================
// FitZone Gym Assistant - Frontend logic
// ============================================================

(function () {
    'use strict';

    const chatScroll = document.getElementById('chatScroll');
    const chatBox = document.getElementById('chatBox');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const typingIndicator = document.getElementById('typingIndicator');
    const errorBanner = document.getElementById('errorBanner');

    const REQUEST_TIMEOUT_MS = 10000;
    const REDUCED_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    let pending = false;
    let errorTimer = null;

    // ---------- Utilities ----------

    function escapeHtml(text) {
        const el = document.createElement('div');
        el.textContent = text;
        return el.innerHTML;
    }

    /**
     * Lightweight formatting for bot answers:
     *  - **bold** -> <strong>
     *  - |  -> separate structured rows (the FAQ answers use pipes as rows)
     */
    function formatBotAnswer(text) {
        const escaped = escapeHtml(String(text));
        const withBold = escaped.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>');
        const rows = withBold.split('|').map(function (row) {
            return row.trim();
        }).filter(Boolean);

        if (rows.length > 1) {
            return rows.map(function (row) {
                return '<div class="faq-row">' + row + '</div>';
            }).join('');
        }
        return '<div class="faq-row">' + withBold + '</div>';
    }

    function scrollToBottom() {
        chatScroll.scrollTo({
            top: chatScroll.scrollHeight,
            behavior: REDUCED_MOTION ? 'auto' : 'smooth'
        });
    }

    function avatarElement(kind) {
        const avatar = document.createElement('div');
        avatar.className = 'avatar avatar--' + kind;
        avatar.setAttribute('aria-hidden', 'true');
        avatar.textContent = kind === 'bot' ? '🤖' : '🙂';
        return avatar;
    }

    function confidenceLevel(confidence) {
        const score = parseFloat(confidence);
        if (Number.isNaN(score)) {
            return 'mid';
        }
        if (score >= 70) {
            return 'high';
        }
        if (score >= 40) {
            return 'mid';
        }
        return 'low';
    }

    // ---------- Message rendering ----------

    function appendUserMessage(text) {
        const message = document.createElement('div');
        message.className = 'message message--user';

        const body = document.createElement('div');
        body.className = 'message__body';

        const bubble = document.createElement('div');
        bubble.className = 'bubble bubble--user';
        bubble.textContent = text;

        body.appendChild(bubble);
        message.appendChild(body);
        chatBox.appendChild(message);
        scrollToBottom();
    }

    function appendBotMessage(text, data) {
        const message = document.createElement('div');
        message.className = 'message';
        message.appendChild(avatarElement('bot'));

        const body = document.createElement('div');
        body.className = 'message__body';

        let bubbleClass = 'bubble';
        if (data.status === 'error') {
            bubbleClass += ' bubble--error';
        } else if (data.status === 'no_match') {
            bubbleClass += ' bubble--hint';
        }
        const bubble = document.createElement('div');
        bubble.className = bubbleClass;

        const content = document.createElement('div');
        content.className = 'bubble__content';
        content.innerHTML = formatBotAnswer(text);
        bubble.appendChild(content);
        body.appendChild(bubble);

        // Category chip + confidence pill
        if (data.category || data.confidence) {
            const meta = document.createElement('div');
            meta.className = 'msg-meta';

            let categoryLabel = 'General';
            if (data.status === 'no_match') {
                categoryLabel = 'No exact match';
            } else if (data.category && data.category !== 'unknown') {
                categoryLabel = data.category;
            }
            const categoryBadge = document.createElement('span');
            categoryBadge.className = 'badge badge--category';
            categoryBadge.textContent = categoryLabel;
            meta.appendChild(categoryBadge);

            if (data.confidence && data.status === 'success') {
                const pill = document.createElement('span');
                pill.className = 'badge badge--confidence badge--confidence--' +
                    confidenceLevel(data.confidence);
                pill.textContent = data.confidence + ' confident';
                meta.appendChild(pill);
            }

            body.appendChild(meta);
        }

        message.appendChild(body);
        chatBox.appendChild(message);
        scrollToBottom();
    }

    // ---------- Error banner ----------

    function showErrorBanner(message) {
        errorBanner.textContent = message;
        errorBanner.hidden = false;
        clearTimeout(errorTimer);
        errorTimer = setTimeout(function () {
            errorBanner.hidden = true;
        }, 5000);
    }

    // ---------- Pending state ----------

    function setPending(isPending) {
        pending = isPending;
        typingIndicator.hidden = !isPending;
        sendBtn.disabled = isPending;
        userInput.disabled = isPending;
        chatScroll.setAttribute('aria-busy', String(isPending));

        document.querySelectorAll('.chip').forEach(function (chip) {
            chip.disabled = isPending;
        });

        if (isPending) {
            scrollToBottom();
        }
    }

    // ---------- Send flow ----------

    function sendMessage() {
        if (pending) {
            return;
        }

        const message = userInput.value.trim();
        if (!message) {
            userInput.focus();
            return;
        }

        appendUserMessage(message);
        userInput.value = '';
        setPending(true);

        const controller = new AbortController();
        const timeoutId = setTimeout(function () {
            controller.abort();
        }, REQUEST_TIMEOUT_MS);

        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message }),
            signal: controller.signal
        })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.status === 'error') {
                    showErrorBanner(data.answer || 'Something went wrong. Please try again.');
                } else {
                    appendBotMessage(data.answer, data);
                }
            })
            .catch(function (error) {
                const timedOut = error.name === 'AbortError';
                showErrorBanner(timedOut
                    ? 'The response took too long. Please try again.'
                    : 'Could not reach the server. Check your connection and try again.'
                );
            })
            .finally(function () {
                clearTimeout(timeoutId);
                setPending(false);
                userInput.focus();
            });
    }

    // ---------- Welcome message ----------

    function showWelcome() {
        appendBotMessage(
            "👋 Welcome to FitZone Gym Assistant! Ask me about timings, membership plans, " +
            'classes, facilities, trainers and more. Or tap a suggestion below to get started.',
            { status: 'success', category: 'Welcome', confidence: undefined }
        );
    }

    // ---------- Events ----------

    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
            event.preventDefault();
            sendMessage();
        }
    });

    document.querySelectorAll('.chip').forEach(function (chip) {
        chip.addEventListener('click', function () {
            if (pending) {
                return;
            }
            userInput.value = chip.dataset.question;
            sendMessage();
        });
    });

    showWelcome();
    userInput.focus();
})();