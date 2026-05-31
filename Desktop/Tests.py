"""
test_all.py - Τα 10 τεστ αξιολόγησης (ΔΙΟΡΘΩΜΕΝΑ).
Τρέξε το από τον υπολογιστή σου.
"""

import pandas as pd
import numpy as np
from algorithm import CrashDetector
from sklearn.metrics import classification_report, confusion_matrix

# =========================================================
# ΤΕΣΤ 1: ΒΑΣΙΚΗ ΑΞΙΟΛΟΓΗΣΗ (ORIGINAL DATASET)
# =========================================================
def test_1_original_dataset():
    print("\n" + "="*60)
    print("ΤΕΣΤ 1: ΒΑΣΙΚΗ ΑΞΙΟΛΟΓΗΣΗ (8.000 samples)")
    print("="*60)
    df = pd.read_csv("road_accident_imu_dataset_8000.csv")
    detector = CrashDetector()
    df["Prediction"] = detector.predict(df)
    print(classification_report(df["Crash_Label"], df["Prediction"],
          labels=[0, 1], target_names=["No Crash", "Crash"], zero_division=0))
    cm = confusion_matrix(df["Crash_Label"], df["Prediction"], labels=[0, 1])
    print("Confusion Matrix:")
    print(cm)
    tn, fp, fn, tp = cm.ravel()
    print(f"Recall: {tp/(tp+fn)*100:.1f}% | Precision: {tp/(tp+fp)*100:.1f}% | F1: {2*(tp/(tp+fp)*tp/(tp+fn))/(tp/(tp+fp)+tp/(tp+fn)):.2f}")

# =========================================================
# ΤΕΣΤ 2: ΓΕΝΙΚΕΥΣΗ
# =========================================================
def test_2_synthetic():
    print("\n" + "=" * 60)
    print("ΤΕΣΤ 2: ΓΕΝΙΚΕΥΣΗ (Synthetic Dataset)")
    print("=" * 60)
    df = pd.read_csv("synthetic_dataset__.csv")
    detector = CrashDetector()
    df["Prediction"] = detector.predict(df)
    print(classification_report(df["Crash_Label"], df["Prediction"],
                                labels=[0, 1], target_names=["No Crash", "Crash"], zero_division=0))
    cm = confusion_matrix(df["Crash_Label"], df["Prediction"], labels=[0, 1])
    print("Confusion Matrix:")
    print(cm)
    tn, fp, fn, tp = cm.ravel()
    print(
        f"Recall: {tp / (tp + fn) * 100:.1f}% | Precision: {tp / (tp + fp) * 100:.1f}% | F1: {2 * (tp / (tp + fp) * tp / (tp + fn)) / (tp / (tp + fp) + tp / (tp + fn)):.2f}")


# =========================================================
# ΤΕΣΤ 3: LOW-SPEED CRASH
# =========================================================
def test_3_low_speed():
    print("\n" + "=" * 60)
    print("ΤΕΣΤ 3: LOW-SPEED CRASH (<15 km/h)")
    print("=" * 60)
    np.random.seed(42)
    n = 200;
    t = pd.date_range("2025-01-01", periods=n, freq="20ms")
    s = np.ones(n) * 12;
    ax = np.random.normal(0, 0.02, n);
    ay = np.random.normal(0, 0.02, n);
    az = np.random.normal(9.8, 0.02, n)
    labels = np.zeros(n)
    for i in range(60, 85):
        ax[i] = -10.0 + np.random.normal(0, 1.5);
        ay[i] = np.random.normal(0, 1.5)
        az[i] = 12.0 + np.random.normal(0, 0.8);
        s[i] = max(0, s[i - 1] - 2.5)
    labels[60:85] = 1
    for i in range(85, n): s[i] = 0
    df = pd.DataFrame({"Timestamp": t, "Acc_X": ax, "Acc_Y": ay, "Acc_Z": az,
                       "Gyro_X": 0, "Gyro_Y": 0, "Gyro_Z": 0, "Speed_kmh": s,
                       "Latitude": 0, "Longitude": 0, "Motion_Intensity": 0, "Crash_Label": labels})
    detector = CrashDetector()
    df["Pred"] = detector.predict(df)
    print(f"Crash detected: {df['Pred'].iloc[60:85].sum()}/25 samples")


