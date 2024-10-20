# Voice Reader

This is a Flask-based web application that allows users to upload documents (PDF, TXT, DOCX) and converts the text into speech (TTS). The web app provides a user-friendly interface, supports multiple languages, and generates audio files from text.

## Features

- Upload PDF, TXT, and DOCX files.
- Convert text to speech using Google TTS.
- Dynamic language switching between English and Spanish.
- Downloadable audio file of the converted text.

## Getting Started

### Prerequisites

- Python 3.11
- Flask
- Babel
- gTTS (Google Text-to-Speech)
- pdfplumber
- docx

## Usage

1. Upload a `.pdf`, `.txt`, or `.docx` file.
2. The app will extract the text and convert it into speech.
3. Download the generated audio file in `.mp3` format.

## License

This project is licensed under the MIT License.
