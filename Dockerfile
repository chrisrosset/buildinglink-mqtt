FROM selenium/standalone-firefox
ENTRYPOINT []

RUN sudo apt-get update && \
    sudo apt-get -qy install \
    python3-paho-mqtt \
    python3-selenium

RUN sudo mkdir /app && sudo chmod 777 /app
COPY buildinglink_mqtt.py /app
WORKDIR "/app"

CMD ["python3", "buildinglink_mqtt.py"]