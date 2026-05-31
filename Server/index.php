<!DOCTYPE html>
<html>
<head>
    <title>Crash Detection - Live Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <style>
        #map {  
            height: 50vh;
            width: 90%;
            max-width: 1400px;
            margin: 20px auto;
            border-radius: 20px;
        }
        body {
            background-color: #001F3F;
            font-family: Arial, sans-serif;
        }
        h2 {
            color: white;
            text-align: center;
            margin-top: 20px;
        }
        #table-container {
            width: 90%;
            max-width: 1400px;
            margin: 30px auto;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
            overflow-y: auto;
            max-height: 300px; 
            border-radius: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            border-radius: 20px;
        }
        th, td {
            padding: 12px 10px;
            text-align: left;
            border-bottom: 1px solid #555;
            font-size: 14px;
        }
        th {
            background-color: #333;
            color: white;
            text-transform: uppercase;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        tr {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #ddd;
        }
        .crash-row {
            background-color: #ffe6e6 !important;
        }
        .crash-row:hover {
            background-color: #ffcccc !important;
        }
        .no-data {
            color: white;
            text-align: center;
            padding: 40px;
            font-size: 18px;
        }
        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }
        .badge-crash {
            background-color: #e74c3c;
        }
        .badge-normal {
            background-color: #27ae60;
        }
        .flame-row {
            background-color: #fff3e0 !important;  /* Ανοιχτό πορτοκαλί */
        }
        .flame-row:hover {
            background-color: #ffe0b2 !important;  /* Πιο σκούρο πορτοκαλί */
        }
        .badge-flame {
            background-color: #ff9800;  /* Πορτοκαλί */
        }
    </style>
</head>
<body>

    <h2>Crash Detection System - Live Map</h2>

    <div id="map"></div>

    <?php

    $conn = mysqli_connect("localhost", "root", "", "accident_data");
    
    if (!$conn) {
        die('<p class="no-data"> Connection failed: ' . mysqli_connect_error() . '</p>');
    }

    $sql = "SELECT * FROM points ORDER BY created_at DESC";
    $result = mysqli_query($conn, $sql);
    ?>

    <script>
        // Αρχικοποίηση χάρτη
        var map = L.map('map').setView([39.074207, 21.824312], 7);
        
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        // Ομάδα για τα markers (για εύκολη διαχείριση)
        var crashGroup = L.layerGroup().addTo(map);
    </script>

    <?php
    if (mysqli_num_rows($result) > 0) {
        // Πρώτα βάζουμε τα markers στον χάρτη
        while ($row = mysqli_fetch_assoc($result)) {
            $lat = $row["latitude"];
            $lon = $row["longitude"];
            $accident = $row["accident"];
            $speed = $row["speed"];
            $fullname = $row["fullname"];
            $date = $row["date"];
            $time = $row["time"];
            
            if ($accident == "crash") {
                $markerColor = "red";
            } elseif ($accident == "flame") {
                $markerColor = "orange";
            } else {
                $markerColor = "blue";
            }
            ?>
            <script>
                // Δημιουργία custom marker με χρώμα
                var markerIcon = L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-<?php echo $markerColor; ?>.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
                
                var marker = L.marker([<?php echo $lat; ?>, <?php echo $lon; ?>], {icon: markerIcon}).addTo(map);
                
                var popupText = "<b><?php echo htmlspecialchars($fullname); ?></b><br>" +
                               "Lat: <?php echo $lat; ?><br>" +
                               "Lon: <?php echo $lon; ?><br>" +
                               "Speed: <?php echo $speed; ?> km/h<br>" +
                               "Date: <?php echo $date . ' ' . $time; ?><br>" +
                               $statusText = ($accident == "crash") ? "CRASH" : (($accident == "flame") ? "FLAME" : "NORMAL");
                                "Status: <b>" . $statusText . "</b>";
                
                marker.bindPopup(popupText);
            </script>
            <?php
        }
        
        // Επαναφορά του result pointer για τον πίνακα
        mysqli_data_seek($result, 0);
    }
    ?>

    <div id="table-container">
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Latitude</th>
                <th>Longitude</th>
                <th>Speed (km/h)</th>
                <th>Date</th>
                <th>Time</th>
                <th>Full Name</th>
                <th>License Plate</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            <?php
            if (mysqli_num_rows($result) > 0) {
                while ($row = mysqli_fetch_assoc($result)) {
                $accidentType = $row["accident"];
                if ($accidentType == "crash") {
                    $rowClass = "crash-row";
                    $badgeClass = "badge-crash";
                    $statusText = "CRASH";
                } elseif ($accidentType == "flame") {
                    $rowClass = "flame-row";
                    $badgeClass = "badge-flame";
                    $statusText = "FLAME";
                } else {
                    $rowClass = "";
                    $badgeClass = "badge-normal";
                    $statusText = "NORMAL";
                }
                    ?>
                    <tr class="<?php echo $rowClass; ?>">
                        <td><?php echo $row["id"]; ?></td>
                        <td><?php echo $row["latitude"]; ?></td>
                        <td><?php echo $row["longitude"]; ?></td>
                        <td><?php echo $row["speed"]; ?></td>
                        <td><?php echo $row["date"]; ?></td>
                        <td><?php echo $row["time"]; ?></td>
                        <td><?php echo htmlspecialchars($row["fullname"]); ?></td>
                        <td><?php echo htmlspecialchars($row["license_plate"]); ?></td>
                        <td><span class="badge <?php echo $badgeClass; ?>"><?php echo $statusText; ?></span></td>
                    </tr>
                    <?php
                }
            } else {
                ?>
                <tr>
                    <td colspan="9" class="no-data" style="color: #333;">  Δεν υπάρχουν δεδομένα ακόμα.</td>
                </tr>
                <?php
            }
            mysqli_close($conn);
            ?>
        </tbody>
    </table>
    </div>

</body>
</html>