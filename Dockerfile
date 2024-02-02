FROM docker.io/powerapi/powerapi:2.3.0@sha256:a5ff16ec42411cef2739fcd0ea3cf409a16edf572a9b50e036e2ebac5c32e1d0

USER powerapi
COPY --chown=powerapi . /tmp/smartwatts
RUN pip install --user --no-cache-dir "/tmp/smartwatts" && rm -r /tmp/smartwatts

ENTRYPOINT ["python3", "-m", "smartwatts"]
