FROM docker.io/powerapi/powerapi:2.5.0@sha256:cecbff7b19c7f6383f8cf67ea478ed0122ee70b34345c0035e667ae5fe5627b2

USER powerapi
COPY --chown=powerapi . /tmp/smartwatts
RUN pip install --user --no-cache-dir "/tmp/smartwatts" && rm -r /tmp/smartwatts

ENTRYPOINT ["python3", "-m", "smartwatts"]
