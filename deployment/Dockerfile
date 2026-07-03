FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install fastapi uvicorn scikit-learn pandas joblib

# Copy model files and app
COPY model/models/ ./model/models/
COPY deployment/app.py ./app.py

# Expose port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
