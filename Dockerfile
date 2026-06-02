FROM python:3.11

WORKDIR /travel_time_prediction

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
    
CMD ["python", "orchestrator/orchestrator.py"]