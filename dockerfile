FROM mcr.microsoft.com/playwright/python:v1.44.0-focal

RUN pip install playwright boto3 aws-lambda-ric
RUN playwright install chromium

# Copie ton code
COPY lambda_function.py ./

CMD ["lambda_function.lambda_handler"]
