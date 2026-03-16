FROM python:alpine

LABEL author="Borgia Leiva <edoardo.borgia.leiva@outlook.com>"
LABEL version="0.1.dev1"
LABEL description="Backend image for Group&Meet made with FastAPI."

WORKDIR /usr/src/group_n_meet_backend
COPY .  /usr/src/group_n_meet_backend

## Installing build dependencies
RUN apk update && \
    apk add --no-cache build-base gcc musl-dev wget

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir .

EXPOSE 8000
CMD [ "gnm-backend" ]

HEALTHCHECK \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1