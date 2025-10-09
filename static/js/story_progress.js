document.addEventListener("htmx:afterSwap", function (e) {
    if (e.detail.target.id === "stories_container") {
        initStoryProgress();
    }
});

document.addEventListener("DOMContentLoaded", initStoryProgress);

let currentInterval = null;
let progressPaused = false;
let progressWidth = 0;
const duration = 10000;
const interval = 100;
const step = (interval / duration) * 100;

function initStoryProgress() {
    const progress = document.querySelector(".current-progress");
    if (!progress) return;

    if (currentInterval) {
        clearInterval(currentInterval);
        currentInterval = null;
    }

    progress.style.width = "0%";
    progressWidth = 0;
    progressPaused = false;

    currentInterval = setInterval(() => {
        if (progressPaused) return;

        if (!progress.isConnected) {
            clearInterval(currentInterval);
            currentInterval = null;
            return;
        }

        progressWidth += step;
        progress.style.width = `${progressWidth}%`;

        if (progressWidth >= 100) {
            clearInterval(currentInterval);
            currentInterval = null;

            const nextBtn = document.getElementById("next-story-btn");
            const closeBtn = document.getElementById("close-btn");

            if (nextBtn && nextBtn.hasAttribute("hx-get")) {
                const url = nextBtn.getAttribute("hx-get");
                htmx.ajax("GET", url, {
                    target: "#stories_container",
                    swap: "innerHTML"
                });
            } else if (closeBtn) {
                window.location.href = closeBtn.getAttribute("href");
            }
        }
    }, interval);
    attachModalListeners();
}

function attachModalListeners() {
    const modal = document.getElementById("small_modal");
    if (!modal) return;
    modal.addEventListener("shown.bs.modal", () => {
        progressPaused = true;
    });
    modal.addEventListener("hidden.bs.modal", () => {
        progressPaused = false;
    });
}
