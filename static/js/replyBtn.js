function attachReplyWatcher() {
    const input = document.getElementById("replyInput");
    const button = document.getElementById("replyButton");

    if (!input || !button) return;

    input.addEventListener("input", function() {
        if (input.value.trim().length > 0) {
            button.classList.remove('d-none');
        } else {
            button.classList.add('d-none');
        }
    });
}

document.addEventListener("DOMContentLoaded", attachReplyWatcher);
document.body.addEventListener("htmx:afterSwap", attachReplyWatcher);