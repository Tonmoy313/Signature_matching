document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const referenceImagesInput = document.getElementById('referenceImages');
    const referencePreviewDiv = document.getElementById('referenceImagesPreview');
    const verificationImageInput = document.getElementById('verificationImage');
    const verificationPreviewDiv = document.getElementById('verificationImagePreview');
    const thresholdInput = document.getElementById('threshold');
    const thresholdValue = document.getElementById('thresholdValue');

    // Maximum number of reference images
    const MAX_REFERENCE_IMAGES = 6;

    // Update threshold value display
    thresholdInput.addEventListener('input', function() {
        thresholdValue.textContent = this.value;
    });

    // Handle reference images upload
    referenceImagesInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        
        if (files.length > MAX_REFERENCE_IMAGES) {
            showAlert('Please select a maximum of ' + MAX_REFERENCE_IMAGES + ' images.', 'warning');
            referenceImagesInput.value = '';
            return;
        }

        referencePreviewDiv.innerHTML = ''; // Clear existing previews

        files.forEach((file, index) => {
            if (file.type.startsWith('image/')) {
                const col = document.createElement('div');
                col.className = 'col-md-4';

                const previewContainer = document.createElement('div');
                previewContainer.className = 'position-relative';

                const img = document.createElement('img');
                img.className = 'img-fluid rounded';
                img.style.maxHeight = '200px';
                img.style.width = 'auto';

                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'btn btn-danger btn-sm position-absolute top-0 end-0 m-2';
                deleteBtn.innerHTML = '×';
                deleteBtn.onclick = function() {
                    col.remove();
                    updateFileInput();
                    // Reset file input if all previews are removed
                    if (referencePreviewDiv.children.length === 0) {
                        referenceImagesInput.value = '';
                    }
                };

                // Read and display image
                const reader = new FileReader();
                reader.onload = function(e) {
                    img.src = e.target.result;
                };
                reader.readAsDataURL(file);

                previewContainer.appendChild(img);
                previewContainer.appendChild(deleteBtn);
                col.appendChild(previewContainer);
                referencePreviewDiv.appendChild(col);
            }
        });
        updateFileInput();
    });

    // Handle verification image upload
    verificationImageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        verificationPreviewDiv.innerHTML = ''; // Clear existing preview

        if (file && file.type.startsWith('image/')) {
            const previewContainer = document.createElement('div');
            previewContainer.className = 'position-relative d-inline-block';

            const img = document.createElement('img');
            img.className = 'img-fluid rounded';
            img.style.maxHeight = '200px';
            img.style.width = 'auto';

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-danger  btn-sm position-absolute top-0 end-0 m-2';
            deleteBtn.innerHTML = '×';
            deleteBtn.onclick = function() {
                verificationPreviewDiv.innerHTML = '';
                verificationImageInput.value = '';
            };

            // Read and display image
            const reader = new FileReader();
            reader.onload = function(e) {
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);

            previewContainer.appendChild(img);
            previewContainer.appendChild(deleteBtn);
            verificationPreviewDiv.appendChild(previewContainer);
        }
    });
});

function updateFileInput() {
    const dt = new DataTransfer();
    const fileInput = document.getElementById('referenceImages');
    const container = document.getElementById('referenceImagesPreview');
    
    container.querySelectorAll('img').forEach((img, index) => {
    const file = fileInput.files[index];
    if (file) {
        dt.items.add(file);
    }
    });
    
    fileInput.files = dt.files;
}

function showAlert(message, type = 'danger', containerId = 'alertContainer') {
    const alertContainer = document.getElementById(containerId);
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.role = 'alert';
    alertElement.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    alertContainer.appendChild(alertElement);
  
    setTimeout(() => {
      alertElement.remove();
    }, 5000);
}
  


