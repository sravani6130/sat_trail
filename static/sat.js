document.addEventListener("DOMContentLoaded", function () {
    // Variables to store uploaded images
    let uploadedImages = [];

    // File input element
    const fileInput = document.getElementById("fileInput");

    // Uploaded images container
    const uploadedImagesContainer = document.getElementById("uploadedImages");

    // Function to handle image upload
    fileInput.addEventListener("change", function () {
        handleImageUpload();
    });

    // Function to handle image upload
    function handleImageUpload() {
        const files = fileInput.files;

        // Display uploaded images
        for (let i = 0; i < files.length; i++) {
            const img = document.createElement("img");
            img.src = URL.createObjectURL(files[i]);
            uploadedImages.push(img.src);
            uploadedImagesContainer.appendChild(img);
        }
    }

    // Function to navigate to the Video Customization page
    window.goToCustomization = function () {
        document.getElementById("upload").style.display = "none";
        document.getElementById("customize").style.display = "block";
    };

    // Function to navigate to the Preview page
    window.goToPreview = function () {
        document.getElementById("customize").style.display = "none";
        document.getElementById("preview").style.display = "block";
    };

    // Function to navigate to the Output Settings page
    window.goToOutputSettings = function () {
        document.getElementById("preview").style.display = "none";
        document.getElementById("output").style.display = "block";
    };

    // Function to navigate to the User Authentication page
    window.goToAuthentication = function () {
        document.getElementById("output").style.display = "none";
        document.getElementById("auth").style.display = "block";
    };
});
