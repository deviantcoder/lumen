document.addEventListener("DOMContentLoaded", () => {
    function scrollToBottom(time=0) {
        setTimeout(() => {
            const container = document.getElementById('chat_messages');
            if (container) container.scrollTop = container.scrollHeight;
        }, time);
    }
    scrollToBottom();

    const form = document.getElementById("chat_message_form");
    const input = document.getElementById("chat-input");
    const indicator = document.getElementById("typing_indicator");

    let socket = null;
    let typingTimeout;

    if (!form || !input || !indicator) return;

    form.addEventListener("htmx:wsOpen", () => {
        socket = form["htmx-internal-data"].webSocket;

        socket.addEventListener("message", (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === "typing") {
                    if (data.typing) {
                        indicator.classList.remove("d-none");
                    } else {
                        indicator.classList.add("d-none");
                    }
                    scrollToBottom();
                }
            } catch (e) {
                scrollToBottom();
            }
        });
    });

    input.addEventListener("input", () => {
        if (!socket) return;

        socket.send(JSON.stringify({ type: "typing", typing: true }));

        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            socket.send(JSON.stringify({ type: "typing", typing: false }));
        }, 2000);
    });
});