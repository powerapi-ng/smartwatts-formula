FROM ghcr.io/powerapi-ng/powerapi:2.10.0@sha256:04af70333dc8c87d0bffe7596e21867fe1c2bd57e85825f8dd831f6a50936641

COPY --chown=powerapi . /tmp/smartwatts
RUN pip install --no-cache-dir "/tmp/smartwatts" && rm -r /tmp/smartwatts

USER powerapi
ENTRYPOINT ["python3", "-m", "smartwatts"]
