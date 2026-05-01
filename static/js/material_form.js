document.addEventListener('DOMContentLoaded', function () {

    var typeOptions = document.querySelectorAll('.type-option');
    var typeRadios = document.querySelectorAll('.type-radio');
    var submitBtn = document.getElementById('submitBtn');

    var fieldUrl = document.getElementById('field-url');
    var fieldContent = document.getElementById('field-content');
    var fieldFile = document.getElementById('field-file');
    var fileTypeHint = document.getElementById('fileTypeHint');
    var typeInfoCard = document.getElementById('typeInfoCard');

    var fileDropZone = document.getElementById('fileDropZone');
    var fileInput = document.getElementById('file');
    var fileNamePreview = document.getElementById('fileNamePreview');
    var fileNameText = document.getElementById('fileNameText');

    var typeInfo = {
        pdf: {
            title: 'PDF File',
            desc: 'Upload a PDF document. Students will be able to view and download it.',
            hint: 'PDF files only (max 20MB)',
            icon: 'fa-file-pdf'
        },
        link: {
            title: 'External Link',
            desc: 'Add a URL to an external resource — a website, article, YouTube video, etc.',
            hint: 'Must start with https://',
            icon: 'fa-link'
        },
        text: {
            title: 'Text Content',
            desc: 'Write lesson notes, explanations or instructions directly as text.',
            hint: 'Supports plain text content.',
            icon: 'fa-file-lines'
        },
        image: {
            title: 'Image',
            desc: 'Upload an image — diagram, chart, photo or illustration.',
            hint: 'JPG, PNG, GIF, WEBP (max 10MB)',
            icon: 'fa-image'
        },
        video: {
            title: 'Video File',
            desc: 'Upload a video lesson. For large files consider using a link instead.',
            hint: 'MP4, MOV, AVI, WEBM (max 100MB)',
            icon: 'fa-circle-play'
        }
    };

    function hideAllTypeFields() {
        if (fieldUrl) fieldUrl.style.display = 'none';
        if (fieldContent) fieldContent.style.display = 'none';
        if (fieldFile) fieldFile.style.display = 'none';
    }

    function showFieldForType(type) {
        hideAllTypeFields();

        if (type === 'link' && fieldUrl) {
            fieldUrl.style.display = 'block';
        } else if (type === 'text' && fieldContent) {
            fieldContent.style.display = 'block';
        } else if ((type === 'pdf' || type === 'image' || type === 'video') && fieldFile) {
            fieldFile.style.display = 'block';
            if (fileTypeHint) {
                fileTypeHint.textContent = typeInfo[type] ? typeInfo[type].hint : 'Select a file';
            }
        }
    }

    function updateTypeInfoCard(type) {
        if (!typeInfoCard) return;
        var info = typeInfo[type];
        if (!info) return;
        typeInfoCard.innerHTML =
            '<p class="side-card-title"><i class="fa-solid ' + info.icon + '"></i> ' + info.title + '</p>' +
            '<p class="text-sm text-muted mt-8">' + info.desc + '</p>' +
            '<p class="text-sm text-muted mt-8"><i class="fa-solid fa-circle-info"></i> ' + info.hint + '</p>';
    }

    function enableSubmit() {
        if (submitBtn) submitBtn.disabled = false;
    }

    if (typeOptions.length > 0) {
        typeOptions.forEach(function (option) {
            option.addEventListener('click', function () {
                typeOptions.forEach(function (o) { o.classList.remove('selected'); });
                this.classList.add('selected');

                var radio = this.querySelector('.type-radio');
                if (radio) radio.checked = true;

                var type = this.getAttribute('data-type');
                showFieldForType(type);
                updateTypeInfoCard(type);
                enableSubmit();
            });
        });
    }

    if (submitBtn && typeOptions.length === 0) {
        submitBtn.disabled = false;
    }

    if (fileDropZone && fileInput) {
        fileDropZone.addEventListener('click', function () {
            fileInput.click();
        });

        fileInput.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                var name = this.files[0].name;
                if (fileNameText) fileNameText.textContent = name;
                if (fileNamePreview) fileNamePreview.style.display = 'block';
                fileDropZone.classList.add('has-file');
            }
        });

        fileDropZone.addEventListener('dragover', function (e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });

        fileDropZone.addEventListener('dragleave', function () {
            this.classList.remove('drag-over');
        });

        fileDropZone.addEventListener('drop', function (e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            var files = e.dataTransfer.files;
            if (files && files[0]) {
                fileInput.files = files;
                var name = files[0].name;
                if (fileNameText) fileNameText.textContent = name;
                if (fileNamePreview) fileNamePreview.style.display = 'block';
                this.classList.add('has-file');
            }
        });
    }

});