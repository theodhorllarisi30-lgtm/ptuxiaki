"""
 - Κεντρικές ρυθμίσεις για το Raspberry.
"""


# CrashDetector Ρυθμίσεις
CRITICAL_JERK = 0.1
CRITICAL_DV = 15.0
CRITICAL_HIC = 2.0
ALPHA = 0.3


# Server Ρυθμίσεις
SERVER_URL = "http://192.168.1.5/crash.php"


# Ρυθμίσεις Λειτουργίας
SAMPLE_DELAY = 0.05      # 50ms = 20Hz
ALERT_COOLDOWN = 10      # Δευτερόλεπτα μεταξύ alerts
BUFFER_SIZE = 100        # Πόσα samples κρατάμε πριν το crash


# GPRS Ρυθμίσεις
GPRS_PORT = "/dev/ttyACM0"
GPRS_BAUDRATE = 9600
GPRS_APN = "internet"  #Ανάλογα με τον πάροχό


# Τρόπος αποστολής: "gprs" ή "wifi"
SEND_METHOD = "gprs"  # Άλλαγή σε "wifi" αν χρειάζεται


# Flame Sensor Ρυθμίσεις
FLAME_ENABLED = True  # False αν δεν έχει υπάρχει αισθητήρας φλόγας
