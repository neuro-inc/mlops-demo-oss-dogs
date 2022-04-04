FROM heartexlabs/label-studio:1.4.0

# Install DVC and Git (needed for DVC)
RUN apt update -y -qq --allow-releaseinfo-change && \
    apt install -y -qq git rsync lsyncd procps curl unzip openssh-client python3.8-venv

# install pachyderm CLI
RUN curl -o /tmp/pachctl.deb -L https://github.com/pachyderm/pachyderm/releases/download/v2.0.2/pachctl_2.0.2_amd64.deb \
    && dpkg -i /tmp/pachctl.deb \
    && rm -f /tmp/pachctl.deb

RUN pip install --progress-bar=off -U pip
RUN pip install --progress-bar=off -U pipx && pipx install neuro-cli

RUN mkdir ~/.ssh && echo "IdentityFile ~/.ssh/id-rsa" > ~/.ssh/config
RUN ssh-keyscan github.com >> ~/.ssh/known_hosts

ENV PATH /root/.local/bin:$PATH