# 🌍 TripBuddy AI - Intelligent Travel Companion

A powerful **Azure AI** based real-time travel assistant built by a beginner developer.

## ✨ Features

- **📸 Image Analyzer** - Describe scenes, read signs & menus using Computer Vision
- **🌐 Real-time Translator** - Translate text into multiple languages
- **🔊 Voice Output** - Listen to translations with natural Indian & English voices
- **📄 Document Scanner** - Extract information from tickets, bookings, invoices
- **⭐ Review Analyzer** - Sentiment analysis + key points from hotel/restaurant reviews

## 🛠 Technologies Used

- **Azure AI Services**:
- **Azure AI Vision (Image Analysis)**
- **Azure AI Translator**
- **Azure AI Speech (Text-to-Speech)**
- **Azure AI Document Intelligence**
- **Azure AI Text Analytics**

- **Backend**: Python + Flask
- **Frontend**: HTML, Tailwind CSS, JavaScript

## 🚀 How to Run

1. Clone / Open the project folder
2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
3. Install dependencies:
   ```bash
   pip install flask azure-ai-vision-imageanalysis azure-ai-translation-text azure-cognitiveservices-speech azure-ai-documentintelligence azure-ai-textanalytics pillow requests
4. Run the application:
   ```bash
   python app.py
5. Open your browser and go to: ```http://127.0.0.1:5000```
6. Paste your Azure service Endpoints and Keys in the configuration section and click "Save Configuration".
