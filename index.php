<!DOCTYPE html>

<html>

   <head>
	<head>
	  <link rel="stylesheet" href="style.css" media="screen">
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

	function readFromDatabase() {
		global $locked,$alarm,$phoneCommState,$phoneSignalInfo,$temp1,$temp2,$humidity,$pressure,$voltageMet;
	
		
		$db = new SQLite3('/home/pi/main.db');

		$results = $db->query('SELECT * FROM state');
		$row = $results->fetchArray();
		
		$db->close();
		
		$locked=$row['locked']=='1'?1:0;
		$alarm=$row['alarm']=='1'?1:0;
		
		$phoneCommState=$row['phoneCommState']=='1'?1:0;
		$phoneSignalInfo=$row['phoneSignalInfo'];
		
		$temp1=$row['temp1'];
		$temp2=$row['temp2'];
		$humidity=$row['humidity'];
		$pressure=$row['pressure'];
		$voltageMet=$row['voltageMet'];
		
		
		
		//document.getElementById("textout").innerHTML = str; 
	}
	
	function runPriceScript() {
		global $pyPrice;
		
		$command = escapeshellcmd('python3 /home/pi/scripts/electricityPrice.py');
		$output = shell_exec($command);
		//$data = json_decode($output,true);
		
		// Read JSON file
		$json = file_get_contents('/home/pi/scripts/consumptionData/electricityPriceData.txt');

		//Decode JSON
		$pyPrice = json_decode($json,true);	

	}
	?>
   <script>//JAVASCRIPT
	   
	var backgroundWidth = 800.0;
	var backgroundHeight = 600.0;
	
	
	function winResize() {
		
		var canvs = document.getElementById("myCanvas");
		canvs.width = window.innerWidth;
		canvs.height = window.innerWidth*backgroundHeight/backgroundWidth;
		
		<?php
		readFromDatabase();
		?>
		
		draw();
		
	}
	function draw() {
		<?php
			global $locked,$alarm,$phoneCommState,$phoneSignalInfo,$temp1,$temp2,$humidity,$pressure,$voltageMet;
			global $price1,$data;
		?>
		
		var canvas = document.getElementById("myCanvas");
		var ctx=canvas.getContext("2d");
		ctx.font="30px Comic Sans MS";
		ctx.fillStyle = "red";
		ctx.textAlign = "center";
		ctx.fillText("Hello World", canvas.width/2, canvas.height/2);
		
		var w = canvas.width/100;
		var h = canvas.height/100;
		
				
		var fontSize = 2*w;
		ctx.font = fontSize+"px OCR A Extended";
		ctx.fillStyle = "#2cb4e8";
		ctx.textAlign="left"; 
		
		
		ctx.fillText("Temperature1: "+<?php echo $temp1;?>+"°C",60*w,10*h);
		ctx.fillText("Temperature2: "+<?php echo $temp2;?>+"°C",60*w,13*h);
		ctx.fillText("Humidity: "+<?php echo $humidity;?>+"%",60*w,16*h);
		ctx.fillText("Pressure: "+<?php echo $pressure;?>+"kPa",60*w,19*h);
		ctx.fillText("Voltage met: "+<?php echo $voltageMet;?>+"V",60*w,22*h);
		ctx.fillText("Locked: "+<?php echo $locked;?>,60*w,25*h);
		
		if (<?php echo $phoneCommState;?>==0){
			ctx.fillStyle = "red";
		}
		ctx.fillText("Phone comm: "+<?php echo $phoneCommState;?>,60*w,28*h);
		
		if (<?php echo $phoneCommState;?>==1){
			var myvar = <?php echo json_encode($phoneSignalInfo); ?>;
			ctx.fillText("Quality: "+myvar,62*w,31*h);
		}
		
		ctx.fillStyle = "#2cb4e8";
		
		
		//var myvar2 = String(<?php echo gettype($price1);?>));
		
		<?php
		runPriceScript();
		?>

		ctx.fillText("Cena za včera:"+<?php echo $pyPrice['priceLastDay'];?>+" kč",60*w,40*h);
		
		ctx.fillText("Plnění ročního zúčtování:"+<?php echo $pyPrice['yearPerc'];?>+" %",60*w,43*h);
	}
	
	</script>
	
   <body bgcolor="#404040"onload="winResize()">
   
		<svg class="svg-background" viewBox="0 0 800 600" >
			<?php echo file_get_contents("graphics/background.svg"); ?>
		</svg>
	
	
	<canvas id="myCanvas" style="border:1px solid #d3d3d3;">
		Your browser does not support the canvas element.
	</canvas>

	
	<br><br><br><br><br><br><br><br><br><br><br><br>
	<br><br><br><br><br><br><br><br><br><br><br><br>
	<br><br><br><br><br><br><br><br><br><br><br><br>
	<br><br><br><br><br><br><br><br><br><br><br><br>
	<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
	---------
	<p id="textout"></p>
	
	<a href="/grafana" style="color: #F6F6E8">Grafana</a> 
	
	   
	   
    <?php
	if(array_key_exists('buttonHeatingInhibit', $_POST)) { 
		//echo $_POST["buttonHeatingInhibitVal"];
		
		$db = new SQLite3('/home/pi/main.db');
		$db->exec("UPDATE cmd SET updated = 1, heatingInhibit = ".$_POST["buttonHeatingInhibitVal"]);
		$db->close();
	   
	} 
	else if(array_key_exists('buttonVentilationCmd', $_POST)) { 
		$db = new SQLite3('/home/pi/main.db');
		$db->exec("UPDATE cmd SET updated = 1, ventilationCmd = ".$_POST["buttonVentilationCmdVal"]);
		$db->close();
	} 
    ?> 
	   
	<form method="post"> 
        <input type="submit" name="buttonHeatingInhibit" value="buttonHeatingInhibit"/> 
		<input type="text" name="buttonHeatingInhibitVal"
                value="0" /> 
          
        <input type="submit" name="buttonVentilationCmd" value="buttonVentilationCmd"/> 
		<input type="text" name="buttonVentilationCmdVal"
                value="0" /> 
    </form> 

	<script>
		
		var uc=true;
		window.addEventListener("resize", winResize, uc);
		
		
		draw();
	
		
	</script>
	

</body>

</html>