# =========================================================
# ΤΕΣΤ 4: ΛΑΚΚΟΥΒΑ + ΦΡΕΝΑΡΙΣΜΑ
# =========================================================
def test_4_pothole():
    print("\n" + "=" * 60)
    print("ΤΕΣΤ 4: ΛΑΚΚΟΥΒΑ & ΑΠΟΤΟΜΟ ΦΡΕΝΑΡΙΣΜΑ")
    print("=" * 60)
    np.random.seed(42)
    n = 200;
    t = pd.date_range("2025-01-01", periods=n, freq="20ms")
    s = np.ones(n) * 50;
    ax = np.random.normal(0, 0.02, n);
    ay = np.random.normal(0, 0.02, n);
    az = np.random.normal(9.8, 0.02, n)
    labels = np.zeros(n)
    for i in range(50, 60): ax[i] = np.random.normal(0, 1.0); ay[i] = np.random.normal(0, 1.0); az[
        i] = 22.0 + np.random.normal(0, 4.0)
    for i in range(120, 135):
        ax[i] = -7.0 + np.random.normal(0, 0.8);
        ay[i] = np.random.normal(0, 0.8)
        az[i] = 9.8 + np.random.normal(0, 0.3);
        s[i] = max(25, s[i - 1] - 3)
    for i in range(135, n): s[i] = 35
    df = pd.DataFrame({"Timestamp": t, "Acc_X": ax, "Acc_Y": ay, "Acc_Z": az,
                       "Gyro_X": 0, "Gyro_Y": 0, "Gyro_Z": 0, "Speed_kmh": s,
                       "Latitude": 0, "Longitude": 0, "Motion_Intensity": 0, "Crash_Label": labels})
    detector = CrashDetector()
    df["Pred"] = detector.predict(df)
    print(f"False Positives: {df['Pred'].iloc[50:65].sum()} (λακκούβα) | {df['Pred'].iloc[120:150].sum()} (φρενάρισμα)")

# =========================================================
# ΤΕΣΤ 5: ΠΛΕΥΡΙΚΗ ΣΥΓΚΡΟΥΣΗ
# =========================================================
def test_5_side():
    print("\n" + "=" * 60)
    print("ΤΕΣΤ 5: ΠΛΕΥΡΙΚΗ ΣΥΓΚΡΟΥΣΗ")
    print("=" * 60)
    np.random.seed(42)
    n = 200;
    t = pd.date_range("2025-01-01", periods=n, freq="20ms")
    s = np.ones(n) * 40;
    ax = np.random.normal(0, 0.02, n);
    ay = np.random.normal(0, 0.02, n);
    az = np.random.normal(9.8, 0.02, n)
    labels = np.zeros(n)
    for i in range(60, 85):
        ax[i] = np.random.normal(0, 1.5);
        ay[i] = -14.0 + np.random.normal(0, 3.0)
        az[i] = 13.0 + np.random.normal(0, 1.5);
        s[i] = max(0, s[i - 1] - 4)
    labels[60:85] = 1
    for i in range(85, n): s[i] = 0
    df = pd.DataFrame({"Timestamp": t, "Acc_X": ax, "Acc_Y": ay, "Acc_Z": az,
                       "Gyro_X": 0, "Gyro_Y": 0, "Gyro_Z": 0, "Speed_kmh": s,
                       "Latitude": 0, "Longitude": 0, "Motion_Intensity": 0, "Crash_Label": labels})
    detector = CrashDetector()
    df["Pred"] = detector.predict(df)
    print(f"Crash detected: {df['Pred'].iloc[60:85].sum()}/25 samples")

# =========================================================
# ΤΕΣΤ 6: ΓΛΙΣΤΡΗΜΑ
# =========================================================
def test_6_slippery():
    print("\n" + "=" * 60)
    print("ΤΕΣΤ 6: ΓΛΙΣΤΡΗΜΑ (ΠΑΓΟΣ/ΝΕΡΟ)")
    print("=" * 60)
    np.random.seed(42)
    n = 200;
    t = pd.date_range("2025-01-01", periods=n, freq="20ms")
    s = np.ones(n) * 50;
    ax = np.random.normal(0, 0.02, n);
    ay = np.random.normal(0, 0.02, n);
    az = np.random.normal(9.8, 0.02, n)
    labels = np.zeros(n)
    for i in range(40, 60): ax[i] = np.random.normal(0, 0.02); ay[i] = np.random.normal(0, 0.02); az[
        i] = 9.8 + np.random.normal(0, 0.02); s[i] = max(45, s[i - 1] - 0.5)
    for i in range(60, 85):
        ax[i] = -16.0 + np.random.normal(0, 2.5);
        ay[i] = np.random.normal(0, 2.5)
        az[i] = 13.0 + np.random.normal(0, 1.5);
        s[i] = max(0, s[i - 1] - 5)
    labels[60:85] = 1
    for i in range(85, n): s[i] = 0
    df = pd.DataFrame({"Timestamp": t, "Acc_X": ax, "Acc_Y": ay, "Acc_Z": az,
                       "Gyro_X": 0, "Gyro_Y": 0, "Gyro_Z": 0, "Speed_kmh": s,
                       "Latitude": 0, "Longitude": 0, "Motion_Intensity": 0, "Crash_Label": labels})
    detector = CrashDetector()
    df["Pred"] = detector.predict(df)
    print(f"Recall: {df['Pred'].iloc[60:85].sum() / 25 * 100:.0f}%")

