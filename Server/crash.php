<?php

//Κάνει εγγραφή στην βάση
$conn = new mysqli("localhost", "root", "", "accident_data");

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$data = json_decode(file_get_contents("php://input"), true);

$latitude = $data["latitude"]?? 0.0;
$longitude = $data["longitude"]?? 0.0;
$altitude = $data["altitude"]?? 0.0;
$fullname = $data["fullname"]?? 0.0;
$license_plate = $data["license_plate"]?? 0.0;
$accident = $data["accident"]?? 0.0;

$date = date("Y-m-d");
$time = date("H:i:s");

$stmt = $conn->prepare("INSERT INTO points 
(latitude, longitude, altitude, date, time, fullname, license_plate, accident) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?)");

$stmt->bind_param("ddssssss",
    $latitude,
    $longitude,
    $altitude,
    $date,
    $time,
    $fullname,
    $license_plate,
    $accident
);

$stmt->execute();

echo "OK";

$stmt->close();
$conn->close();

?>