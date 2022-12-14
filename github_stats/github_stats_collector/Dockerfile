# following the guide at https://docs.aws.amazon.com/lambda/latest/dg/images-create.html#images-create-1
FROM public.ecr.aws/lambda/python:3.8
COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

## Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}
COPY records.py ${LAMBDA_TASK_ROOT}
COPY __init__.py ${LAMBDA_TASK_ROOT}

## Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]
