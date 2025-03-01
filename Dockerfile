FROM python:3.9-slim
WORKDIR /app
COPY MedGenAiBackend/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY MedGenAiBackend/ MedGenAiBackend/
COPY MedGenAI-Images/ MedGenAI-Images/
WORKDIR /app/MedGenAiBackend 
EXPOSE 5328
CMD ["python3", "app.py"]
