import requests
import json
from datetime import datetime

# =========================================================
# ΡΥΘΜΙΣΕΙΣ — Άλλαξε την IP αν χρειάζεται
# =========================================================
SERVER_URL = "http://192.168.1.5/I.N.S/crash.php"  # Βάλε τη σωστή IP


def test_crash_alert():
    """Στέλνει ένα δοκιμαστικό CRASH alert."""
    payload = {
        "latitude": 37.9838,
        "longitude": 23.7275,
        "altitude": 120.0,
        "speed": 0.0,
        "fullname": "Test Driver",
        "license_plate": "ABC-1234",
        "accident": "crash",
        "timestamp": str(datetime.utcnow())
    }

    print("=" * 50)
    print("ΤΕΣΤ ΑΛΥΣΙΔΑΣ — CRASH ALERT")
    print("=" * 50)
    print(f"Server: {SERVER_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            SERVER_URL,
            json=payload,
            timeout=5
        )
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text.strip()}")

        if response.status_code == 200:
            print("\nΕΠΙΤΥΧΙΑ! Το crash alert στάλθηκε και αποθηκεύτηκε.")
            print("   Άνοιξε το http://[IP]/index.php για να δεις την πινέζα στον χάρτη!")
            return True
        else:
            print(f"\nΑΠΟΤΥΧΙΑ: Ο server επέστρεψε {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"\nΑΠΟΤΥΧΙΑ: Δεν μπορώ να συνδεθώ στον server ({SERVER_URL})")
        print("   Έλεγξε:")
        print("   1. Είναι ο server ανοιχτός;")
        print("   2. Είναι η IP σωστή;")
        print("   3. Είναι το Apache/XAMPP σε λειτουργία;")
        print("   4. Το crash.php είναι στον σωστό φάκελο;")
        return False
    except Exception as e:
        print(f"\nΑΠΟΤΥΧΙΑ: {e}")
        return False


def test_normal_reading():
    """Στέλνει ένα δοκιμαστικό NORMAL alert (όχι crash)."""
    payload = {
        "latitude": 40.6400,
        "longitude": 22.8544,
        "altitude": 50.0,
        "speed": 60.0,
        "fullname": "Normal Driver",
        "license_plate": "XYZ-9999",
        "accident": "no_crash",
        "timestamp": str(datetime.utcnow())
    }

    print("\n" + "=" * 50)
    print("ΤΕΣΤ ΑΛΥΣΙΔΑΣ — NORMAL READING")
    print("=" * 50)
    print(f"Server: {SERVER_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            SERVER_URL,
            json=payload,
            timeout=5
        )
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text.strip()}")

        if response.status_code == 200:
            print("\nΕΠΙΤΥΧΙΑ! Το normal reading στάλθηκε και αποθηκεύτηκε.")
            return True
        else:
            print(f"\nΑΠΟΤΥΧΙΑ: Ο server επέστρεψε {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"\nΑΠΟΤΥΧΙΑ: Δεν μπορώ να συνδεθώ στον server")
        return False
    except Exception as e:
        print(f"\nΑΠΟΤΥΧΙΑ: {e}")
        return False


def test_website():
    """Ελέγχει αν το index.php είναι προσβάσιμο."""
    index_url = SERVER_URL.replace("crash.php", "index.php")

    print("\n" + "=" * 50)
    print("ΤΕΣΤ ΑΛΥΣΙΔΑΣ — WEBSITE")
    print("=" * 50)
    print(f"URL: {index_url}")

    try:
        response = requests.get(index_url, timeout=5)
        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            print("ΕΠΙΤΥΧΙΑ! Το site είναι προσβάσιμο.")
            return True
        else:
            print(f"ΑΠΟΤΥΧΙΑ: {response.status_code}")
            return False
    except:
        print("ΑΠΟΤΥΧΙΑ: Το site δεν απαντά.")
        return False


# =========================================================
# ΤΡΕΞΕ ΟΛΑ ΤΑ ΤΕΣΤ
# =========================================================
if __name__ == "__main__":
    results = []

    results.append(("Crash Alert", test_crash_alert()))
    results.append(("Normal Reading", test_normal_reading()))
    results.append(("Website", test_website()))

    print("\n" + "=" * 50)
    print("ΣΥΝΟΨΗ ΤΕΣΤ")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "" if passed else "❌"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\nΟΛΑ ΤΑ ΤΕΣΤ ΠΕΡΑΣΑΝ!")
        print("   Η αλυσίδα δουλεύει από άκρη σε άκρη:")
        print("   Python → crash.php → MySQL → index.php")
    else:
        print("\nΜΕΡΙΚΑ ΤΕΣΤ ΑΠΕΤΥΧΑΝ. Δες τα μηνύματα παραπάνω.")