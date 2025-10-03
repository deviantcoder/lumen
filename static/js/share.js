document.addEventListener("click", (e) => {
    const el = e.target.closest(".select-user");
    if (!el) return;

    const selectedUsers = window.selectedUsers || new Set();
    const hiddenInput = document.getElementById("selected-users");
    const sendBtn = document.getElementById("send-btn");

    const username = el.dataset.username;

    if (selectedUsers.has(username)) {
        selectedUsers.delete(username);
        el.classList.remove("selected");
    } else {
        selectedUsers.add(username);
        el.classList.add("selected");
    }

    hiddenInput.value = Array.from(selectedUsers).join(",");
    sendBtn.disabled = selectedUsers.size === 0;

    window.selectedUsers = selectedUsers;
});