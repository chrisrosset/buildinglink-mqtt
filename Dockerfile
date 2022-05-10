FROM python:3.9-bullseye
ENTRYPOINT []

RUN apt-get update && \
    apt-get -qy install \
    python3-lxml \
    python3-paho-mqtt \
    python3-requests

RUN mkdir /app && chmod 777 /app
COPY buildinglink_mqtt.py /app
WORKDIR "/app"

ENV PYTHONPATH="/usr/lib/python3/dist-packages"
CMD ["python3", "buildinglink_mqtt.py"]
