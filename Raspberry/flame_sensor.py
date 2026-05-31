"""
flame_sensor.py - Παρακολουθεί αισθητήρες φλόγας σε ξεχωριστό thread.
Μόλις ανιχνευθεί φωτιά, καλεί την αποστολή alert.
"""

import RPi.GPIO as GPIO
import time
import threading


class FlameSensor:
    """
    Παρακολουθεί πολλαπλούς αισθητήρες φλόγας.
    Τρέχει σε ξεχωριστό thread για άμεση απόκριση.
    """
    
    # Τα GPIO pins για τους αισθητήρες φλόγας
    FLAME_PINS = [17, 27, 22, 5, 6]
    
    def __init__(self, callback):
        """
        Args:
            callback: Συνάρτηση που καλείται όταν ανιχνευθεί φωτιά.
                      Π.χ. η send_flame_alert από το main.py
        """
        self.callback = callback
        self.is_running = False
        self.thread = None
        
        # Αρχικοποίηση GPIO
        GPIO.setmode(GPIO.BCM)
        for pin in self.FLAME_PINS:
            GPIO.setup(pin, GPIO.IN)
        
        print(f"FlameSensor έτοιμος σε {len(self.FLAME_PINS)} pins: {self.FLAME_PINS}")
    
    def _monitor_loop(self):
        """Εσωτερικός βρόχος που τρέχει στο thread."""
        self.is_running = True
        
        while self.is_running:
            # Έλεγχος όλων των pins — αν έστω ένα δει φλόγα
            flame_detected = False
            for pin in self.FLAME_PINS:
                if GPIO.input(pin):
                    flame_detected = True
                    break
            
            if flame_detected:
                print("FLAME DETECTED!")
                # Καλεί την callback για να στείλει alert
                if self.callback:
                    self.callback()
                
                # Μικρή παύση για να μην στείλει πολλαπλά alerts
                time.sleep(5)
            
            time.sleep(0.1)  # Έλεγχος κάθε 100ms
    
    def start(self):
        """Ξεκινάει το thread παρακολούθησης."""
        if self.thread is not None:
            print("FlameSensor ήδη τρέχει")
            return
        
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("FlameSensor ξεκίνησε (thread)")
    
    def stop(self):
        """Σταματάει το thread."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("FlameSensor σταμάτησε")