# Fraud Detection Project

## Overview

This project demonstrates an end-to-end **fraud detection** workflow:

1. **Backend (FastAPI + PostgreSQL)**  
   - Dockerized FastAPI app exposing an endpoint (`/analyze-statement`) to receive credit card statements (PDFs or images).  
   - Parses transactions via **pdfplumber** (for PDFs) or **OpenCV + Tesseract** (for images).  
   - Runs a **Machine Learning (RandomForest)** model to predict fraudulent transactions.
   - The model was trained on a credit card transactions dataset of 1.3 million real credit card transactions from kaggle. 
   - Stores transaction records in **PostgreSQL**.  
   - Sends email alerts (via **SendGrid**) if suspicious transactions are found (You should update the .env file with your sendgrid api key, and your from email).

2. **Frontend (React Native)**  
   - Uses the camera or file picker to upload statements from a mobile device.  
   - Displays the results of fraud analysis (flags suspicious transactions).  
   - Lets the user enter a contact email for fraud alerts.

## Features

- **Upload or Capture** a credit card statement (PDF/image).  
- **OCR & Parsing**: Convert PDF or scanned statements into structured data.  
- **Fraud Prediction**: RandomForest model trained with SMOTE for class imbalance.  
- **Database Logging**: Store transactions in PostgreSQL.  
- **Email Alerts**: Automatic email notification for suspicious activity.  
- **User-Friendly UI**: React Native app for capturing or uploading files.

## Prerequisites

1. **Docker & Docker Compose**  
   - [Install Docker](https://docs.docker.com/engine/install/)  
   - [Install Docker Compose](https://docs.docker.com/compose/install/)

2. **Node.js & npm** (or Yarn)  
   - [Install Node.js](https://nodejs.org/) (v14 or newer recommended).  
   - npm is bundled with Node.js. Alternatively, you can install [Yarn](https://yarnpkg.com/).

3. **Expo CLI** (recommended for the easiest React Native experience)  
   - `npm install --global expo-cli`  
   - Or you can rely on local `npx expo` commands instead of installing globally.

4. (Optional) **Android Studio / Xcode**  
   - If you want to run the React Native app on an **Android emulator** or **iOS simulator**, you’ll need the platform tools installed:
     - [Android Studio](https://developer.android.com/studio)
     - [Xcode](https://developer.apple.com/xcode/)

## Getting Started

### 1. Start the Backend with Docker Compose

1. Navigate to `backend`:
   ```bash
   cd backend
   ```
2. Build and launch the containers:
   ```bash
   docker-compose up --build
   ```
   - This command will:
     - Pull the `postgres:15` image.
     - Build the Docker image for FastAPI (including Tesseract, OpenCV, etc.).
     - Launch both **app** and **db** services.
3. Once running, FastAPI is available at `http://localhost:8000`.
4. Access the Swagger UI docs at:
   ```bash
   http://localhost:8000/docs
   ```
   Here you can Test the api.


### 4. Run the Frontend (Expo / React Native)

1. **Install Dependencies**:
   ```bash
   cd ../frontend
   npm install
   ```
   or
   ```bash
   yarn
   ```

2. **Configure the API URL** (in `frontend/utils/api.js`):
   ```js
   const API_BASE = "http://localhost:8000"; // If you're using a simulator on your same machine
   // On a real device, replace 'localhost' with your computer's IP on the same Wi-Fi network.
   ```

3. **Launch the App**:
   - Using **Expo**:
     ```bash
     npx expo start
     ```
     or if you installed Expo CLI globally:
     ```bash
     expo start
     ```
     - This will open **Expo DevTools** in your browser.  
     - Scan the QR code with the **Expo Go** app on your phone, or click “Run on Android device/emulator” or “Run on iOS simulator.”
   - Using **React Native CLI**:
     - For **Android**:
       ```bash
       npx react-native run-android
       ```
     - For **iOS**:
       ```bash
       npx react-native run-ios
       ```

4. **Test** the app by capturing or uploading a PDF/image. You should see the results displayed after analysis.

### 5. Usage

- **Update Contact Email** in the app’s form so you can receive email alerts if any fraud is detected.  
- **Capture or Upload** a credit card statement.  
- **Analyze** transactions.  
- The **Results Screen** shows parsed transactions, their fraud probability, and any flagged items.

### 6. Testing & Verification

- **Backend Only**:  
  - In `backend/app/test.py`, run:
    ```bash
    python test.py
    ```
    It parses a sample PDF, runs predictions, and prints JSON output in the console.

- **End-to-End**:  
  - Use the mobile app to upload the same PDF or an image scan, see if you get a matching JSON response in the logs, and confirm if any email alerts were triggered.
