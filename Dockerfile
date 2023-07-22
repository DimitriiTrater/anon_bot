FROM python:latest
WORKDIR /app/ 
COPY . /app/
RUN pip install --user vkbottle
CMD ["python", "main.py"]
