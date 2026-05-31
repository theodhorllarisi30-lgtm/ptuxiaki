-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Εξυπηρετητής: 127.0.0.1
-- Χρόνος δημιουργίας: 31 Μάη 2026 στις 03:26:50
-- Έκδοση διακομιστή: 10.4.28-MariaDB
-- Έκδοση PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Βάση δεδομένων: `accident_data`
--

-- --------------------------------------------------------

--
-- Δομή πίνακα για τον πίνακα `points`
--

CREATE TABLE `points` (
  `id` int(11) NOT NULL,
  `latitude` double NOT NULL DEFAULT 0,
  `longitude` double NOT NULL DEFAULT 0,
  `altitude` double NOT NULL DEFAULT 0,
  `speed` double NOT NULL DEFAULT 0 COMMENT 'Ταχύτητα σε km/h',
  `date` date NOT NULL,
  `time` time NOT NULL,
  `crash_timestamp` datetime DEFAULT NULL COMMENT 'Πλήρες timestamp από το Raspberry',
  `fullname` varchar(100) NOT NULL DEFAULT 'Unknown' COMMENT 'Όνομα οδηγού',
  `license_plate` varchar(20) NOT NULL DEFAULT 'Unknown' COMMENT 'Πινακίδα',
  `accident` varchar(20) NOT NULL DEFAULT 'no_crash' COMMENT 'crash, flame, ή no_crash',
  `crash_severity` varchar(20) DEFAULT NULL COMMENT 'low, medium, high (προαιρετικό)',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Πότε μπήκε η εγγραφή',
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'Τελευταία τροποποίηση'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Άδειασμα δεδομένων του πίνακα `points`
--

INSERT INTO `points` (`id`, `latitude`, `longitude`, `altitude`, `speed`, `date`, `time`, `crash_timestamp`, `fullname`, `license_plate`, `accident`, `crash_severity`, `created_at`, `updated_at`) VALUES
(1, 37.9838, 23.7275, 120, 0, '2026-05-31', '04:26:27', '2026-05-31 04:26:27', 'Test Driver', 'ABC-1234', 'crash', NULL, '2026-05-31 01:26:27', '2026-05-31 01:26:27'),
(2, 40.64, 22.9444, 50, 60, '2026-05-31', '04:26:27', '2026-05-31 04:26:27', 'Normal Driver', 'XYZ-9999', 'no_crash', NULL, '2026-05-31 01:26:27', '2026-05-31 01:26:27');

--
-- Ευρετήρια για άχρηστους πίνακες
--

--
-- Ευρετήρια για πίνακα `points`
--
ALTER TABLE `points`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_date` (`date`),
  ADD KEY `idx_accident` (`accident`),
  ADD KEY `idx_fullname` (`fullname`);

--
-- AUTO_INCREMENT για άχρηστους πίνακες
--

--
-- AUTO_INCREMENT για πίνακα `points`
--
ALTER TABLE `points`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
