##
## dockerfile
##
## Author: Borgia Leiva <edoardo.borgia.leiva@outlook.com> <edbole@campusaula.com> 
##

## Builder stage
FROM python:slim AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev

WORKDIR /usr/src/group_n_meet_backend

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

COPY . .
RUN pip install --prefix=/install .

## Runner stage
FROM python:slim

LABEL author="Borgia Leiva <edoardo.borgia.leiva@outlook.com>"
LABEL version="0.1.dev1"
LABEL description="Backend image for Group&Meet made with FastAPI."

RUN apt-get update && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m group_n_meet
USER group_n_meet

COPY --from=builder /install /usr/local
COPY --chmod=755 . .

EXPOSE 8000
CMD [ "gnm-backend" ]

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1
