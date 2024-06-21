FROM docker.io/powerapi/powerapi:2.7.0@sha256:0ce871bf2ad0b81d87cdc60eb115e48648f90a02a793c79936a35f36b87aeaf0

USER powerapi
COPY --chown=powerapi . /tmp/smartwatts
RUN pip install --user --no-cache-dir "/tmp/smartwatts" && rm -r /tmp/smartwatts

ENTRYPOINT ["python3", "-m", "smartwatts"]
