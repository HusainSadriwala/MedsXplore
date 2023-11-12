const uploadButton = document.getElementById("upload-button");
const uploadedImage = document.getElementById("uploaded-image");

uploadButton.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            uploadedImage.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});

document.addEventListener('DOMContentLoaded', function () {
const thumbnailImages = document.querySelectorAll('.thumbnail');
const enlargedImages = document.querySelectorAll('.enlarged');

thumbnailImages.forEach((thumbnail, index) => {
thumbnail.addEventListener('click', () => {
    enlargedImages[index].style.display = 'block';
});

enlargedImages[index].addEventListener('click', () => {
    enlargedImages[index].style.display = 'none';
});
});
function speakText(text) {
const synth = window.speechSynthesis;
const utterance = new SpeechSynthesisUtterance(text);
synth.speak(utterance);
const detectedLanguage = franc(text);

    // Set the appropriate language for speech synthesis
    if (detectedLanguage === 'eng') {
    utterance.lang = 'en-US'; // English
} else if (detectedLanguage === 'hin') {
    utterance.lang = 'hi-IN'; // Hindi
} else {
    // Set a default language (e.g., English) for other languages
    utterance.lang = 'en-US';
}

// Set the rate (speech speed) to a faster value if necessary
utterance.rate = 1.0; // Adjust as needed

synth.speak(utterance);
}

// Add event listener to all elements with the 'speak-button' class
const speakButtons = document.querySelectorAll('.speak-button');
speakButtons.forEach((button) => {
button.addEventListener('click', function () {
    const textToSpeak = this.getAttribute('data-text');
    speakText(textToSpeak);
});
});


});