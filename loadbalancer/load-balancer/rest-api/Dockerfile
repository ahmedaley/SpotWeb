#use an official Python runtime as a parent image
FROM python:3.6.2-slim

WORKDIR rest-api

ADD /src /rest-api

COPY entrypoint.sh /
RUN pip install --isolated flask_restful

RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
