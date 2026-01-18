from machine import Pin, time_pulse_us
import time
import usmtp

# --- EMAIL SETTINGS ---
SENDER_EMAIL = "..........."
SENDER_PASSWORD = ".........."  # 16-character app password
RECIPIENTS = [".........", ".........."]

# --- PIN SETUP ---
trig = Pin(5, Pin.OUT)
echo = Pin(18, Pin.IN)

buzzer = Pin(15, Pin.OUT, value=1)

rain_sensor = Pin(4, Pin.IN)
fire_sensor = Pin(2, Pin.IN, Pin.PULL_UP)
smoke_sensor = Pin(34, Pin.IN)  # Analog pin (ESP32)

# --- DISTANCE FUNCTION ---
def get_dist():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    duration = time_pulse_us(echo, 1, 30000)

    if duration < 0:
        return 100

    return (duration / 2) / 29.1

# --- EMAIL ALERT FUNCTION ---
def send_alert(sensor_name):
    print("Connecting to Gmail server...")
    try:
        smtp = usmtp.SMTP('smtp.gmail.com', 587, ssl=False)
        smtp.starttls()
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)

        subject = "SECURITY ALERT: " + sensor_name
        content = "Warning! The {} has been triggered at your home.".format(sensor_name)
        message = "Subject: {}\n\n{}".format(subject, content)

        for email in RECIPIENTS:
            smtp.send_mail(SENDER_EMAIL, email, message)

        smtp.quit()
        print("Email sent successfully!")

    except Exception as e:
        print("Failed to send email:", e)

# --- STARTUP ---
print("--- FULL SECURITY SYSTEM ONLINE ---")
print("Warming up smoke sensor... please wait.")
time.sleep(2)

# --- MAIN LOOP ---
while True:

    # 1. SMOKE CHECK
    if smoke_sensor.value() == 0:
        print("!!! WARNING: SMOKE / GAS DETECTED !!!")
        buzzer.value(0)
        time.sleep(0.05)
        buzzer.value(1)
        time.sleep(0.05)
        send_alert("Smoke / Gas detected")
        time.sleep(3)

    # 2. FIRE CHECK
    if fire_sensor.value() == 1:
        print("!!! ALERT: FIRE DETECTED !!!")
        buzzer.value(0)
        time.sleep(0.2)
        buzzer.value(1)
        send_alert("Fire detected")
        time.sleep(3)

    # 3. RAIN CHECK
    if rain_sensor.value() == 0:
        print("Rain detected.")
        buzzer.value(0)
        time.sleep(0.5)
        buzzer.value(1)

    # 4. DISTANCE CHECK
    d = get_dist()

    if 20 < d < 50:
        print("Distance: {:.1f} cm".format(d))
        buzzer.value(0)
        time.sleep(0.02)
        buzzer.value(1)
        time.sleep(d / 500)

    elif d < 10:
        print("!!! OBJECT TOO CLOSE !!!")
        send_alert("Intruder too close")
        time.sleep(3)

    time.sleep(0.1)
