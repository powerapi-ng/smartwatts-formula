FROM docker.io/powerapi/powerapi:2.1.0@sha256:2f0afe67265c1afa12dc400c0498c7e0849c6e425961b9461ef63002904ad675

USER powerapi
COPY --chown=powerapi . /tmp/smartwatts
RUN pip install --user --no-cache-dir "/tmp/smartwatts" && rm -r /tmp/smartwatts

ENTRYPOINT ["python3", "-m", "smartwatts"]
