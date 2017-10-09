# To build:
#
#     $ docker build -t bless_server:latest .
#
# To run, set AWS_* env vars, then:
#
#     $ docker run -p 8000:8000 -it \
#         --env AWS_REGION \
#         --env AWS_ACCESS_KEY_ID \
#         --env AWS_SECRET_ACCESS_KEY \
#         -v /local/path/to/config/dir:/opt/bless_server/config \
#         bless_server:latest
#
FROM amazonlinux:latest
MAINTAINER Ryan Nagle
RUN yum install -y gcc \
  gcc-c++ \
  make \
  openssl-devel \
  python27 \
  python27-setuptools \
  python27-pip \
  python27-devel

ENV PROJECT=bless_server
ENV CONTAINER_HOME=/opt
ENV CONTAINER_PROJECT=$CONTAINER_HOME/$PROJECT

WORKDIR $CONTAINER_HOME
RUN mkdir logs
COPY . $CONTAINER_PROJECT

RUN pip install -r $CONTAINER_PROJECT/requirements.txt
RUN pip install gunicorn

WORKDIR $CONTAINER_PROJECT
COPY ./entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
