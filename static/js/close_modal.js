document.body.addEventListener("htmx:afterRequest", function (e) {
    if (e.detail.xhr.getResponseHeader("HX-Trigger") === "close") {
        const modal = bootstrap.Modal.getInstance(document.getElementById("small_modal"));
        if (modal) modal.hide();
    }
});