# 🚗 Crash Detection System

Σχεδιασμός και Υλοποίηση Έξυπνου Συστήματος Ανίχνευσης Τροχαίων Ατυχημάτων με Χρήση Αισθητήρων και Αυτόματη Ειδοποίηση Έκτακτης Ανάγκης

---

## 📋 Περιεχόμενα

1. [Περιγραφή](#-περιγραφή)
2. [Αρχιτεκτονική](#-αρχιτεκτονική)
3. [Δομή Project](#-δομή-project)
4. [Απαιτήσεις Hardware](#-απαιτήσεις-hardware)
5. [Απαιτήσεις Software](#-απαιτήσεις-software)
6. [Οδηγίες Εγκατάστασης](#-οδηγίες-εγκατάστασης)
7. [Οδηγίες Εκτέλεσης](#-οδηγίες-εκτέλεσης)
8. [Test Cases](#-test-cases)
9. [Απόδοση Αλγορίθμου](#-απόδοση-αλγορίθμου)
10. [Ρυθμίσεις](#-ρυθμίσεις)
11. [Troubleshooting](#-troubleshooting)

---

## 📖 Περιγραφή

Το σύστημα ανιχνεύει τροχαία ατυχήματα σε πραγματικό χρόνο χρησιμοποιώντας αισθητήρες χαμηλού κόστους. Ακολουθεί την αρχιτεκτονική **Υποδοχής → Ανάλυσης → Ειδοποίησης → Απεικόνισης**:

1. **Υποδοχής:** Αισθητήρες (επιταχυνσιόμετρο, γυροσκόπιο, GPS) διαβάζουν συνεχώς δεδομένα
2. **Ανάλυσης:** Αλγόριθμος 4 σταδίων (Jerk → ΔV → HIC → GPS) αποφασίζει αν έγινε ατύχημα
3. **Ειδοποίησης:** Τα δεδομένα αποστέλλονται μέσω GPRS ή WiFi σε απομακρυσμένο server
4. **Απεικόνισης:** Web interface εμφανίζει το ατύχημα σε χάρτη και πίνακα

---

## 🏗️ Αρχιτεκτονική
```
ΟΧΗΜΑ (Raspberry Pi)
├── sensor_reader.py ← MPU6050 (I2C) + GPS (UART)
├── crash_detector.py ← 4 στάδια: Jerk → ΔV → HIC → GPS
├── gprs_client.py ← SIM900 (AT commands)
├── flame_sensor.py ← Αισθητήρες φλόγας (thread)
├── alert_client.py ← Αποστολή μέσω WiFi
├── config.py ← Ρυθμίσεις
└── main.py ← Συντονιστής
│
│ HTTP POST (JSON)
▼
SERVER
├── crash.php ← INSERT → MySQL (accident_datat.points)
└── index.php ← SELECT → Χάρτης (Leaflet.js) + Πίνακας
```
---

## 📁 Δομή Project
```
project/
├── raspberry/ # Κώδικας για το Raspberry Pi (στο όχημα)
│ ├── main.py # Συντονιστής — το τρέχεις
│ ├── config.py # Όλες οι ρυθμίσεις σε ένα μέρος
│ ├── sensor_reader.py # Ανάγνωση MPU6050 + GPS
│ ├── crash_detector.py # Αλγόριθμος 4 σταδίων
│ ├── alert_client.py # Αποστολή alert μέσω WiFi
│ ├── gprs_client.py # Αποστολή alert μέσω GPRS (SIM900)
│ └── flame_sensor.py # Ανίχνευση φωτιάς (thread)
│
├── server/ # Κώδικας για τον Apache Server
│ ├── crash.php # Endpoint — δέχεται POST JSON → MySQL
│ └── index.php # Web interface — χάρτης + πίνακας
│
├── desktop/ # Κώδικας για ανάπτυξη & testing
│ ├── algorithm.py # Ο αλγόριθμος (για CSV tests)
│ ├── Tests.py # Τρέχει τον αλγόριθμο σε datasets
│ └── test_end_to_end.py # Τεστ όλης της αλυσίδας
│
├── database/ # Βάση δεδομένων
│ └── schema.sql # SQL script για δημιουργία της βάσης
│
└── README.md # Αυτό το αρχείο
```
---

## 🔧 Απαιτήσεις Hardware

### Για το Raspberry Pi (όχημα)

| Υλικό | Μοντέλο | Σκοπός |
|-------|---------|--------|
| Raspberry Pi | 3B+ ή νεότερο | Κεντρική μονάδα επεξεργασίας |
| MPU6050 | GY-521 | Επιταχυνσιόμετρο + Γυροσκόπιο |
| GPS Module | NEO-6M ή παρόμοιο | Στίγμα και ταχύτητα |
| GPRS Module | SIM900 | Αποστολή δεδομένων μέσω κινητής |
| Αισθητήρες φλόγας | KY-026 (×5) | Ανίχνευση φωτιάς (προαιρετικό) |
| SIM κάρτα | Data enabled | Για το GPRS module |
| Καλώδια | Dupont | Συνδεσμολογία |

### Συνδεσμολογία
MPU6050:
VCC → 3.3V
GND → GND
SCL → GPIO 3 (SCL)
SDA → GPIO 2 (SDA)

GPS (NEO-6M):
VCC → 5V
GND → GND
TX → GPIO 15 (RX)
RX → GPIO 14 (TX)

SIM900:
VCC → 5V (εξωτερική τροφοδοσία)
GND → GND
TX → GPIO 15 (RX) — ή USB
RX → GPIO 14 (TX) — ή USB

Flame Sensors (×5):
VCC → 3.3V
GND → GND
DO → GPIO 17, 27, 22, 5, 6

---

## 💻 Απαιτήσεις Software

### Raspberry Pi

```bash
# Python 3.x
sudo apt update
sudo apt install python3-pip

# Python libraries
pip install smbus2 pynmea2 requests pandas numpy RPi.GPIO

# Ενεργοποίηση I2C
sudo raspi-config
# → Interfacing Options → I2C → Enable

# Ενεργοποίηση UART
sudo raspi-config
# → Interface Options → Serial Port → Login shell over serial? → No → Enable serial hardware? → Yes
---

Server (Laptop ή VPS)
- Apache HTTP Server (XAMPP ή LAMP)
- PHP 7.4+
- MySQL 5.7+ ή MariaDB
- phpMyAdmin (προαιρετικό)

---

🚀 Οδηγίες Εγκατάστασης

1. Server — Βάση Δεδομένων
# Τρόπος Α: Μέσω command line
mysql -u root -p < database/schema.sql

# Τρόπος Β: Μέσω phpMyAdmin
# 1. Άνοιξε http://localhost/phpmyadmin
# 2. Πήγαινε στην καρτέλα "SQL"
# 3. Κάνε copy-paste το περιεχόμενο του database/schema.sql
# 4. Πάτα "Εκτέλεση"

2. Server — PHP Αρχεία
# Αντέγραψε τα PHP αρχεία στον φάκελο του Apache
cp server/crash.php /var/www/html/
cp server/index.php /var/www/html/

# Ή για XAMPP (Windows)
# Αντιγράψτε τα στο C:\xampp\htdocs\

3. Raspberry Pi — Κώδικας
# Αντέγραψε όλα τα αρχεία από τον φάκελο raspberry/ στο Raspberry
scp raspberry/*.py pi@raspberrypi:/home/pi/crash_system/

# Μπες στο Raspberry και πήγαινε στον φάκελο
ssh pi@raspberrypi
cd /home/pi/crash_system/

4. Ρύθμιση του config.py
# Άνοιξε το config.py και άλλαξε:
SERVER_URL = "http://Η_IP_TOY_SERVER/crash.php"  # Π.χ. http://192.168.1.100/crash.php
GPRS_APN = "internet"  # Το APN του παρόχου κινητής σου
SEND_METHOD = "wifi"    # "wifi" για δοκιμές, "gprs" για κανονική χρήση

---

Οδηγίες Εκτέλεσης

Raspberry Pi
cd /home/pi/crash_system/
python main.py


Server — Web Interface
στο browser:
http://Η_IP_TOY_SERVER/index.php

---


Test Cases

1. End-to-End
cd Desktop/
# Άλλαξε το SERVER_URL στο test_end_to_end.py
python test_end_to_end.py

2. Αλγόριθμος σε Dataset
cd Desktop/
# Τοποθέτησε το dataset CSV στον ίδιο φάκελο
python Tests.py


## ⚙️ Ρυθμίσεις (config.py)

Όλες οι παράμετροι του συστήματος βρίσκονται στο `raspberry/config.py`.

| Παράμετρος | Τιμή | Περιγραφή |
|-----------|------|-----------|
| `CRITICAL_JERK` | `0.1` | Κατώφλι Jerk (m/s³) |
| `CRITICAL_DV` | `15.0` | Κατώφλι Δέλτα-V (km/h) |
| `CRITICAL_HIC` | `2.0` | Κατώφλι HIC |
| `ALPHA` | `0.3` | Συντελεστής εξομάλυνσης EMA φίλτρου |
| `SERVER_URL` | `"http://x.x.x.x/I.N.S/crash.php"` | URL του server endpoint |
| `SEND_METHOD` | `"gprs"` ή `"wifi"` | Τρόπος αποστολής δεδομένων |
| `SAMPLE_DELAY` | `0.05` | Καθυστέρηση μεταξύ δειγμάτων (20 Hz) |
| `BUFFER_SIZE` | `100` | Αριθμός δειγμάτων στο buffer |
| `ALERT_COOLDOWN` | `10` | Ελάχιστα δευτερόλεπτα μεταξύ alerts |
| `GPRS_PORT` | `"/dev/ttyACM0"` | Σειριακή θύρα του SIM900 |
| `GPRS_BAUDRATE` | `9600` | Baud rate για το SIM900 |
| `GPRS_APN` | `"internet"` | APN παρόχου κινητής τηλεφωνίας |
| `FLAME_ENABLED` | `True` ή `False` | Ενεργοποίηση αισθητήρων φλόγας |
| `DRIVER_NAME` | `"Petros"` | Όνομα οδηγού (αποστέλλεται στον server) |
| `LICENSE_PLATE` | `"ABC-1234"` | Πινακίδα οχήματος |

---

## 🔧 Troubleshooting

| Πρόβλημα | Πιθανή λύση |
|----------|-------------|
| `ModuleNotFoundError: No module named 'smbus2'` | `pip install smbus2` |
| `ModuleNotFoundError: No module named 'pynmea2'` | `pip install pynmea2` |
| `ModuleNotFoundError: No module named 'requests'` | `pip install requests` |
| `ModuleNotFoundError: No module named 'RPi.GPIO'` | `pip install RPi.GPIO` (μόνο σε Raspberry Pi) |
| Το GPS δεν δίνει στίγμα | Βγες σε ανοιχτό χώρο, έλεγξε την κεραία GPS |
| Το SIM900 δεν απαντάει (`AT` → timeout) | Έλεγξε τροφοδοσία (θέλει 2A), δοκίμασε baudrate 115200 |
| Το SIM900 δεν συνδέεται στο δίκτυο | Έλεγξε το APN στο `config.py`, επιβεβαίωσε ότι η SIM έχει δεδομένα |
| `crash.php` επιστρέφει 404 | Το αρχείο δεν είναι στον σωστό φάκελο (πρέπει `htdocs/`) |
| `crash.php` επιστρέφει 500 | Έλεγξε τα credentials της MySQL στο `crash.php` |
| `Column 'latitude' cannot be null` | Το JSON δεν παραδίδεται σωστά — έλεγξε το `SERVER_URL` |
| `index.php` δεν εμφανίζει πινέζες | Έλεγξε ότι η βάση `accident_data` υπάρχει και έχει δεδομένα |
| Ο Apache δεν ξεκινάει | `sudo service apache2 start` (Linux) ή άνοιξε το XAMPP Control Panel (Windows) |
| Το Raspberry δεν έχει I2C | `sudo raspi-config` → Interfacing Options → I2C → Enable |
| `Permission denied: /dev/ttyACM0` | `sudo chmod 666 /dev/ttyACM0` ή πρόσθεσε τον χρήστη στο group `dialout` |
| Τα test δεν βρίσκουν τα datasets | Τοποθέτησε τα αρχεία `road_accident_imu_dataset_8000.csv`, `Driver_Behavior.csv`, `synthetic_dataset__.csv` στον φάκελο `Desktop/` |



Συγγραφέας
Theodhor Llarisi  — Πτυχιακή Εργασία


