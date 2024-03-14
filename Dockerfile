FROM docker.io/powerapi/powerapi:2.4.0@sha256:7a2ff304ce0d2f3b591170fd890b2ea56f40ab690bc6911a55b5f0578c77324a

USER powerapi
COPY --chown=powerapi . /tmp/smartwatts
RUN pip install --user --no-cache-dir "/tmp/smartwatts" && rm -r /tmp/smartwatts

ENTRYPOINT ["python3", "-m", "smartwatts"]
