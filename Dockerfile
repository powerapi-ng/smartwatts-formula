FROM gfieni/powerapi:base

# Put the Python dependencies into a layer to optimize the image build time
COPY --chown=powerapi requirements.txt /opt/powerapi/smartwatts-requirements.txt
RUN pip3 install --user --no-cache-dir -r /opt/powerapi/smartwatts-requirements.txt

COPY --chown=powerapi . /opt/powerapi/smartwatts
RUN pip3 install --user --no-cache-dir --no-deps -e /opt/powerapi/smartwatts

ENTRYPOINT ["python3", "-m", "smartwatts"]