# Install service
FROM saarsec/saarctf-ci-base
ADD ./build_output /opt/
ADD ./gamelib /opt/gamelib
WORKDIR /opt/
RUN bash -c 'ls -la /opt && source ./gamelib/ci/buildscripts/prepare-install.sh && ./install.sh && ./gamelib/ci/buildscripts/post-install.sh'
CMD ["sh", "-c", "/opt/publish-network-infos.sh && exec python3 -u /opt/systemd-replacement.py"]
