# 🌱 AgriGPT AI – Smart Agriculture Assistant

## 📌 Project Overview

AgriGPT AI is an AI-based agriculture assistant designed to help farmers get information about crops, farming practices, crop diseases, common agricultural problems, and crop recommendations.

The system provides agriculture-related answers through a knowledge base and supports crop recommendations using a Machine Learning model. It also includes Tamil language response support to make agricultural information more accessible to Tamil-speaking farmers.

## 🎯 Objectives

* Provide useful agricultural information to farmers.
* Answer common questions related to crops and farming.
* Recommend suitable crops based on input parameters.
* Support Tamil responses for better accessibility.
* Integrate a Machine Learning model with a Flask backend.
* Provide API endpoints for frontend integration.

## 🛠️ Technologies Used

* **Programming Language:** Python
* **Backend Framework:** Flask
* **API Support:** Flask-CORS
* **Machine Learning:** Scikit-learn
* **Model Loading:** Joblib
* **Language Translation:** Deep Translator
* **Version Control:** Git and GitHub

## 📂 Project Structure

```text
AgriGPT-AI/
│
├── app.py
├── knowledge.py
├── crop_recommendation.py
├── train_model.py
├── crop_model.pkl
├── requirements.txt
└── .gitignore
```

## ⚙️ Main Components

### 1. app.py – Flask Backend

* Creates the Flask application.
* Handles API requests from the frontend.
* Provides endpoints for agricultural questions and crop recommendations.
* Integrates the agriculture knowledge base.
* Loads the trained Machine Learning model.
* Supports Tamil response translation.
* Enables cross-origin requests using Flask-CORS.

### 2. knowledge.py – Agriculture Knowledge Base

* Stores agriculture-related information and question-answer content.
* Covers crops such as rice, maize, wheat, sugarcane, cotton, groundnut, tomato, potato, onion, chilli, brinjal, and banana.
* Includes general farming practices and common crop problems.
* Helps retrieve relevant information for farmers' questions.

### 3. crop_recommendation.py – Crop Recommendation

* Contains the crop recommendation functionality.
* Processes the required input parameters.
* Helps identify a suitable crop based on the recommendation logic and model integration.

### 4. train_model.py – Model Training

* Contains the code used to train the crop recommendation Machine Learning model.
* Produces the trained model file used by the application.

### 5. crop_model.pkl – Trained Model

* Stores the trained Machine Learning model.
* Is loaded by the backend to generate crop recommendations.

### 6. requirements.txt – Dependencies

Lists the Python packages required to install and run the backend.

### 7. .gitignore – Git Configuration

Prevents unnecessary files, such as virtual environments, Python cache files, and environment files, from being tracked by Git.

## ✨ Key Features

* Agriculture question-answering system.
* Crop information and farming guidance.
* Crop recommendation using Machine Learning.
* Tamil-language response support.
* Flask REST API endpoints.
* Frontend integration support.
* Organized agriculture knowledge base.

## 🔄 Recent Development Updates

The following development work was completed during the recent project updates:

1. Organized the AgriGPT AI backend files.
2. Updated `app.py` to handle agricultural queries and crop recommendation API requests.
3. Integrated the agriculture knowledge base through `knowledge.py`.
4. Worked on the crop recommendation logic in `crop_recommendation.py`.
5. Integrated the trained crop model stored in `crop_model.pkl`.
6. Added Tamil translation support for crop recommendation responses.
7. Updated `requirements.txt` with the dependencies needed for the application and deployment.
8. Created a Git repository and uploaded the backend source code to GitHub.
9. Updated the GitHub repository with the latest dependency changes.

## 🚀 Installation and Setup

### Prerequisites

* Python installed on your system.
* Git installed on your system.
* Visual Studio Code or another Python editor.

### Step 1: Clone the Repository

```bash
git clone https://github.com/klingapabitha2006-hue/AgriGPT-AI.git
```

### Step 2: Open the Project

```bash
cd AgriGPT-AI
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

The Flask backend will start according to the host and port configured in `app.py`.

## 🔌 API Endpoints

| Endpoint                      | Method | Purpose                                              |
| ----------------------------- | ------ | ---------------------------------------------------- |
| `/`                           | GET    | Check the application root                           |
| `/api/status`                 | GET    | Check backend status                                 |
| `/api/ask`                    | POST   | Submit an agriculture-related question               |
| `/api/crop-recommendation`    | POST   | Request a crop recommendation                        |
| `/api/recommend-crop`         | POST   | Access crop recommendation functionality             |
| `/api/crop-ml-recommendation` | POST   | Request a Machine Learning-based crop recommendation |

**Note:** Request parameters and response formats depend on the implementation in `app.py`.

## 🔮 Future Enhancements

* Improve the accuracy of crop recommendations.
* Expand the agricultural knowledge base.
* Enhance Tamil-language support.
* Integrate weather and soil information.
* Add more crop-specific guidance.
* Deploy the backend for online access.

## 👩‍💻 Repository

**GitHub:** https://github.com/klingapabitha2006-hue/AgriGPT-AI

## 📄 License

A license can be added to the repository when the project distribution terms are decided.
