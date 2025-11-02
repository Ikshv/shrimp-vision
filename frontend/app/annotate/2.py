#!/usr/bin/env python3
"""
GPIO Multi-Button with Working MQTT - Version 2 with Config File
Supports multiple buttons with different actions using external config
"""

import lgpio
import time
import sys
import paho.mqtt.client as mqtt
import json
from button_config import BUTTONS, MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD, GPIO_CHIP, POLLING_RATE, DEBOUNCE_TIME

# Global variables
chip = None
client = None
button_states = {}

# MQTT client setup
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to MQTT broker!")
        return True
    else:
        print(f"❌ Failed to connect: {rc}")
        return False

def on_publish(client, userdata, mid, reason_code, properties):
    print(f"✅ Message {mid} published successfully!")

def send_button_message(button_name, button_config):
    """Send MQTT message when button is pressed"""
    print(f"🔘 {button_config['description']} pressed! Sending MQTT message...")
    
    try:
        # Create message for this specific button
        message = {
            "action": button_config["action"],
            "button_name": button_name,
            "timestamp": time.time(),
            "source": "gpio_button",
            "device_class": "button",
            "entity_id": button_config.get("entity_id", f"button.{button_name}_gpio"),
            "value": "pressed"
        }
        
        print(f"📝 Message: {json.dumps(message, indent=2)}")
        print(f"📡 Publishing to topic: {button_config['topic']}")
        
        # Publish message
        result = client.publish(button_config["topic"], json.dumps(message), qos=1)
        
        print(f"📤 Publish result: {result}")
        print(f"📤 Return code: {result.rc}")
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"✅ {button_config['description']} message sent!")
            return True
        else:
            print(f"❌ Failed to send {button_name} message: {result.rc}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending {button_name} MQTT message: {e}")
        return False

def setup_gpio_buttons():
    """Setup all GPIO buttons"""
    global chip
    
    print("Opening GPIO...")
    chip = lgpio.gpiochip_open(GPIO_CHIP)
    
    for button_name, config in BUTTONS.items():
        pin = config["pin"]
        try:
            lgpio.gpio_claim_input(chip, pin, lgpio.SET_PULL_UP)
            print(f"✅ {config['description']} - GPIO {pin} claimed successfully!")
            button_states[button_name] = 1  # Initialize as not pressed
        except lgpio.error as e:
            if "GPIO busy" in str(e):
                print(f"GPIO {pin} is busy. Trying to free it first...")
                try:
                    lgpio.gpio_free(chip, pin)
                    lgpio.gpio_claim_input(chip, pin, lgpio.SET_PULL_UP)
                    print(f"✅ {config['description']} - GPIO {pin} claimed on retry!")
                    button_states[button_name] = 1
                except lgpio.error as e2:
                    print(f"❌ Failed to claim GPIO {pin} for {button_name}: {e2}")
            else:
                print(f"❌ GPIO {pin} error for {button_name}: {e}")
    
    return chip

def read_all_buttons():
    """Read all buttons and handle presses"""
    for button_name, config in BUTTONS.items():
        pin = config["pin"]
        try:
            current_state = lgpio.gpio_read(chip, pin)
            last_state = button_states.get(button_name, 1)
            
            # Detect falling edge (button press)
            if current_state == 0 and last_state == 1:
                print(f"\n{'='*60}")
                send_button_message(button_name, config)
                print(f"{'='*60}")
                time.sleep(DEBOUNCE_TIME)  # Debounce
            
            button_states[button_name] = current_state
            
        except Exception as e:
            print(f"❌ Error reading {button_name} button: {e}")

def cleanup():
    """Clean up GPIO and MQTT connections"""
    print("\nCleaning up...")
    
    # Free all GPIO pins
    for button_name, config in BUTTONS.items():
        try:
            lgpio.gpio_free(chip, config["pin"])
            print(f"✅ GPIO {config['pin']} freed")
        except:
            pass
    
    # Close GPIO chip
    try:
        lgpio.gpiochip_close(chip)
        print("✅ GPIO chip closed")
    except:
        pass
    
    # Disconnect MQTT
    try:
        client.loop_stop()
        client.disconnect()
        print("✅ MQTT disconnected")
    except:
        pass
    
    print("✅ Cleanup complete!")

def main():
    """Main function"""
    global client
    
    print("🚀 GPIO Multi-Button MQTT Controller v2 (Config)")
    print("=" * 60)
    
    # Import and display configuration
    from button_config import print_configuration
    print_configuration()
    
    # Setup GPIO buttons
    setup_gpio_buttons()
    
    # Connect to MQTT broker
    print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
    client.on_connect = on_connect
    client.on_publish = on_publish
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        time.sleep(2)  # Wait for connection
    except Exception as e:
        print(f"❌ Failed to connect to MQTT broker: {e}")
        cleanup()
        sys.exit(1)
    
    print(f"\n🔌 Wiring Instructions:")
    for button_name, config in BUTTONS.items():
        print(f"   {config['description']}: Physical Pin {config['pin']} to button, other side to Ground")
    
    print(f"\n📡 MQTT Topics:")
    for button_name, config in BUTTONS.items():
        print(f"   {button_name}: {config['topic']}")
    
    print(f"\n✅ All {len(BUTTONS)} buttons ready! Press any button to send MQTT messages...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            read_all_buttons()
            time.sleep(POLLING_RATE)
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
