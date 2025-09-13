const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file-input");
const fileList = document.getElementById("file-list");

dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.remove("bg-dark-subtle");
    dropzone.classList.add("bg-secondary");
});

dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("bg-secondary");
    dropzone.classList.add("bg-dark-subtle");
});

dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("bg-dark");

    fileInput.files = e.dataTransfer.files;
    updateFileList();
});

fileInput.addEventListener("change", updateFileList);

function updateFileList() {
    fileList.innerHTML = "";
    const files = fileInput.files;

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const fileDiv = document.createElement("div");
        fileDiv.classList.add("mb-2");

        if (file.type.startsWith("image/")) {
            const img = document.createElement("img");
            img.classList.add("img-thumbnail", "me-2");
            img.style.maxHeight = "100px";
            img.style.maxWidth = "100px";

            const reader = new FileReader();
            reader.onload = (e) => {
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);

            fileDiv.appendChild(img);
        } 
        else if (file.type.startsWith("video/")) {
            const icon = document.createElement("i");
            icon.classList.add("bi", "bi-camera-video", "me-2", "fs-3");
            fileDiv.appendChild(icon);
        } 
        else {
            const icon = document.createElement("i");
            icon.classList.add("bi", "bi-file-earmark", "me-2", "fs-3");
            fileDiv.appendChild(icon);
        }

        const filename = document.createElement("span");
        filename.textContent = file.name;
        fileDiv.appendChild(filename);

        fileList.appendChild(fileDiv);
    }
}