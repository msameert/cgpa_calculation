FROM python:3.13.4
EXPOSE 8501
WORKDIR /gpa
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["streamlit","run","gpa.py","--server.port=8501","--server.address=0.0.0.0"]