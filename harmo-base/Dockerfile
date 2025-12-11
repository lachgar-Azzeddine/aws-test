FROM ubuntu:24.04

RUN apt-get update && apt-get upgrade -y
# Install Python3, pip, and virtualenv
RUN apt-get update && apt-get install -y --fix-broken rsync sudo python3 python3-pip python3-venv git curl wget vim sshpass openssl openssh-client gnupg2 p7zip-full zip unzip netcat-openbsd docker.io netcat-traditional libssl-dev libffi-dev libdlt2 libcrypt1 libpam0g libstdc++6 libgcc1 libc6 libncurses6 libelf1 expect file
# Install kubectl, mc, terraform, govc, rke2
RUN wget https://dl.k8s.io/release/v1.31.1/bin/linux/amd64/kubectl -O /usr/local/bin/kubectl
RUN chmod +x /usr/local/bin/kubectl

RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc
RUN chmod +x /usr/local/bin/mc


RUN wget https://github.com/rancher/rke2/releases/download/v1.31.1%2Brke2r2/rke2.linux-amd64 -O /usr/local/bin/rke2
RUN chmod +x /usr/local/bin/rke2

# Install helm
RUN HELM_VERSION=v3.15.4 && \
  curl -fsSL https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz -o helm.tar.gz && \
  tar -xzf helm.tar.gz && \
  mv linux-amd64/helm /usr/local/bin/helm && \
  rm -rf linux-amd64 helm.tar.gz

RUN wget https://www.python.org/ftp/python/3.7.10/Python-3.7.10.tar.xz 

RUN tar -xvf Python-3.7.10.tar.xz

RUN cd Python-3.7.10 && \
  ./configure --enable-optimizations --with-ensurepip && \
  make -j$(nproc) && \
  make altinstall  

RUN rm Python-3.7.10.tar.xz  && rm -rf Python-3.7.10


RUN useradd -ms /bin/bash devops
RUN usermod -aG docker devops

USER devops

RUN python3.7 -m venv /home/devops/venv_37

RUN  /home/devops/venv_37/bin/pip install ifxpy==3.0.2

COPY ./informix_test.py /home/devops/venv_37
# Create a virtual environment for Python
RUN python3 -m venv /home/devops/venv
ENV PATH="/home/devops/venv/bin:$PATH"

# Install ansible and other Python dependencies in the virtual environment
RUN pip3 install --no-cache-dir ansible
RUN pip3 install --no-cache-dir kubernetes PyYAML jsonpatch jmespath
RUN ansible-galaxy collection install kubernetes.core

WORKDIR /home/devops
COPY ./requirements.txt .
USER root
RUN chown devops:devops requirements.txt


USER devops
RUN /home/devops/venv/bin/pip install --no-cache-dir -r /home/devops/requirements.txt

# RUN apt-get update
# RUN apt-get install helm
USER root
RUN apt-get clean
USER devops

