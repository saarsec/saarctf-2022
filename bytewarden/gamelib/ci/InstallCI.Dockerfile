# Install service
FROM saarsec/saarctf-ci-base
ADD . /opt/
WORKDIR /opt/
RUN bash -c 'ls -la /opt && source ./gamelib/ci/buildscripts/prepare-install.sh && ./install.sh && ./gamelib/ci/buildscripts/post-install.sh'
CMD ["python3", "-u", "/opt/systemd-replacement.py"]
