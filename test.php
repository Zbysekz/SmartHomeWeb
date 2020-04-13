<!DOCTYPE html>

<html>

   <head>
	<head>
	</head>
    
      <title>Home system visualization</title>
   </head>

	<?php
	
	
	
	$locked = 0;
	$alarm = 0;
	$phoneCommState = 0;
	$phoneSignalInfo = 'Not available';
	$temp1=0.0;
	$temp2=0.0;
	$humidity=0.0;
	$pressure=0.0;
	$voltageMet=0.0;
	$pyPrice;
	$deviceTable = array();

	function readFromDatabase() {
		global $locked,$alarm,$phoneCommState,$phoneSignalInfo,$temp1,$temp2,$humidity,$pressure,$voltageMet,$deviceTable;
	
		
		$db = new SQLite3('/home/pi/main.db');
		$db->busyTimeout(5000);
		
		// ----- read state table
		$results = $db->query('SELECT * FROM state');
		$row = $results->fetchArray();
		
		// ----- read online device table
		$results = $db->query('SELECT ip FROM onlineDevices LIMIT 10');
		
		while ($row = $results->fetchArray()) {
			//var_dump($row);
    		array_push($deviceTable, $row);
		}
		
		$db->close();
		
		$locked=$row['locked']=='1'?1:0;
		$alarm=$row['alarm']=='1'?1:0;
		
		$phoneCommState=$row['phoneCommState']=='1'?1:0;
		$phoneSignalInfo=$row['phoneSignalInfo'];
		
		$temp1=$row['temp1'];
		$temp2=$row['temp2'];
		$humidity=$row['humidity'];
		$pressure=$row['pressure']/100;
		$voltageMet=$row['voltageMet'];
	
		
		//document.getElementById("textout").innerHTML = str; 
	}
	
	function CheckDeviceOnline($ip){
		global $deviceTable;
			
		foreach ($deviceTable as $entry) {
			if ($entry['ip'] == $ip)
				return true;
			else
				return false;
				
		}
	}
	
	?>
   
	
   <body>
   
		<?php
	   echo "Hello!";
	   readFromDatabase();
	   
	   var_dump(CheckDeviceOnline("192.168.0.99"));
	   ?>
	

</body>

</html>

