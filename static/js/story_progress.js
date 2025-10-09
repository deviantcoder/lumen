document.addEventListener("DOMContentLoaded", function () {
    const progress = document.getElementById("current-progress");
    if (!progress) return;

    let width = 0;
    const duration = 10000;
    const interval = 50;

    const step = (interval / duration) * 100;
    const timer = setInterval(() => {
        width += step;
        progress.style.width = `${width}%`;

        if (width >= 100) {
            clearInterval(timer);
            const nextBtn = document.getElementById("next-story-btn");
            const closeBtn = document.getElementById("close-btn")
            if (nextBtn) {
                window.location.href = nextBtn.getAttribute("href");
            } else {
                window.location.href = closeBtn.getAttribute("href")
            }
        }
    }, interval);
});