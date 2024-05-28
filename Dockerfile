FROM docker.io/powerapi/powerapi:2.6.0@sha256:8f6d37e2c0d52a52d2acd98b97a4382a0b3566f15b101c90f9f8fd8a883b8cd2

USER powerapi
COPY --chown=powerapi . /tmp/smartwatts
RUN pip install --user --no-cache-dir "/tmp/smartwatts" && rm -r /tmp/smartwatts

ENTRYPOINT ["python3", "-m", "smartwatts"]
