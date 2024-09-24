FROM docker.io/powerapi/powerapi:2.8.0@sha256:d1a3946c07e21971299fc9ea0d2b8313652d4865f6d3a044e7873716aa96430f

COPY --chown=powerapi . /tmp/smartwatts
RUN pip install --no-cache-dir "/tmp/smartwatts" && rm -r /tmp/smartwatts

USER powerapi
ENTRYPOINT ["python3", "-m", "smartwatts"]
