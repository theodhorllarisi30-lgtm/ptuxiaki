"""
main.py - Συντονιστής: Διαβάζει αισθητήρες → Ελέγχει για crash → Στέλνει alert.
Υποστηρίζει Crash Detection + Flame Detection σε παράλληλο thread.
"""

import time
import json
import pandas as pd
from datetime import datetime

from config import (
    CRITICAL_JERK, CRITICAL_DV, CRITICAL_HIC, ALPHA,
    SERVER_URL, SAMPLE_DELAY, BUFFER_SIZE,
    DRIVER_NAME, LICENSE_PLATE,
    GPRS_PORT, GPRS_BAUDRATE, GPRS_APN, SEND_METHOD,
    FLAME_ENABLED
)
from sensor_reader import SensorReader
from crash_detector import CrashDetector
from alert_client import AlertClient
from gprs_client import GPRSClient
from flame_sensor import FlameSensor


# =========================================================
# Global μεταβλητές για πρόσβαση από την callback του FlameSensor
# =========================================================
gps_data_for_flame = {"Latitude": 0.0, "Longitude": 0.0, "Speed_kmh": 0.0}


def send_alert_via_gprs(gprs, server_url, prediction, last_sample, accident_type="crash"):
    """Στέλνει alert χρησιμοποιώντας το GPRS module."""
    payload = {
        "latitude": last_sample["Latitude"],
        "longitude": last_sample["Longitude"],
        "altitude": 0.0,
        "speed": last_sample["Speed_kmh"],
        "fullname": DRIVER_NAME,
        "license_plate": LICENSE_PLATE,
        "accident": accident_type,
        "timestamp": str(last_sample["Timestamp"])
    }
    
    response = gprs.http_post(server_url, json.dumps(payload))
    
    if response and "OK" in response:
        print(f"Alert sent via GPRS! ({accident_type})")
        return True
    else:
        print("GPRS alert failed")
        return False


def send_flame_alert():
    """Καλείται από το FlameSensor όταν ανιχνευθεί φωτιά."""
    global gps_data_for_flame
    
    print("Αποστολή alert φωτιάς...")
    
    last_sample = {
        "Latitude": gps_data_for_flame["Latitude"],
        "Longitude": gps_data_for_flame["Longitude"],
        "Speed_kmh": gps_data_for_flame["Speed_kmh"],
        "Timestamp": datetime.utcnow()
    }
    
    if SEND_METHOD == "gprs" and gprs:
        send_alert_via_gprs(gprs, SERVER_URL, 1, last_sample, accident_type="flame")
    else:
        alert.send_alert(
            prediction=1,
            latitude=last_sample["Latitude"],
            longitude=last_sample["Longitude"],
            speed=last_sample["Speed_kmh"],
            timestamp=last_sample["Timestamp"],
            fullname=DRIVER_NAME,
            license_plate=LICENSE_PLATE
        )
    
    print("Location sent for flame!")


def main():
    global gprs, alert, gps_data_for_flame
    gprs = None
    alert = None
    
    print("=" * 50)
    print("CRASH & FLAME DETECTION SYSTEM")
    print("=" * 50)
    
    # =========================================================
    # 1. Αρχικοποίηση όλων των components
    # =========================================================
    
    sensor = SensorReader()
    detector = CrashDetector(
        critical_jerk=CRITICAL_JERK,
        critical_dv=CRITICAL_DV,
        critical_hic=CRITICAL_HIC,
        alpha=ALPHA
    )
    
    # Ανάλογα με το SEND_METHOD, αρχικοποιούμε το σωστό client
    if SEND_METHOD == "gprs":
        gprs = GPRSClient(port=GPRS_PORT, baudrate=GPRS_BAUDRATE, apn=GPRS_APN)
        if not gprs.connect():
            print("Cannot connect GPRS. Exiting.")
            return
        alert = AlertClient(SERVER_URL)
    else:
        gprs = None
        alert = AlertClient(SERVER_URL)
    
    # Εκκίνηση FlameSensor σε ξεχωριστό thread
    flame_sensor = None
    if FLAME_ENABLED:
        flame_sensor = FlameSensor(callback=send_flame_alert)
        flame_sensor.start()
    
    print("Όλα τα components είναι έτοιμα!")
    print(f"Server: {SERVER_URL}")
    print(f"Send method: {SEND_METHOD}")
    print(f"Flame Sensor: {'ENABLED' if FLAME_ENABLED else 'DISABLED'}")
    print(f"Ρυθμός δειγματοληψίας: {1/SAMPLE_DELAY:.0f} Hz")
    print("\nΞεκινάω παρακολούθηση...\n")
    
    # =========================================================
    # 2. Buffer για τα τελευταία Ν δείγματα
    # =========================================================
    data_buffer = []
    
    try:
        while True:
            # -------------------------------------------------
            # Βήμα Α: Διαβάζει δεδομένα από αισθητήρες
            # -------------------------------------------------
            sample = sensor.read_sample()
            data_buffer.append(sample)
            
            # Ενημερώνει το GPS για το FlameSensor
            gps_data_for_flame = {
                "Latitude": sample["Latitude"],
                "Longitude": sample["Longitude"],
                "Speed_kmh": sample["Speed_kmh"]
            }
            
            # Κρατάει μόνο τα τελευταία BUFFER_SIZE δείγματα
            if len(data_buffer) > BUFFER_SIZE:
                data_buffer.pop(0)
            
            # -------------------------------------------------
            # Βήμα Β: Τρέχει τον CrashDetector
            # -------------------------------------------------
            df = pd.DataFrame(data_buffer)
            prediction = detector.predict(df)
            
            # Παίρνει την τελευταία πρόβλεψη
            last_prediction = prediction[-1] if len(prediction) > 0 else 0
            
            # -------------------------------------------------
            # Βήμα Γ: Αν βρέθηκε crash, στείλνει alert
            # -------------------------------------------------
            if last_prediction == 1:
                print(f"\nCRASH DETECTED! {datetime.utcnow()}")
                
                last_sample = data_buffer[-1]
                
                if SEND_METHOD == "gprs" and gprs:
                    success = send_alert_via_gprs(gprs, SERVER_URL, 1, last_sample)
                else:
                    success = alert.send_alert(
                        prediction=1,
                        latitude=last_sample["Latitude"],
                        longitude=last_sample["Longitude"],
                        speed=last_sample["Speed_kmh"],
                        timestamp=last_sample["Timestamp"],
                        fullname=DRIVER_NAME,
                        license_plate=LICENSE_PLATE
                    )
                
                if success:
                    print(f"Location: {last_sample['Latitude']:.4f}, {last_sample['Longitude']:.4f}")
            
            # -------------------------------------------------
            # Βήμα Δ: Αναμονή για το επόμενο δείγμα
            # -------------------------------------------------
            time.sleep(SAMPLE_DELAY)
            
    except KeyboardInterrupt:
        print("\n\nΤερματισμός...")
    finally:
        if flame_sensor:
            flame_sensor.stop()
        if gprs:
            gprs.disconnect()
        sensor.close()
        print("Τελος!")


if __name__ == "__main__":
    main()