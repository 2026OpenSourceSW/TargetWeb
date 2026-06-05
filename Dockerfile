FROM python:3.12-slim

WORKDIR /app
COPY app.py /app/app.py

ENV OWASP_LAB_HOST=0.0.0.0
ENV OWASP_LAB_PORT=8000

EXPOSE 8000
CMD ["python", "app.py"]
