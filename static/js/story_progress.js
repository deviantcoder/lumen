document.addEventListener("htmx:afterSwap", function (e) {
    if (e.detail.target.id === "stories_container") {
        initStoryProgress();
    }
});

document.addEventListener("DOMContentLoaded", initStoryProgress);

function initStoryProgress() {
    const progress = document.getElementById("current-progress");
    if (!progress) return;

    progress.style.width = "0%";

    let width = 0;
    const duration = 5000;
    const interval = 50;
    const step = (interval / duration) * 100;

    const timer = setInterval(() => {
        width += step;
        progress.style.width = `${width}%`;

        if (width >= 100) {
            clearInterval(timer);

            const nextBtn = document.getElementById("next-story-btn");
            const closeBtn = document.getElementById("close-btn");

            if (nextBtn) {
                if (nextBtn.hasAttribute("hx-get")) {
                    nextBtn.click();
                }
            } else {
                window.location.href = closeBtn.getAttribute("href");
            }
        }
    }, interval);
}
