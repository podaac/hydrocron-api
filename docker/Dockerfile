FROM public.ecr.aws/lambda/python:3.8

COPY $SOURCE .
RUN pip3 install -t /var/task --force ./$SOURCE

# Run the lambda
CMD ["/var/task/podaac/controllers/fts_controller.lambda_handler"]