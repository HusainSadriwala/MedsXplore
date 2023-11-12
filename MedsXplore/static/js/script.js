const captureButton = document.getElementById('captureButton');
const imageInput = document.getElementById('imageInput');
const capturedImageInput = document.getElementById('capturedImageInput');
const uploadButton = document.getElementById('uploadButton');
const capturedImageContainer = document.getElementById('capturedImageContainer');
const capturedImage = document.getElementById('capturedImage');

captureButton.addEventListener('click', () => {
    imageInput.click();
});

imageInput.addEventListener('change', () => {
    const file = imageInput.files[0];
    if (file) {
        capturedImageContainer.style.display = 'block';
        capturedImage.src = URL.createObjectURL(file);
        capturedImageInput.files = imageInput.files;
        uploadButton.style.display = 'block';
    }
});
