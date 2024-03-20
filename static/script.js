document.addEventListener("DOMContentLoaded", function () {
  // Variables to store uploaded images
  let uploadedImages = [];

  // File input element
  const fileInput = document.getElementById("fileInput");

  // Uploaded images container
  const uploadedImagesContainer = document.getElementById("uploadedImages");

  // Function to handle image upload
  fileInput.addEventListener("change", function () {
    const files = fileInput.files; // Get the selected files
    // Display uploaded images
    for (let i = 0; i < files.length; i++) {
      const img = document.createElement("img");
      img.src = URL.createObjectURL(files[i]);
      img.classList.add("uploaded-image");

      // Create a delete button for each image
      const deleteBtn = document.createElement("button");
      deleteBtn.textContent = "Delete";

      // Append the image and delete button to the container
      const imageContainer = document.createElement("div");
      imageContainer.classList.add("image-container");
      imageContainer.appendChild(img);
      imageContainer.appendChild(deleteBtn);
      uploadedImagesContainer.appendChild(imageContainer);

      uploadedImages.push({ img, deleteBtn });
    }

    const formData = new FormData(); // Assuming you have a form element with the id 'form'
    for (const file of files) {
      formData.append("images", file);
    }

    // Send the uploaded images to the server using AJAX
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload");
    xhr.send(formData);

    xhr.onload = function () {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        if (response.success) {
          console.log("Images saved successfully");
          // Clear the file input
          fileInput.value = "";
        } else {
          console.log("Error saving images:", response.error);
        }
      } else {
        console.log("Error saving images:", xhr.statusText);
      }
    };
  });

  // Function to delete an image
  function deleteImage(imageContainer) {
    uploadedImages = uploadedImages.filter(
      (item) => item.img !== imageContainer.firstChild
    );
    imageContainer.remove();
    displayUploadedImagesCount();
  }

  function displayUploadedImagesCount() {
    // Update display of uploaded images count
    const countDisplay = document.getElementById("uploadedImagesCount");
    countDisplay.textContent = uploadedImages.length;
  }

  // Event delegation for delete buttons
  uploadedImagesContainer.addEventListener("click", function (event) {
    if (event.target && event.target.nodeName === "BUTTON") {
      const imageContainer = event.target.closest(".image-container");
      if (imageContainer) {
        deleteImage(imageContainer);
      }
    }
  });
});
window.goToHome = function () {
  // Redirect to the customization page
  window.location.href = "index.html";
};
// Function to navigate to the Video Customization page
window.goToCustomization = function () {
  // Redirect to the customization page
  window.location.href = "video_customize.html";
};
window.goToSignIn = function () {
  // Redirect to the customization page
  window.location.href = "signin.html";
};

// Function to navigate to the Preview page
window.goToPreview = function () {
  window.location.href = "preview.html";
};

// Function to navigate to the Output Settings page
window.goToOutputSettings = function () {
  window.location.href = "output.html";
};
window.goToSignUp = function () {
  window.location.href = "signup.html";
};

// Function to navigate to the User Authentication page
window.goToAuthentication = function () {
  document.getElementById("output").style.display = "none";
  document.getElementById("auth").style.display = "block";
};
