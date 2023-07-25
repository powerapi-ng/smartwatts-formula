FROM docker.io/powerapi/powerapi:2.1.0@sha256:d81766ebf3af9a555652fa275a708a0d151f40de81ca3e977a2c9fd7aaed06cf

USER powerapi
COPY --chown=powerapi . /tmp/smartwatts
RUN pip install --user --no-cache-dir "/tmp/smartwatts" && rm -r /tmp/smartwatts

ENTRYPOINT ["python3", "-m", "smartwatts"]
