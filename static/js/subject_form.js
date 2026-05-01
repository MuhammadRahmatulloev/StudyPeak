document.addEventListener('DOMContentLoaded', function () {

    var coverDropZone = document.getElementById('coverDropZone');
    var coverInput = document.getElementById('cover');
    var coverPreviewWrap = document.getElementById('coverPreviewWrap');
    var coverPreviewImg = document.getElementById('coverPreviewImg');
    var coverRemoveBtn = document.getElementById('coverRemoveBtn');
    var coverDropInner = document.getElementById('coverDropInner');

    if (!coverDropZone || !coverInput) return;

    coverDropZone.addEventListener('click', function (e) {
        if (e.target === coverRemoveBtn || coverRemoveBtn && coverRemoveBtn.contains(e.target)) return;
        coverInput.click();
    });

    coverInput.addEventListener('change', function () {
        var file = this.files && this.files[0];
        if (!file) return;
        showPreview(file);
    });

    coverDropZone.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.classList.add('drag-over');
    });

    coverDropZone.addEventListener('dragleave', function () {
        this.classList.remove('drag-over');
    });

    coverDropZone.addEventListener('drop', function (e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        var file = e.dataTransfer.files && e.dataTransfer.files[0];
        if (!file) return;
        coverInput.files = e.dataTransfer.files;
        showPreview(file);
    });

    if (coverRemoveBtn) {
        coverRemoveBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            clearPreview();
        });
    }

    function showPreview(file) {
        var reader = new FileReader();
        reader.onload = function (e) {
            if (coverPreviewImg) coverPreviewImg.src = e.target.result;
            if (coverDropInner) coverDropInner.style.display = 'none';
            if (coverPreviewWrap) coverPreviewWrap.style.display = 'block';
            coverDropZone.classList.add('has-file');
        };
        reader.readAsDataURL(file);
    }

    function clearPreview() {
        coverInput.value = '';
        if (coverPreviewImg) coverPreviewImg.src = '';
        if (coverDropInner) coverDropInner.style.display = 'flex';
        if (coverPreviewWrap) coverPreviewWrap.style.display = 'none';
        coverDropZone.classList.remove('has-file');
    }

});