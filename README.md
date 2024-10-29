# Signature Verification System

Welcome to the Signature Verification System! This project uses Flask as the backend framework, HTML/CSS/JavaScript for the frontend, and MongoDB as the database. It enables users to verify the authenticity of a signature by comparing it with stored reference images.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Running the Project](#running-the-project)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

The **Signature Verification System** enables automatic verification of signatures. By uploading a signature image, the system will compare it with a set of pre-stored reference images using model algorithms (like VGG and ResNet) and provide a similarity score. The project aims to assist in validating signature authenticity in a secure, fast, and reliable manner.

---

## Features

- **Signature Upload**: Users can upload a signature image for verification.
- **Model Comparison**: Uses VGG and ResNet models to generate similarity scores.
- **Threshold-Based Results**: Displays results based on user-defined thresholds.
- **MongoDB Integration**: Stores reference images for verification purposes.
- **Real-Time Feedback**: Displays loading status and final verification results dynamically.

---

## Technology Stack

- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript (Bootstrap for UI)
- **Database**: MongoDB
- **APIs**: RESTful APIs to handle image upload, verification, and result generation

---

## Getting Started

### Prerequisites

Ensure you have the following installed:

- **Python** (>= 3.6)
- **MongoDB** (locally or as a service, e.g., MongoDB Atlas)
- **Flask** and other required packages (listed in `requirements.txt`)

### Installation

Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/your-username/signature-verification-system.git
cd signature-verification-system
```

Install the necessary Python packages:

```bash
pip install -r requirements.txt
```

Ensure MongoDB is running on your local machine or connect to your MongoDB Atlas cluster.

---

### Running the Project

1. **Set up Environment Variables**:
   - Create a `.env` file in the project directory.
   - Add the following variables to configure MongoDB, Flask's secret key, and API keys used for uploading and verifying signatures:

     ```plaintext
     MONGO_URI=mongodb://localhost:27017/your_database
     SECRET_KEY=your_secret_key
     UPLOAD_API_KEY=18daa167476e0a371966fa954ef38f79
     API_KEY_VERIFICATION=dc4b3f8464b89175b6a1bae401483fe0
     ```

     - **Note**: The API keys must match the values checked in `static/js/script.js` within the `uploadSignatures()` and `verifySignature()` functions.

2. **Start the Flask Application**:
   - Run the project using:

     ```bash
     py app.py
     ```

---

   The project should now be running at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Usage

1. **Access the Homepage**: Visit `http://127.0.0.1:5000`.
2. **Upload Signature for Verification**: Enter the person’s name, select a threshold, and upload a signature image.
3. **View Results**: After processing, view the results displayed in the modal with similarity scores for both models.

---

## Folder Structure

```
signature-verification-system/
│
├── app.py                 # Main Flask application file
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
└── templates/             # HTML templates
    └── index.html
```

---

## Contributing

1. **Fork the repository**
2. **Clone your fork**: `git clone https://github.com/your-username/signature-verification-system.git`
3. **Create a new branch**: `git checkout -b feature-name`
4. **Commit your changes**: `git commit -m "Add feature"`
5. **Push to the branch**: `git push origin feature-name`
6. **Open a pull request**

All contributions are welcome!

---

## License

This project is licensed under the MIT License. See `LICENSE` for more information.

---

**Thank you for using the Signature Verification System!** For any questions, feel free to contact the project maintainers.
