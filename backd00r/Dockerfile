# Build things
FROM saarsec/saarctf-ci-base AS buildstage
ENV SERVICENAME=backd00r
ADD ./service /opt/service
ADD ./build.sh /opt/
WORKDIR /opt/
RUN echo $SERVICENAME > servicename && ./build.sh && ls -la /opt

# Install service
FROM saarsec/saarctf-ci-base
ENV SERVICENAME=backd00r
COPY --from=buildstage /opt /opt/
ADD ./gamelib /opt/gamelib
ADD ./install.sh /opt/install.sh
WORKDIR /opt/
RUN bash -c 'source ./gamelib/ci/buildscripts/prepare-install.sh && ./install.sh && ./gamelib/ci/buildscripts/post-install.sh'
CMD ["python3", "-u", "/opt/systemd-replacement.py"]