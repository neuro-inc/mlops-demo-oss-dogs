FROM ghcr.io/neuro-inc/base:v22.2.1-devel

# TODO: do not use /project dir since it persists and afterwards can't be used for git clone. use /tmp/project
RUN mkdir -p /tmp/project
WORKDIR /tmp/project

COPY requirements requirements
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get -qq update && \
    cat requirements/apt.txt | tr -d "\r" | xargs -I % apt-get -qq install --no-install-recommends % && \
    apt-get -qq clean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/*

COPY setup.cfg .

RUN pip install --progress-bar=off -U --no-cache-dir -r requirements/python-base.txt

RUN ssh-keygen -f /id_rsa -t rsa -N neuromation -q

# install pachyderm CLI
RUN curl -o /tmp/pachctl.deb -L https://github.com/pachyderm/pachyderm/releases/download/v2.0.2/pachctl_2.0.2_amd64.deb \
    && dpkg -i /tmp/pachctl.deb \
    && rm -f /tmp/pachctl.deb

RUN mkdir ~/.ssh && echo "IdentityFile ~/.ssh/id-rsa" > ~/.ssh/config
RUN ssh-keyscan github.com >> ~/.ssh/known_hosts
