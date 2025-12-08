FROM ubuntu:24.04

RUN apt-get update && apt-get upgrade -y
# Install Python3, pip, and virtualenv
RUN apt-get update && apt-get install -y --fix-broken rsync sudo python3 python3-pip python3-venv git curl wget vim sshpass openssl openssh-client gnupg2 p7zip-full zip unzip netcat-openbsd docker.io netcat-traditional libssl-dev libffi-dev libdlt2 libcrypt1 libpam0g libstdc++6 libgcc1 libc6 libncurses6 libelf1 expect file
# Install kubectl, mc, terraform, govc, rke2
RUN wget https://dl.k8s.io/release/v1.31.1/bin/linux/amd64/kubectl -O /usr/local/bin/kubectl
RUN chmod +x /usr/local/bin/kubectl

RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc
RUN chmod +x /usr/local/bin/mc

RUN wget https://releases.hashicorp.com/terraform/1.9.8/terraform_1.9.8_linux_amd64.zip -O /tmp/terraform.zip
RUN unzip /tmp/terraform.zip -d /usr/local/bin
RUN rm /tmp/terraform.zip
RUN chmod +x /usr/local/bin/terraform

RUN wget https://github.com/vmware/govmomi/releases/download/v0.45.0/govc_Linux_x86_64.tar.gz -O /tmp/govc.tar.gz
RUN tar -xvf /tmp/govc.tar.gz -C /usr/local/bin
RUN rm /tmp/govc.tar.gz
RUN chmod +x /usr/local/bin/govc

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



RUN chmod +x /opt/informix-installer/installclientsdk &&  expect -c ' \
  set timeout 30; \
  spawn /opt/informix-installer/installclientsdk; \
  expect "PRESS <ENTER> TO CONTINUE: "; \
  send "\r"; \
  sleep 5; \
  expect "Press Enter to continue viewing the license agreement, or enter \"1\" to accept the agreement, \"2\" to decline it, \"3\" to print it, or \"99\" to go back to the previous screen.: "; \
  send "1\r"; \
  sleep 5; \
  expect "ENTER AN ABSOLUTE PATH, OR PRESS <ENTER> TO ACCEPT THE DEFAULT\r\t: "; \
  send "\r"; \
  sleep 5; \
  expect "ENTER THE NUMBER FOR YOUR CHOICE, OR PRESS <ENTER> TO ACCEPT THE DEFAULT: "; \
  send "2\r"; \
  sleep 5; \
  expect "Press <ENTER> to install above selected features or choose the corresponding number to change the feature selection: "; \
  send "\r"; \
  expect "PRESS <ENTER> TO CONTINUE: "; \
  send "\r"; \
  expect "PRESS <ENTER> TO EXIT THE INSTALLER: "; \
  send "\r"; \
  '
RUN rm -rf /opt/informix-installer

RUN touch /opt/IBM/Informix.4.50.FC11W1/etc/sqlhosts

ENV INFORMIXDIR='/opt/IBM/Informix.4.50.FC11W1'
ENV CSDK_HOME=${INFORMIXDIR}
ENV PATH=$INFORMIXDIR/bin:$PATH
ENV LD_LIBRARY_PATH=$INFORMIXDIR/lib:$INFORMIXDIR/lib/esql:$INFORMIXDIR/lib/cli

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
RUN chown devops:devops /opt/IBM/Informix.4.50.FC11W1/etc/sqlhosts

USER devops
RUN /home/devops/venv/bin/pip install --no-cache-dir -r /home/devops/requirements.txt

# RUN apt-get update
# RUN apt-get install helm
USER root
RUN apt-get clean
USER devops

