"""
gprs_client.py - Στέλνει HTTP POST requests μέσω SIM900 GPRS module.
"""

import serial
import time


class GPRSClient:
    """
    Διαχειρίζεται το SIM900 GPRS module.
    Ανοίγει σύνδεση, στέλνει HTTP POST, κλείνει σύνδεση.
    """
    
    def __init__(self, port="/dev/ttyACM0", baudrate=9600, apn="internet"):
        self.port = port
        self.baudrate = baudrate
        self.apn = apn
        self.ser = None
        self.is_connected = False
    
    def _send_at(self, command, wait=1):
        """Στέλνει AT command και επιστρέφει την απάντηση."""
        if self.ser is None:
            return "ERROR: Serial not open"
        
        self.ser.write((command + "\r\n").encode())
        time.sleep(wait)
        response = self.ser.read(self.ser.in_waiting).decode("utf-8", errors="ignore")
        return response.strip()
    
    def connect(self):
        """
        Ανοίγει τη σειριακή σύνδεση και ενεργοποιεί το GPRS.
        Επιστρέφει True αν όλα πήγαν καλά.
        """
        print("Opening serial connection to SIM900...")
        
        try:
            self.ser = serial.Serial(self.port, baudrate=self.baudrate, timeout=2)
            time.sleep(1)
        except Exception as e:
            print(f"Cannot open serial port: {e}")
            return False
        
        # 1. Βασικό τεστ
        response = self._send_at("AT")
        if "OK" not in response:
            print("SIM900 not responding")
            return False
        print("SIM900 responding")
        
        # 2. Έλεγχος SIM
        response = self._send_at("AT+CPIN?")
        if "READY" not in response:
            print("SIM not ready")
            return False
        print("SIM ready")
        
        # 3. Έλεγχος σήματος
        response = self._send_at("AT+CSQ")
        print(f"Signal: {response}")
        
        # 4. Ενεργοποίηση GPRS
        self._send_at("AT+CGATT=1", wait=3)
        
        # 5. Ορισμός APN
        self._send_at(f'AT+CSTT="{self.apn}"')
        
        # 6. Ενεργοποίηση ασύρματης σύνδεσης
        self._send_at("AT+CIICR", wait=3)
        
        # 7. Έλεγχος IP
        response = self._send_at("AT+CIFSR")
        print(f"IP: {response}")
        
        self.is_connected = True
        print("GPRS connected!")
        return True
    
    def http_post(self, url, json_data):
        """
        Στέλνει HTTP POST request μέσω SIM900.
        
        Args:
            url: Το URL (π.χ. "http://123.456.789.0/crash.php")
            json_data: String με το JSON body
        
        Returns:
            Response από τον server ή None αν αποτύχει
        """
        if not self.is_connected:
            print("GPRS not connected")
            return None
        
        import json
        
        # Εξαγωγή host και path από το URL
        url = url.replace("http://", "").replace("https://", "")
        parts = url.split("/", 1)
        host = parts[0]
        path = "/" + parts[1] if len(parts) > 1 else "/"
        
        # Προετοιμασία του HTTP request
        body = json.dumps(json_data) if isinstance(json_data, dict) else json_data
        content_length = len(body)
        
        # 1. Έναρξη TCP σύνδεσης
        response = self._send_at(f'AT+CIPSTART="TCP","{host}","80"', wait=3)
        if "CONNECT OK" not in response and "ALREADY CONNECT" not in response:
            print(f"TCP connection failed: {response}")
            return None
        print("TCP connected")
        
        # 2. Αποστολή HTTP request
        http_request = (
            f"POST {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {content_length}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
            f"{body}"
        )
        
        # το μέγεθος των δεδομένων που θα σταλούν
        self._send_at(f"AT+CIPSEND={len(http_request)}", wait=1)
        time.sleep(0.5)
        
        # Στείλνει το HTTP request
        self.ser.write(http_request.encode())
        time.sleep(3)
        
        # Διαβάζει την απάντηση
        response = self.ser.read(self.ser.in_waiting).decode("utf-8", errors="ignore")
        print(f"📬 Server response:\n{response[:500]}")  # Πρώτα 500 chars
        
        # 3. Κλείσιμο TCP σύνδεσης
        self._send_at("AT+CIPCLOSE", wait=1)
        
        return response
    
    def disconnect(self):
        """Κλείνει τη σύνδεση GPRS και τη σειριακή θύρα."""
        if self.ser:
            self._send_at("AT+CIPSHUT", wait=2)
            self.ser.close()
            self.ser = None
            self.is_connected = False
            print("GPRS disconnected")