//Upload signatures
function uploadSignatures() {
    // Clear any existing alerts
    document.getElementById('alertContainer').innerHTML = '';

    // Check if person's name is provided
    const personName = document.getElementById('personName').value.trim();
    if (!personName) {
        showAlert('Please enter a person\'s name.', 'warning');
        return;
    }

    // Check if images are uploaded
    const images = document.getElementById('referenceImages').files;
    if (images.length === 0) {
        showAlert('Please upload some reference images.', 'warning');
        return;
    }

    if (images.length > 6) {
        showAlert('Please upload a maximum of 6 reference images.', 'warning');
        return;
    }

    // Prepare FormData to send to the backend
    const formData = new FormData();
    formData.append('person_name', personName);
    formData.append('type', 'genuine'); // Can adjust based on input
    console.log("NO of images:", images.length)
    for (let i = 0; i < images.length; i++) {
        formData.append('reference_images', images[i]);
        console.log("image",i, "is appeneded")
    }

    // Log the FormData object to the console
    console.log('FormData:', formData);

    // Show the loading modal
    const uploadModal = new bootstrap.Modal(document.getElementById('uploadModal'));
    document.getElementById('uploadLoadingSection').classList.remove('d-none');
    document.getElementById('uploadResultSection').classList.add('d-none');
    uploadModal.show();

    // Make API call
    fetch('/upload', {
        method: 'POST',
        headers: {
            'x-api-key': "18daa167476e0a371966fa954ef38f79" 
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Display success or error messages based on the response
        showUploadResults(data.message ? true : false, data.message || data.error);
    })
    .catch(error => {
        showUploadResults(false, `Error Occured..!!\n error: ${error} \nFailed to upload signatures. Please try again.`);
        console.error('Error:', error);
    });
}

function showUploadResults(isSuccess, message) {
    // Prepare result elements
    const resultIcon = document.getElementById('resultIcon');
    const resultText = document.getElementById('resultText');

    // Set icon and text based on result
    resultIcon.innerHTML = isSuccess 
        ? '<i class="fa fa-check-circle result-icon genuine-text"></i>'
        : '<i class="fa fa-times-circle result-icon forged-text"></i>';

    resultText.textContent = message;
    resultText.className = isSuccess ? 'mb-3 genuine-text' : 'mb-3 forged-text';

    // Hide loading, show results
    document.getElementById('uploadLoadingSection').classList.add('d-none');
    document.getElementById('uploadResultSection').classList.remove('d-none');

    // Clear the form if successful
    if (isSuccess) {
        document.getElementById('personName').value = '';
        document.getElementById('referenceImages').value = '';
        document.getElementById('referenceImagesPreview').innerHTML = '';
        showAlert(message, 'success');
    } else {
        showAlert(message, 'danger');
    }
}

//Verify Signature

function verifySignature() {
  document.getElementById('verifyAlertContainer').innerHTML = '';

  // Get threshold and person name
  const threshold = parseInt(document.getElementById('threshold').value);
  const personName = document.getElementById('personName_v').value; 
  if (!personName) {
    showAlert('Please enter the person\'s name.', 'warning', 'verifyAlertContainer');
    return;
  }
  // Get verification image
  const verificationImage = document.getElementById('verificationImage').files[0];
  if (!verificationImage) {
    showAlert('Please upload a verification image.', 'warning', 'verifyAlertContainer');
    return;
  }


  const formData = new FormData();
  formData.append('person_name', personName);
  formData.append('threshold', threshold);
  formData.append('verification_image', verificationImage);


  const resultModal = new bootstrap.Modal(document.getElementById('resultModal'));
  document.getElementById('loadingSection').classList.remove('d-none');
  document.getElementById('resultSection').classList.add('d-none');
  resultModal.show();

  console.log(formData)

  let currentStep = 0; 
  const loadingTexts = [
    'Connecting to Database...',
    `Retrieving signature records for ${personName}...`,
    'Preparing images for analysis...',
    'Analyzing reference signatures...',
    'Comparing with provided signature...',
    'Generating results...'
  ];

  const loadingInterval = setInterval(() => {
    if (currentStep < loadingTexts.length) {
      document.getElementById('loadingText').textContent = loadingTexts[currentStep];
      currentStep++;
    } else {
      clearInterval(loadingInterval); // Clear the interval when done
    }
  }, 2000);


  fetch('/signature-matching', {
    method: 'POST',
    headers: {
      'x-api-key': "dc4b3f8464b89175b6a1bae401483fe0", 
    },
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      showResults(data);
    })
    .catch(error => {
      console.error('Error:', error);
      showUploadResults(false, `Failed to Verify signatures. Error: ${error}`);
      showAlert('Verification failed. Please try again.', 'danger', 'verifyAlertContainer');
    //   resultModal.hide();
      
    });
}

function showResults(data) {
    const isGenuine = data.vgg.prediction;
    const vggScore = data.vgg.score;
    console.log("the result is :", isGenuine);

    const resultIcon = document.getElementById('resultIcon_v');
    const resultText = document.getElementById('resultText_v');
    const vggScoreProgress = document.getElementById('vggScoreProgress');
    const vggScoreValue = document.getElementById('vggScoreValue');
    // const resnetScoreProgress = document.getElementById('resnetScoreProgress');
    // const resnetScoreValue = document.getElementById('resnetScoreValue');

    resultIcon.innerHTML = isGenuine
        ? '<i class="fas fa-check-circle result-icon genuine-text"></i>'
        : '<i class="fas fa-times-circle result-icon forged-text"></i>';

    resultText.textContent = isGenuine ? 'Signature is Genuine' : 'Signature is Forged';
    resultText.className = isGenuine ? 'mb-3 genuine-text' : 'mb-3 forged-text';
    

    vggScoreProgress.style.width = vggScore + '%';
    vggScoreProgress.className = `progress-bar ${isGenuine ? 'genuine' : 'forged'}`;
    vggScoreValue.textContent = vggScore;

    // Hide loading, show results
    document.getElementById('loadingSection').classList.add('d-none');
    document.getElementById('resultSection').classList.remove('d-none');

    // Show alert with result
    const alertMessage = isGenuine
        ? `Signature verified as genuine with confidence score ${vggScore}% similarity`
        : `Signature detected as forged with confidence score ${vggScore}% similarity`;
    const alertType = isGenuine ? 'success' : 'danger';
    showAlert(alertMessage, alertType, 'verifyAlertContainer');
}

//For 2 model scores
// function showResults(data) {
//     const vggPrediction = data.vgg.prediction;
//     const vggScore = data.vgg.score;
//     const resnetPrediction = data.resnet.prediction;
//     const resnetScore = data.resnet.score;
  
//     const threshold = parseInt(document.getElementById('threshold').value);
//     let resultMessage; // Variable to hold the result message
//     const resultIcon = document.getElementById('resultIcon_v');
//     const resultText = document.getElementById('resultText_v');
//     const vggScoreProgress = document.getElementById('vggScoreProgress');
//     const vggScoreValue = document.getElementById('vggScoreValue');
//     const resnetScoreProgress = document.getElementById('resnetScoreProgress');
//     const resnetScoreValue = document.getElementById('resnetScoreValue');
    
//     // Determine the result based on the scores
//     if (vggScore >= threshold && resnetScore >= threshold) {
//         resultMessage = 'Signature is Genuine';
//         resultIcon.innerHTML = '<i class="fa fa-check-circle result-icon genuine-text"></i>';
//     } else if (vggScore < threshold && resnetScore < threshold) {
//         resultMessage = 'Signature is Forged';
//         resultIcon.innerHTML = '<i class="fa fa-times-circle result-icon forged-text"></i>';
//     } else {
//         resultMessage = "Can't Say";
//         resultIcon.innerHTML = '<i class="far fa-sad-tear result-icon warning-text"></i>'; // Updated icon for uncertainty
//     }
//     // <i class="far fa-sad-tear"></i>
//     // Update the result text
//     resultText.textContent = resultMessage;
//     resultText.className = resultMessage === 'Signature is Genuine' 
//         ? 'mb-3 genuine-text' 
//         : resultMessage === 'Signature is Forged' 
//         ? 'mb-3 forged-text' 
//         : 'mb-3 warning-text'; // Class for warning

//     // Set VGG score progress
//     vggScoreProgress.style.width = vggScore + '%';
//     vggScoreProgress.className = `progress-bar ${vggScore >= threshold ? 'genuine' : 'forged'}`;
//     vggScoreValue.textContent = vggScore;

//     // Set ResNet score progress
//     resnetScoreProgress.style.width = resnetScore + '%';
//     resnetScoreProgress.className = `progress-bar ${resnetScore >= threshold ? 'genuine' : 'forged'}`;
//     resnetScoreValue.textContent = resnetScore;

//     // Hide loading, show results
//     document.getElementById('loadingSection').classList.add('d-none');
//     document.getElementById('resultSection').classList.remove('d-none');

//     // Show alert with result
//     const alertMessage = resultMessage === "Can't determine: one model indicates genuine, the other indicates forged." 
//         ? resultMessage 
//         : `${resultMessage} with ${vggScore}% (VGG) and ${resnetScore}% (ResNet) confidence.`;
//     const alertType = resultMessage === 'Signature is Genuine' ? 'success' : 
//                       resultMessage === 'Signature is Forged' ? 'danger' : 
//                       'warning'; // Alert type for uncertainty
                      
//     showAlert(alertMessage, alertType, 'verifyAlertContainer');
// }
