import smbus2
import time
import serial
import pynmea2
from datetime import datetime


class SensorReader:
    """
    Υπεύθυνος για την ανάγνωση όλων των αισθητήρων.
    """
    
    MPU_ADDR = 0x68
    GPS_PORT = "/dev/ttyAMA0"
    GPS_BAUDRATE = 9600
    
    def __init__(self):
        """Αρχικοποίηση όλων των αισθητήρων."""
        self._init_mpu()
        self._init_gps()
        print(" SensorReader έτοιμος (MPU6050 + GPS)")
    
    def _init_mpu(self):
        """Ξυπνάει το MPU6050."""
        self.bus = smbus2.SMBus(1)
        self.bus.write_byte_data(self.MPU_ADDR, 0x6B, 0)  # Wake up
        time.sleep(0.1)  # Χρόνος εκκίνησης
    
    def _init_gps(self):
        """Ανοίγει τη σειριακή σύνδεση με το GPS."""
        try:
            self.gps_serial = serial.Serial(
                self.GPS_PORT, 
                baudrate=self.GPS_BAUDRATE, 
                timeout=1
            )
        except Exception as e:
            print(f"Προειδοποίηση: Το GPS δεν άνοιξε ({e}). Θα επιστρέφει 0.")
            self.gps_serial = None
    
    def _read_mpu_word(self, addr):
        """Διαβάζει 2 bytes από το MPU6050 και τα μετατρέπει σε signed int."""
        high = self.bus.read_byte_data(self.MPU_ADDR, addr)
        low = self.bus.read_byte_data(self.MPU_ADDR, addr + 1)
        val = (high << 8) + low
        if val >= 0x8000:
            val = -((65535 - val) + 1)
        return val
    
    def read_imu(self):
        """
        Διαβάζει επιτάχυνση και γυροσκόπιο από το MPU6050.
        Επιστρέφει: (acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z) σε m/s² και °/s
        """
        # Επιτάχυνση (raw → m/s²)
        acc_x = self._read_mpu_word(0x3B) / 16384.0 * 9.81
        acc_y = self._read_mpu_word(0x3D) / 16384.0 * 9.81
        acc_z = self._read_mpu_word(0x3F) / 16384.0 * 9.81
        
        # Γυροσκόπιο (raw → °/s)
        gyro_x = self._read_mpu_word(0x43) / 131.0
        gyro_y = self._read_mpu_word(0x45) / 131.0
        gyro_z = self._read_mpu_word(0x47) / 131.0
        
        return acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z
    
    def read_gps(self):
        """
        Διαβάζει GPS (GPRMC sentence).
        Επιστρέφει: (latitude, longitude, speed_kmh)
        Αν δεν έχει σήμα, επιστρέφει (None, None, 0.0)
        """
        if self.gps_serial is None:
            return None, None, 0.0
        
        try:
            line = self.gps_serial.readline().decode("utf-8", errors="ignore")
            if line.startswith("$GPRMC"):
                msg = pynmea2.parse(line)
                if msg.status == "A":  # Valid fix
                    lat = float(msg.latitude)
                    lon = float(msg.longitude)
                    speed = float(msg.spd_over_grnd) * 1.852  # knots → km/h
                    return lat, lon, speed
        except Exception:
            pass
        
        return None, None, 0.0
    
    def read_sample(self):
        """
        Η ΚΥΡΙΑ ΜΕΘΟΔΟΣ: Διαβάζει όλους τους αισθητήρες και επιστρέφει
        ένα dictionary με ΟΛΕΣ τις στήλες που χρειάζεται ο CrashDetector.
        """
        timestamp = datetime.utcnow()
        acc_x, acc_y, acc_z, gx, gy, gz = self.read_imu()
        lat, lon, speed = self.read_gps()
        
        return {
            "Timestamp": timestamp,
            "Acc_X": acc_x,
            "Acc_Y": acc_y,
            "Acc_Z": acc_z,
            "Gyro_X": gx,
            "Gyro_Y": gy,
            "Gyro_Z": gz,
            "Speed_kmh": speed if speed else 0.0,
            "Latitude": lat if lat else 0.0,
            "Longitude": lon if lon else 0.0
        }
    
    def close(self):
        """Κλείνει τις συνδέσεις"""
        if self.gps_serial:
            self.gps_serial.close()
        print(" Αισθητήρες έκλεισαν.")