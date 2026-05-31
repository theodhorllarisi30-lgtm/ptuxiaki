import json
import requests
from datetime import datetime


class AlertClient:
    """
    Υπεύθυνος για την αποστολή δεδομένων ατυχήματος στον server.
    Στέλνει HTTP POST με JSON body.
    """
    
    def __init__(self, server_url):
 
        self.server_url = server_url
        self.last_alert_time = None  # Για αποφυγή duplicate alerts
        self.alert_cooldown = 10  # Δευτερόλεπτα μεταξύ alerts
    
    def send_alert(self, prediction, latitude, longitude, speed, timestamp, fullname="", license_plate=""):
        """
        Στέλνει τα δεδομένα ατυχήματος στον server.
        
        Args:
            prediction: 0 ή 1 (No Crash / Crash)
            latitude, longitude: Συντεταγμένες GPS
            speed: Ταχύτητα σε km/h
            timestamp: Χρονική σήμανση
            fullname: Όνομα οδηγού (προαιρετικό)
            license_plate: Πινακίδα (προαιρετικό)
        
        Returns:
            True αν στάλθηκε επιτυχώς, False αλλιώς
        """
        # Έλεγχος cooldown για αποφυγή duplicate alerts
        now = datetime.utcnow()
        if self.last_alert_time:
            delta = (now - self.last_alert_time).total_seconds()
            if delta < self.alert_cooldown:
                print(f"⏳ Alert suppressed (cooldown: {delta:.1f}s < {self.alert_cooldown}s)")
                return False
        
        # Δημιουργία του payload
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "altitude": 0,  # Καθώς δεν έχω θέλω
            "fullname": fullname,
            "license_plate": license_plate,
            "accident": "crash" if prediction == 1 else "no_crash",
            "speed": speed,
            "timestamp": str(timestamp)
        }
        
        try:
            # HTTP POST με JSON
            response = requests.post(
                self.server_url,
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                self.last_alert_time = now
                print(f"Alert sent! Server response: {response.text.strip()}")
                return True
            else:
                print(f"Server error {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("Cannot connect to server (Connection Error)")
            return False
        except requests.exceptions.Timeout:
            print(" Server timeout")
            return False
        except Exception as e:
            print(f" Error sending alert: {e}")
            return False