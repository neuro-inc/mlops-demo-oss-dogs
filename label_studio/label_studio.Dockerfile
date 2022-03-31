FROM heartexlabs/label-studio:1.4.0

# Install DVC and Git (needed for DVC)
RUN apt update -y -qq --allow-releaseinfo-change && \
    apt install -y -qq git rsync lsyncd procps curl unzip openssh-client

# install pachyderm CLI
RUN curl -o /tmp/pachctl.deb -L https://github.com/pachyderm/pachyderm/releases/download/v2.0.2/pachctl_2.0.2_amd64.deb \
    && dpkg -i /tmp/pachctl.deb \
    && rm -f /tmp/pachctl.deb