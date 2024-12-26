# Spam and Emotion Detection System

A text analysis system for detecting spam and analyzing emotions in textual content (emails, contact forms, etc.).

## 🚀 Features

- Spam detection in text content
- Emotion analysis in text
- REST API for integration
- Admin interface for testing and feedback
- Docker containerization

## 📁 Project Structure & Setup

### `/api`

REST API built with FastAPI for predictions and feedback collection.

#### Installation & Usage

Clone the repository and navigate to the API directory:
cd api

Build and run with Docker:
docker build -t spam-emotion-api .
docker run -p 8000:8000 spam-emotion-api

The API will be available at http://localhost:8000
Swagger documentation at http://localhost:8000/docs

### `/front`

Admin interface built with Laravel/Filament for API testing and feedback management.

#### Installation & Usage

cd front

composer install
npm install

cp .env.example .env
php artisan key:generate
php artisan migrate
php artisan serve
npm run dev

Access the admin panel at http://localhost:8000

### `/spam`

Jupyter notebooks for spam detection model training.

#### Usage

pip install -r requirements.txt

### `/emotions`

Jupyter notebooks for emotion analysis using LSTM and RoBERTa models.

#### Usage

pip install -r requirements.txt

## 📚 API Documentation

The API provides the following endpoints:

- POST /predict/spam: Detect spam in text content
- POST /predict/emotion: Analyze emotions in text
- POST /feedback: Submit feedback for predictions

Detailed API documentation is available through Swagger UI at /docs endpoint.

## 🔧 System Requirements

- Python 3.8+
- PHP 8.1+
- Node.js 16+
- Docker
- Composer
- npm

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch:
   git checkout -b feature/amazing-feature
3. Commit your changes:
   git commit -m 'Add some amazing feature'
4. Push to the branch:
   git push origin feature/amazing-feature
5. Open a Pull Request

## 📝 License

[MIT License](LICENSE)

## 📫 Support

For support, please open an issue in the GitHub repository.
