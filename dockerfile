##
## dockerfile
##
## Author: Borgia Leiva <edoardo.borgia.leiva@outlook.com> 
##

## Builder stage
FROM python:alpine AS builder

RUN apk add --no-cache build-base gcc musl-dev libffi-dev

WORKDIR /usr/src/group_n_meet_backend

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

COPY . .
RUN pip install --no-cache-dir --prefix=/install .

## Runner stage
FROM python:alpine

LABEL author="Borgia Leiva <edoardo.borgia.leiva@outlook.com>"
LABEL version="0.1.dev1"
LABEL description="Backend image for Group&Meet made with FastAPI."

COPY --from=builder /install /usr/local
COPY --chmod=755 . .

EXPOSE 8000
CMD [ "gnm-backend" ]

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1