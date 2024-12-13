# Change this to needed starting image
# Base Image
FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu20.04
# Latch environment building
COPY --from=812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base-cuda:fe0b-main /bin/flytectl /bin/flytectl
WORKDIR /root

ENV VENV /opt/venv
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONPATH /root
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y libsm6 libxext6 libxrender-dev build-essential procps rsync openssh-server

RUN apt-get update && \
    apt-get install -y software-properties-common &&\
    add-apt-repository -y ppa:deadsnakes/ppa &&\
    apt-get install -y python3.10 python3-pip python3.10-distutils curl

# Install pip using get-pip.py
RUN curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.10 get-pip.py && \
    rm get-pip.py

# Install AWS CLI
RUN python3.10 -m pip install --no-cache-dir awscli

RUN curl -L https://github.com/peak/s5cmd/releases/download/v2.0.0/s5cmd_2.0.0_Linux-64bit.tar.gz -o s5cmd_2.0.0_Linux-64bit.tar.gz &&\
    tar -xzvf s5cmd_2.0.0_Linux-64bit.tar.gz &&\
    mv s5cmd /bin/ &&\
    rm CHANGELOG.md LICENSE README.md

COPY --from=812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base-cuda:fe0b-main /root/Makefile /root/Makefile
COPY --from=812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base-cuda:fe0b-main /root/flytekit.config /root/flytekit.config

# Set work directory
WORKDIR /tmp/docker-build/work/

SHELL [ \
    "/usr/bin/env", "bash", \
    "-o", "errexit", \
    "-o", "pipefail", \
    "-o", "nounset", \
    "-o", "verbose", \
    "-o", "errtrace", \
    "-O", "inherit_errexit", \
    "-O", "shift_verbose", \
    "-c" \
]
ENV TZ='Etc/UTC'
ENV LANG='en_US.UTF-8'

ARG DEBIAN_FRONTEND=noninteractive

# Latch SDK
# DO NOT REMOVE
RUN pip install latch==2.53.12
RUN mkdir /opt/latch

# Can include install commands here
RUN apt-get update && apt-get install -y \
    wget \
    git

# Install BLAST
RUN wget https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.16.0+-x64-linux.tar.gz && \
    tar -xzvf ncbi-blast-2.16.0+-x64-linux.tar.gz && \
    cp ncbi-blast-2.16.0+/bin/* /usr/local/bin/ && \
    rm -rf ncbi-blast-2.16.0+-x64-linux.tar.gz ncbi-blast-2.16.0+

# Install Filtlong
RUN git clone https://github.com/rrwick/Filtlong.git && \
    cd Filtlong && \
    make -j && \
    mv bin/filtlong /usr/local/bin/ && \
    cd .. && \
    rm -rf Filtlong

RUN pip install pandas

# Copy workflow data (use .dockerignore to skip files)
COPY . /root/

# Latch workflow registration metadata
# DO NOT CHANGE
ARG tag

# DO NOT CHANGE
ENV FLYTE_INTERNAL_IMAGE $tag

WORKDIR /root
