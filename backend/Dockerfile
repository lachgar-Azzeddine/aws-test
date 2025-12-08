FROM mrabbah/harmo-base:latest
USER devops

WORKDIR /home/devops

# Create directories needed for application data and configuration
RUN mkdir -p /home/devops/.local/bin /home/devops/data/.kube /home/devops/data/inventory /home/devops/data/env /home/devops/data/terraform /home/devops/data/doc

# Install nvm and Node.js
ENV NVM_DIR="/home/devops/.nvm"
ENV NODE_VERSION="24"
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash && \
  . $NVM_DIR/nvm.sh && \
  nvm install $NODE_VERSION && \
  ln -s "$(nvm which $NODE_VERSION)" /home/devops/.local/bin/node && \
  ln -s "$(dirname $(nvm which $NODE_VERSION))/npm" /home/devops/.local/bin/npm && \
  node -v && \
  npm -v

# Install claude
RUN curl -fsSL https://claude.ai/install.sh | bash

# Copy application files
COPY api.py .
COPY repository.py .
COPY initial_db.py .
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY models.py .
COPY install.py .
COPY env /home/devops/data/env
COPY inventory /home/devops/data/inventory
COPY project /home/devops/data/project
COPY doc /home/devops/data/doc
COPY README.md .
COPY CHANGELOG.md .
COPY tar_images.py /home/devops/data/

USER root

# Consolidate permission changes into a single layer for optimization
RUN chown devops:devops api.py repository.py initial_db.py models.py install.py README.md CHANGELOG.md /home/devops/data/tar_images.py && \
  chown -R devops:devops /home/devops/data/inventory /home/devops/data/doc /home/devops/data/project /home/devops/data/env && \
  chown devops:devops /usr/local/bin/entrypoint.sh && \
  chmod +x /usr/local/bin/entrypoint.sh

USER devops
# Set proxy for http and https for environments requiring a proxy to access internet
#ENV http_proxy="http://10.97.243.181:808/"
#ENV https_proxy="http://10.97.243.181:808/"
#ENV no_proxy="localhost,127.0.0.1,10.0.0.0/8,172.0.0.0/8,*.lydec.wnet,*.srm-cs.wnet"
ENV INFORMIXDIR='/opt/IBM/Informix.4.50.FC11W1'
ENV CSDK_HOME=${INFORMIXDIR}
ENV PATH=$INFORMIXDIR/bin:/home/devops/.local/bin:$PATH
ENV LD_LIBRARY_PATH=$INFORMIXDIR/lib:$INFORMIXDIR/lib/esql:$INFORMIXDIR/lib/cli

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn", "--workers", "2", "--timeout", "3600", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8008", "api:app"]
