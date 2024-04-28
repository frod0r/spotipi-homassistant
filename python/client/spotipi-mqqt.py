import paho.mqtt.client as mqtt
import sys
import os
import configparser
import dbus
import time
import json
from multiprocessing.connection import Client

dir = os.path.dirname(__file__)
filename = os.path.join(dir, '../../config/rgb_options.ini')

# Configuration for the matrix
config = configparser.ConfigParser()
config.read(filename)

brightness = str(config['DEFAULT']['brightness'])
fullstate = {"state": "ON", "brightness": brightness}

sysbus = dbus.SystemBus()
systemd1 = sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
manager = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')
service = sysbus.get_object('org.freedesktop.systemd1', object_path=manager.GetUnit('spotipi.service'))
interface = dbus.Interface(service, dbus_interface='org.freedesktop.DBus.Properties')

client_name = "spotipi"
username = "homeassistant"
client_password = "xxx"
matrix_name = "rgb_matrix"
base_topic = "homeassistant/light/rgb-matrix"
config_topic = base_topic + "/config"
set_topic = base_topic + "/set"
state_topic = base_topic + "/state"
config_payload = '''{
  "~": "''' + base_topic + '''",
  "name": "''' + client_name + '''",
  "unique_id": "''' + matrix_name + '''",
  "cmd_t": "~/set",
  "stat_t": "~/state",
  "schema": "json",
  "brightness": true,
  "brightness_scale": 100
}'''

address = ('localhost', 6000)


def on_message(mqtt_client, userdata, message):
    print("message received ", str(message.payload.decode("utf-8")))
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)
    global fullstate
    global brightness
    # fullstate = {"state": "OFF", "brightness": 0}
    unit_state = interface.Get('org.freedesktop.systemd1.Unit', 'ActiveState')
    if unit_state == 'active':
        brightness = str(config['DEFAULT']['brightness'])
        fullstate = {"state": "ON", "brightness": int(brightness)}
    else:
        brightness = str(0)
        fullstate = {"state": "OFF", "brightness": int(brightness)}
    # print('active_state: ' + active_state)
    mqtt_client.publish(state_topic, json.dumps(fullstate), retain=True)


def on_set_message(mqtt_client, userdata, message):
    global fullstate
    global brightness
    print("in set topic")
    payload = json.loads(message.payload.decode("utf-8"))
    if "brightness" in payload:
        brightness = str(payload["brightness"])
        print("Set brightness to " + brightness)
        # Send brightness to matrix component
        with Client(address, authkey=b'LAEPYAc1v0GuX0fL') as conn:
            conn.send(['brightness', int(brightness)])
            conn.close()
        fullstate = {"state": "ON", "brightness": int(brightness)}
        # Save brightness as new default, to remember it at restart
        config.set('DEFAULT', 'brightness', brightness)
        with open(filename, 'w') as configfile:
            config.write(configfile)
            # os.close(configfile)
            # job = manager.RestartUnit('spotipi.service', 'fail')
            # Tell homeassistant we updated the state
            fullstate = {"state": "ON", "brightness": int(brightness)}
            mqtt_client.publish(state_topic, json.dumps(fullstate), retain=True)
    elif "state" in payload:
        state = payload["state"]
        if state == "ON":
            print("Turning on")
            brightness = str(config['DEFAULT']['brightness'])
            job = manager.StartUnit('spotipi.service', 'replace')
            fullstate = {"state": "ON", "brightness": int(brightness)}
            mqtt_client.publish(state_topic, json.dumps(fullstate), retain=True)
        elif state == "OFF":
            print("Turning off")
            brightness = str(0)
            job = manager.StopUnit('spotipi.service', 'replace')
            fullstate = {"state": "OFF", "brightness": int(brightness)}
            mqtt_client.publish(state_topic, json.dumps(fullstate), retain=True)


def on_disconnect(mqtt_client, userdata, rc):
    if rc != 0:
        print("Unexpected MQTT disconnection. Will auto-reconnect")


def on_connect(mqtt_client, userdata, flags, rc):
    global fullstate
    if rc != 0:
        print("Bad connection. Responding anyways.")
    else:
        print("Connected.")
    client.subscribe(set_topic)
    mqtt_client.publish(config_topic, config_payload, retain=True)
    mqtt_client.publish(state_topic, json.dumps(fullstate), retain=True)



client = mqtt.Client(client_name)
client.username_pw_set(username=username, password=client_password)
client.on_message=on_message
client.message_callback_add(set_topic, on_set_message)
client.on_disconnect = on_disconnect
client.on_connect = on_connect
client.connect("homeassistant")
client.subscribe(set_topic)
client.publish(config_topic, config_payload, retain=True)
client.publish(state_topic, json.dumps(fullstate), retain=True)

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
