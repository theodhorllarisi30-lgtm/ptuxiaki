import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix


class CrashDetector:
    def __init__(self, critical_jerk=0.1, critical_dv=15.0, critical_hic=2.0, alpha=0.3):
        """
        Αρχικοποίηση του ανιχνευτή με τις παραμέτρους (Thresholds) που θέλουμε.
        """
        self.critical_jerk = critical_jerk
        self.critical_dv = critical_dv
        self.critical_hic = critical_hic
        self.alpha = alpha

    def _preprocess(self, df):
        """Εσωτερική μέθοδος για το φιλτράρισμα και την εξαγωγή features."""
        df = df.copy()
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        df = df.sort_values("Timestamp").reset_index(drop=True)
        df["dt"] = df["Timestamp"].diff().dt.total_seconds().fillna(0.01)

        # 1. Ψηφιακό Low-Pass Φίλτρο
        df["Acc_X_filt"] = df["Acc_X"].ewm(alpha=self.alpha, adjust=False).mean()
        df["Acc_Y_filt"] = df["Acc_Y"].ewm(alpha=self.alpha, adjust=False).mean()
        df["Acc_Z_filt"] = df["Acc_Z"].ewm(alpha=self.alpha, adjust=False).mean()

        # 2. Jerk ανά άξονα
        df["jerk_x"] = df["Acc_X_filt"].diff().abs().fillna(0) / df["dt"].replace(0, 0.01)
        df["jerk_y"] = df["Acc_Y_filt"].diff().abs().fillna(0) / df["dt"].replace(0, 0.01)
        df["jerk_z"] = df["Acc_Z_filt"].diff().abs().fillna(0) / df["dt"].replace(0, 0.01)

        # 3. ΔV (Οριζόντιο επίπεδο X-Y)
        df["acc_horiz_ms2"] = np.sqrt(df["Acc_X_filt"] ** 2 + df["Acc_Y_filt"] ** 2)
        df["dV_inst"] = df["acc_horiz_ms2"] * df["dt"]
        df["delta_v_kmh"] = df["dV_inst"].rolling(10, min_periods=1).sum() * 3.6

        # 4. HIC Approximation
        WINDOW = 10
        df["hic"] = 0.0
        for i in range(WINDOW, len(df)):
            window = df["acc_horiz_ms2"].iloc[i - WINDOW:i]
            t = df["dt"].iloc[i - WINDOW:i].sum()
            if t > 0:
                df.loc[i, "hic"] = t * (window.mean() ** 2.5)

        # 5. Rolling Stats για το Adaptive Sensitivity
        ROLL = 20
        df["acc_std"] = df["acc_horiz_ms2"].rolling(ROLL).std().fillna(0)
        df["jerk_std"] = df["jerk_x"].rolling(ROLL).std().fillna(0)

        # 6. Adaptive Sensitivity
        speed_factor = df["Speed_kmh"] / 100.0
        smoothness = 1.0 / (1.0 + df["acc_std"] + df["jerk_std"])
        df["sensitivity"] = 1.0 + (0.5 * smoothness) - (0.5 * speed_factor)
        df["sensitivity"] = np.clip(df["sensitivity"], 0.3, 1.8)

        # 7. Adaptive Thresholds
        df["j_thresh"] = self.critical_jerk * df["sensitivity"]

        # =========================================================
        # 8. GPS STUCK DETECTOR
        # =========================================================
        # π.χ Αν η ταχύτητα έχει std < 0.001 σε παράθυρο 5 δειγμάτων,
        # το GPS θεωρείται "κολλημένο".
        gps_rolling_std = df["Speed_kmh"].rolling(window=5, min_periods=3).std().fillna(0)
        df["gps_is_stuck"] = gps_rolling_std < 0.001
        # Εξαίρεση: ταχύτητα 0.0 είναι φυσιολογική (σταματημένο όχημα)
        # Χρησιμοποιούμε > 0.5 για να αποφύγουμε floating point issues
        df["gps_is_stuck"] = df["gps_is_stuck"] & (df["Speed_kmh"] > 0.5)

        return df

    def predict(self, df_raw):
        """Η κύρια μέθοδος"""
        df = self._preprocess(df_raw)

        # 1. Μηχανή Απόφασης
        stage1_jerk = (df["jerk_x"] > df["j_thresh"]) | (df["jerk_y"] > df["j_thresh"])
        dynamic_dv = np.where(df["Speed_kmh"] < 35.0, self.critical_dv * 0.4, self.critical_dv)
        dynamic_hic = np.where(df["Speed_kmh"] < 35.0, self.critical_hic * 0.1, self.critical_hic)

        stage2_dv = df["delta_v_kmh"] > dynamic_dv
        stage3_hic = df["hic"] > dynamic_hic

        is_pothole = (df["jerk_z"] > (df["jerk_x"] * 1.8)) & (df["jerk_z"] > (df["jerk_y"] * 1.8))

        # Αρχική απόφαση της
        imu_match = stage1_jerk & stage2_dv & stage3_hic & (~is_pothole)
        imu_prediction = imu_match.rolling(window=2, min_periods=1).max().fillna(0).astype(int)

        # =========================================================
        # GPS BLOCKER
        # =========================================================
        # Κοιτάμε την ταχύτητα 10 samples (0.2 δευτερόλεπτα) ΜΕΤΑ το συμβάν.
        # Χρησιμοποιούμε shift(-10) για να κοιτάξουμε στο μέλλον.
        # Αν η ταχύτητα είναι > 25 km/h, το όχημα μάλλον κινείται ακόμα.

        # Χρησιμοποιούμε rolling max αντί για single-point lookup
        # για να αποφύγουμε στιγμιαίες πτώσεις ταχύτητας
        future_speed = df["Speed_kmh"].shift(-10).fillna(method='ffill').fillna(0)
        gps_vehicle_still_moving = future_speed > 25.0

        # Αν το GPS είναι κολλημένο, ΔΕΝ εμπιστευόμαστε τον blocker
        # Το gps_is_stuck είναι True όταν η ταχύτητα είναι σταθερή για 5+ δείγματα
        gps_blocker_active = gps_vehicle_still_moving & (~df["gps_is_stuck"])

        # Η τελική πρόβλεψη: GPS blocker ακυρώνει μόνο αν είναι ενεργός
        final_prediction = np.where(gps_blocker_active & (imu_prediction == 1), 0, imu_prediction)

        # Αποθηκεύουμε μερικές χρήσιμες στήλες για debugging
        self._last_df = df
        self._last_imu = imu_prediction
        self._last_gps_blocker = gps_blocker_active

        return final_prediction

    def evaluate(self, df_raw):
        """Μέθοδος για αυτόματη αξιολόγηση"""
        predictions = self.predict(df_raw)

        print("=== CLASSIFICATION REPORT ===")
        print(classification_report(df_raw["Crash_Label"], predictions, target_names=["No Crash", "Crash"],
                                    zero_division=0))
        print("=== CONFUSION MATRIX ===")
        print(confusion_matrix(df_raw["Crash_Label"], predictions))