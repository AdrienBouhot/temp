FROM mcr.microsoft.com/playwright/python:v1.50.0-noble

RUN pip install boto3 playwright aws-lambda-ric
RUN playwright install chromium

# Copie ton code
COPY lambda_function.py ./

CMD ["lambda_function.lambda_handler"]
