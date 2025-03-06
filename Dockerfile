FROM ghcr.io/powerapi-ng/powerapi:2.9.1@sha256:81fd8527aed8e67653ab1b1ef26d872cd790dda5e058090b1e88c7d7ccdc2c2d

COPY --chown=powerapi . /tmp/smartwatts
RUN pip install --no-cache-dir "/tmp/smartwatts" && rm -r /tmp/smartwatts

USER powerapi
ENTRYPOINT ["python3", "-m", "smartwatts"]