# =========================================================
# ΤΕΣΤ 7: ΑΛΛΕΠΑΛΛΗΛΑ ΓΕΓΟΝΟΤΑ
# =========================================================
def test_7_multiple():
    print("\n" + "=" * 60)
    print("ΤΕΣΤ 7: ΑΛΛΕΠΑΛΛΗΛΑ ΓΕΓΟΝΟΤΑ")
    print("=" * 60)
    np.random.seed(42)
    n = 250;
    t = pd.date_range("2025-01-01", periods=n, freq="20ms")
    s = np.ones(n) * 50;
    ax = np.random.normal(0, 0.02, n);
    ay = np.random.normal(0, 0.02, n);
    az = np.random.normal(9.8, 0.02, n)
    labels = np.zeros(n)
    for i in range(50, 60): ax[i] = -8.0 + np.random.normal(0, 0.5); s[i] = max(20, s[i - 1] - 3)
    for i in range(60, 85): ax[i] = np.random.normal(0, 0.03); s[i] = 30
    for i in range(85, 110):
        ax[i] = -16.0 + np.random.normal(0, 2.5);
        ay[i] = np.random.normal(0, 2.5)
        az[i] = 13.0 + np.random.normal(0, 1.5);
        s[i] = max(0, s[i - 1] - 5)
    labels[85:110] = 1
    for i in range(110, n): s[i] = 0
    df = pd.DataFrame({"Timestamp": t, "Acc_X": ax, "Acc_Y": ay, "Acc_Z": az,
                       "Gyro_X": 0, "Gyro_Y": 0, "Gyro_Z": 0, "Speed_kmh": s,
                       "Latitude": 0, "Longitude": 0, "Motion_Intensity": 0, "Crash_Label": labels})
    detector = CrashDetector()
    df["Pred"] = detector.predict(df)
    print(f"False Positives: {df['Pred'].iloc[50:85].sum()} | False Negatives: {25 - df['Pred'].iloc[85:110].sum()}")

# =========================================================
# ΤΕΣΤ 8: ΤΟΥΝΕΛ
# =========================================================
def test_8_tunnel():
    print("\n" + "=" * 60)
    print("ΤΕΣΤ 8: ΤΟΥΝΕΛ (ΑΠΩΛΕΙΑ GPS)")
    print("=" * 60)
    np.random.seed(123)
    n = 200;
    t = pd.date_range("2025-01-01", periods=n, freq="20ms")
    s = np.ones(n) * 60;
    ax = np.random.normal(0, 0.02, n);
    ay = np.random.normal(0, 0.02, n);
    az = np.random.normal(9.8, 0.02, n)
    labels = np.zeros(n)
    for i in range(60, 90):
        ax[i] = -22.0 + np.random.normal(0, 3.0);
        ay[i] = np.random.normal(0, 3.0)
        az[i] = 16.0 + np.random.normal(0, 2.0);
        s[i] = 60
    labels[60:90] = 1
    df = pd.DataFrame({"Timestamp": t, "Acc_X": ax, "Acc_Y": ay, "Acc_Z": az,
                       "Gyro_X": 0, "Gyro_Y": 0, "Gyro_Z": 0, "Speed_kmh": s,
                       "Latitude": 0, "Longitude": 0, "Motion_Intensity": 0, "Crash_Label": labels})
    detector = CrashDetector()
    df["Pred"] = detector.predict(df)
    print(
        f"Crash detected: {df['Pred'].iloc[60:90].sum()}/30 | GPS blocker active: {detector._last_gps_blocker.iloc[60:90].sum()}/30")

# =========================================================
# ΤΕΣΤ 9: ΕΠΙΚΙΝΔΥΝΗ ΟΔΗΓΗΣΗ (30.000)
# =========================================================
def test_9_risky_a():
    print("\n" + "="*60)
    print("ΤΕΣΤ 9: ΕΠΙΚΙΝΔΥΝΗ ΟΔΗΓΗΣΗ Α (30.000 samples)")
    print("="*60)
    try:
        df = pd.read_csv("Driver_Behavior.csv")
        ad = pd.DataFrame()
        ad["Timestamp"] = pd.date_range("2025-01-01", periods=len(df), freq="20ms")
        ad["Acc_X"] = df["accel_x"]; ad["Acc_Y"] = df["accel_y"]
        ad["Acc_Z"] = 9.8 + np.random.normal(0, 0.1, len(df))
        ad["Speed_kmh"] = df["speed_kmph"]
        ad["Gyro_X"] = ad["Gyro_Y"] = ad["Gyro_Z"] = 0
        ad["Latitude"] = ad["Longitude"] = ad["Motion_Intensity"] = 0
        ad["Crash_Label"] = 0
        detector = CrashDetector()
        ad["Pred"] = detector.predict(ad)
        fp = ad["Pred"].sum()
        print(f"False Positives: {fp}/{len(ad)} ({fp/len(ad)*100:.4f}%)")
    except FileNotFoundError:
        print("Dataset not found. Skipped.")



# =========================================================
# RUN ALL
# =========================================================
if __name__ == "__main__":
    test_1_original_dataset()
    test_2_synthetic()
    test_3_low_speed()
    test_4_pothole()
    test_5_side()
    test_6_slippery()
    test_7_multiple()
    test_8_tunnel()
    test_9_risky_a()
    print("\n" + "="*60)
    print("ΟΛΑ ΤΑ ΤΕΣΤ ΟΛΟΚΛΗΡΩΘΗΚΑΝ")
    print("="*60)
