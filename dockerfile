FROM mcr.microsoft.com/playwright/python:v1.44.0-focal

RUN pip install boto3 playwright
RUN pip install https://github.com/aws/aws-lambda-python-runtime-interface-client/releases/download/v2.0.1/aws_lambda_ric-2.0.1-py3-none-any.whl

RUN playwright install chromium

# Copie ton code
COPY lambda_function.py ./

CMD ["lambda_function.lambda_handler"]
