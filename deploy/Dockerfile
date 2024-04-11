FROM alpine as git

RUN apk add --no-cache git openssh-client

RUN mkdir ~/.ssh && \
    echo "$id" > /root/.ssh/id_rsa && \
    echo "$id_pub" > /root/.ssh/id_rsa.pub && \
    chmod 600 /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa.pub && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts && \
    mkdir /tmp/repo && \
    git clone ${repo} /tmp/repo && \
    cd /tmp/repo && \
    git checkout ${branch} && \
    git pull && \
    rm -rf /root/.ssh

FROM node:20.12.2 as node-build

RUN npm install -g @quasar/cli
COPY --from=git /tmp/repo/frontend/package.json /tmp/repo/frontend/package-lock.json /app/
WORKDIR /app
RUN npm install

COPY --from=git /tmp/repo/frontend/ /app

RUN BACKEND_URL=${backend_url} npx quasar build


FROM python:3.10-slim as backend

COPY --from=git /tmp/repo/backend/requirements.txt /tmp/
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y
RUN pip install -r /tmp/requirements.txt
COPY --from=git /tmp/repo/backend /app
COPY --from=node-build /app/dist/spa /app/semant_annotation/static
WORKDIR /app
ENTRYPOINT [ "python", "run.py" ]