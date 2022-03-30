FROM public.ecr.aws/lambda/python:3.8
COPY app.py ${LAMBDA_TASK_ROOT}
COPY extended-table.json ${LAMBDA_TASK_ROOT}
# COPY mock-original-table.xlsx ${LAMBDA_TASK_ROOT}
# COPY jwt_box_config.json ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
# RUN pip3 install "boxsdk[jwt]"
CMD ["app.lambda_handler"]
