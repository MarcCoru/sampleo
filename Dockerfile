FROM ubuntu:18.04

LABEL maintainer="Marc Rußwurm <marc.russwurm@tum.de>"




# update and install packages
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev curl \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

# add google cloud sdk to packages
RUN echo "deb http://packages.cloud.google.com/apt cloud-sdk-bionic main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
  && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

RUN apt-get update && apt-get install -y google-cloud-sdk

# install python packages
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

COPY ./ /sampleo/
WORKDIR "/sampleo"

# CMD ["/bin/bash"]
#ENTRYPOINT ["/bin/bash"]
