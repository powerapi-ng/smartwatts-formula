FROM docker.io/powerapi/powerapi:2.2.0@sha256:534e53d78b5bd334922b1a2a412db92b99cf47bb7c838fde955eedbbc65014b2

USER powerapi
COPY --chown=powerapi . /tmp/smartwatts
RUN pip install --user --no-cache-dir "/tmp/smartwatts" && rm -r /tmp/smartwatts

ENTRYPOINT ["python3", "-m", "smartwatts"]
