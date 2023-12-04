import time
from os import environ
from os import system
from paho.mqtt.client import Client
from ha_mqtt.ha_device import HaDevice
from ha_mqtt.mqtt_device_base import MqttDeviceSettings
from ha_mqtt.mqtt_switch import MqttSwitch
from ir_sender import IRSender

# Define callback function to handle incoming messages
def on_message(client, userdata, message):
    # print(message)
    print("got payload", message.payload.decode())

# Read the MQTT broker host, username, and password from environment variables
host = environ.get("MQTT_BROKER_HOST")
port = int(environ.get("MQTT_BROKER_PORT"))
username = environ.get("MQTT_USERNAME")
password = environ.get("MQTT_PASSWORD")
device_uuid = environ.get("BALENA_DEVICE_UUID")
ir_config = environ.get("IR_CONFIG")
ir_send_repeat = int(environ.get("SEND_REPEAT"))
on_key = environ.get("IR_ON_KEY")
off_key = environ.get("IR_OFF_KEY")

# Set up IR sender

ir_sender = IRSender(ir_config, ir_send_repeat)

# Set up client object
client = Client(f"ac-ir-{device_uuid}4")
client.username_pw_set(username, password)

# Set up TLS/SSL context
# tls_context = ssl.create_default_context()
# tls_context.check_hostname = False
# tls_context.verify_mode = ssl.CERT_NONE

# Set up client credentials and connect to broker
# client.tls_set_context(tls_context)

client.connect(host, port)
client.loop_start()

# callbacks for the on and off actions
def on(entity: MqttSwitch, id: int):
    print(f"{id} got switch on command")
    success = ir_sender.send_key(on_key)
    if success:
        print(f"{id} switched on")
        entity.set_on()
    else:
        print(f"{id} failed to switch on")


def off(entity: MqttSwitch, id: int):
    print(f"{id} got switch off command")
    success = ir_sender.send_key(off_key)
    if success:
        print(f"{id} switched off")
        entity.set_off()
    else:
        print(f"{id} failed to switch off")

# create device info dictionary
dev = HaDevice("AC IR Remote", f"ac-ir-{device_uuid}")

# instantiate an MQTTSwitch object
sw1 = MqttSwitch(MqttDeviceSettings("ac-sw", f"ac_sw_{device_uuid}", client, dev))

# assign both callbacks
sw1.callback_on = lambda: on(sw1, 1)
sw1.callback_off = lambda: off(sw1, 1)

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    # close the device for cleanup. Gets marked as offline/unavailable in homeassistant
    sw1.close()
    client.loop_stop()
    client.disconnect()

