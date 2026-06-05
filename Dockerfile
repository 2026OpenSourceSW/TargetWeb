FROM python:3.12-slim

WORKDIR /app
COPY app.py /app/app.py
COPY sites /app/sites

ENV OWASP_LAB_HOST=0.0.0.0

EXPOSE 8101 8102 8103 8104 8105 8106 8107 8108 8109 8110 8111
CMD ["python", "app.py"]
