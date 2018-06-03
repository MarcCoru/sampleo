FROM ubuntu:18.04

LABEL maintainer="Marc Rußwurm <marc.russwurm@tum.de>"

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

COPY ./ /sampleo/
WORKDIR "/sampleo"

# CMD ["/bin/bash"]
ENTRYPOINT ["/bin/bash"]
