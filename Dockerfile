FROM powerapi/powerapi:0.6.11

COPY --chown=powerapi . /tmp/smartwatts
RUN pip3 install --user --no-cache-dir "/tmp/smartwatts" && rm -r /tmp/smartwatts

ENTRYPOINT ["python3", "-m", "smartwatts"]
