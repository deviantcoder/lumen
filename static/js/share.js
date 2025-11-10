function initShareLogic() {
    const container = document.querySelector("#share_container");
    
    if (!container) {
        return;
    }

    let selectedUsers = new Set();
    const hiddenInput = document.getElementById("selected-users");
    const sendBtn = document.getElementById("send-btn");

    container.onclick = (e) => {
        const el = e.target.closest(".select-user");
        if (!el) return;

        const username = el.dataset.username;
        if (selectedUsers.has(username)) {
            selectedUsers.delete(username);
            el.classList.remove("selected");
        } else {
            selectedUsers.add(username);
            el.classList.add("selected");
        }

        hiddenInput.value = [...selectedUsers].join(",");
        sendBtn.disabled = selectedUsers.size === 0;
    };
}

document.addEventListener("DOMContentLoaded", initShareLogic);

document.body.addEventListener("htmx:afterSwap", (e) => {
    if (e.detail.target.querySelector("#share_container")) {
        initShareLogic();
    }
});
