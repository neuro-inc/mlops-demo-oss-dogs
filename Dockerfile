FROM neuromation/base:v1.7.8

# TODO: do not use /project dir since it persists and afterwards can't be used for git clone. use /tmp/project
RUN mkdir /project
WORKDIR /project

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
RUN curl -o /tmp/pachctl.deb -L https://github.com/pachyderm/pachyderm/releases/download/v1.12.3/pachctl_1.12.3_amd64.deb \
    && dpkg -i /tmp/pachctl.deb \
    && rm -f /tmp/pachctl.deb
