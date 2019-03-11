FROM gfieni/powerapi:base

COPY --chown=powerapi . /opt/powerapi/smartwatts
RUN pip3 install --user --no-cache-dir -e "/opt/powerapi/smartwatts"

ENTRYPOINT ["python3", "-m", "smartwatts"]