#!/usr/bin/env python3

import datetime
import json
import logging
import pickle
import time

import paho.mqtt.client as mqtt

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

import config

BASE_URL = "https://www.buildinglink.com/"
PACKAGES_PAGE = "V2/Tenant/Deliveries/Deliveries.aspx"
PACKAGES_TABLE_ID = "ctl00_ContentPlaceHolder1_GridDeliveries_ctl00"
PACKAGES_XPATH = f"//table[@id='{PACKAGES_TABLE_ID}']/tbody/tr"

def load_page(driver, page, cfg):
    try:
        driver.get(page)
        for e in [("UserName", cfg['username']), ("Password", cfg['password'])]:
            box = driver.find_element_by_id(e[0])
            box.clear()
            box.send_keys(e[1])

        logging.info("Logging in.")
        button = driver.find_element_by_id("LoginButton")
        button.click()
    except NoSuchElementException:
        logging.info("Already logged in.")
        return

def mqtt_base_topic(cfg):
    return f"{cfg['discovery_prefix']}/sensor/buildinglink"

def publish_mqtt(client, data, cfg):
    client.publish(f"{mqtt_base_topic(cfg)}/state", json.dumps(data), retain=True)

def on_connect(client, userdata, flags, rc, cfg):
    logging.info("Connected to the MQTT broker. rc=" + str(rc))

    base = mqtt_base_topic(cfg)
    client.publish(f"{base}-packages/config", json.dumps({
        "name": "BuildingLink Packages",
        "unique_id": "buildinglink_packages",
        "state_topic": f"{base}/state",
        "icon": "mdi:package-variant",
        "unit_of_measurement": "package(s)",
        "value_template": "{{ value_json.packages | int }}"
    }), retain=True)

def on_disconnect(client, userdata, rc):
    logging.info("Disconnected from the MQTT broker. rc=" + str(rc))

def get_package_count(trs):
    count = len(trs)

    if count == 0:
        logging.warn(f"No package rows found at all")
        count = None
    elif count == 1:
        if "rgNoRecords" in trs[0].get_attribute("class"):
            logging.debug(f"rgNoRecords found; 0 packages")
            count = 0

    return count

def main():
    logging.basicConfig(level=logging.INFO)

    cfg = config.CONFIG

    client = mqtt.Client(client_id=cfg["client_id"])
    client.on_connect = lambda c, u, f, rc: on_connect(c, u, f, rc, cfg)
    client.on_disconnect = on_disconnect
    client.connect(cfg["broker"]["host"])
    client.loop_start()

    options = Options()
    options.headless = True

    with webdriver.Firefox(options=options) as driver:
        driver.implicitly_wait(10)
        driver.get(BASE_URL)

        url = f"{BASE_URL}/{PACKAGES_PAGE}"
        load_page(driver, url, cfg)

        packages = -1

        while True:
            logging.info(f"{str(datetime.datetime.now())}")
            driver.refresh()

            table = driver.find_element_by_id(PACKAGES_TABLE_ID) # implicit wait

            pkg_count = get_package_count(driver.find_elements_by_xpath(PACKAGES_XPATH))

            if pkg_count is not None:
                logging.info(f"{str(pkg_count)} package(s)")

                if packages != pkg_count:
                    packages = pkg_count
                    logging.info(f"Publishing: {packages} package(s) for pickup.")
                    publish_mqtt(client, {"packages": packages}, cfg)

            time.sleep(cfg["refresh_interval"])


if __name__ == "__main__":
    main()
