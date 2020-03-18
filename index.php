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
		$db->busyTimeout(5000);
		
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
		$pressure=$row['pressure']/100;
		$voltageMet=$row['voltageMet'];
		
		
		
		//document.getElementById("textout").innerHTML = str; 
	}
	
	?>
   <script>//JAVASCRIPT
	   
	var backgroundWidth = 800.0;
	var backgroundHeight = 400.0;
	
	
	function winResize() {
		
		var canvs = document.getElementById("myCanvas");
		canvs.width = window.innerWidth;
		canvs.height = window.innerWidth*backgroundHeight/backgroundWidth;
		
		<?php
		readFromDatabase();
		?>
		
		draw();
		
	}
	
	function ShowFloat(n, decimals){
		return parseFloat(n).toFixed(decimals);
	}
	
	function draw() {
		<?php
			global $locked,$alarm,$phoneCommState,$phoneSignalInfo,$temp1,$temp2,$humidity,$pressure,$voltageMet;
			global $price1,$data;
		?>
		
		var canvas = document.getElementById("myCanvas");
		var ctx=canvas.getContext("2d");

		var w = canvas.width/100;
		var h = canvas.height/100;
		
				
		var fontSize = 1.7*w;
		var offsetH = 4;
		ctx.font = fontSize+"px monospace";//OCR A Extended
		
		/*
		ctx.fillStyle = "#2cb4e8";
		if(navigator.platform.includes("Linux x86")){		
			ctx.font = fontSize+"px Uroob";//ctx.fillText("Linux",10,40);
		}else if(navigator.platform.includes("Linux arm")){		
			ctx.font = fontSize+"px Lucida Console";//ctx.fillText("Android",10,40);
		}else if(navigator.platform.includes("Win")){		
			ctx.font = fontSize+"px Lucida Console";//ctx.fillText("Windows",10,40);
		 }*/
		
		/* -------------------- INSIDE HOUSE ----------------------- */
		ctx.fillStyle = "#2cb4e8";
		ctx.textAlign="left";
		var posX = 20;
		var posY = 45;
		ctx.fillText(ShowFloat(<?php echo $temp1;?>,1)+"°C",posX*w,posY*h);posY+=offsetH;
		ctx.fillText(ShowFloat(<?php echo $humidity;?>,1)+"%",posX*w,posY*h);posY+=offsetH;
		
		ctx.textAlign="center"; 
		posX=31.5;posY=24;
		if (<?php echo $locked;?>==0){
			ctx.fillStyle = "#f08700ff";
			ctx.fillText("Odemknuto",posX*w,posY*h);
		}else{
			ctx.fillStyle = "#25b81dff";
			ctx.fillText("Zamknuto",posX*w,posY*h);
		}
		/* -------------------- OUTSIDE METEOSTATION ----------------------- */
		ctx.textAlign="left"; 
		ctx.fillStyle = "#2cb4e8";
		posX = 70;
		posY = 12;
		ctx.fillText(ShowFloat(<?php echo $temp2;?>,1)+" °C",posX*w,posY*h);posY+=offsetH;
		ctx.fillText(ShowFloat(<?php echo $pressure;?>,1)+" kPa",posX*w,posY*h);posY+=offsetH;
		ctx.fillText(ShowFloat(<?php echo $voltageMet;?>,2)+" V",posX*w,posY*h);posY+=offsetH;
		
		
		/* -------------------- SIGNAL INFO ----------------------- */
		posX = 7.5;
		posY = 13;
		if (<?php echo $phoneCommState;?>==0){
			ctx.fillStyle = "red";
			ctx.fillText("OK",posX*w,posY*h);
		}else{
			ctx.fillStyle = "#2cb4e8";
			ctx.fillText("OK",posX*w,posY*h);
		}
		posY+=4;
		var myvar = <?php echo json_encode($phoneSignalInfo); ?>;
		if(myvar != 'Excellent')
			ctx.fillStyle = "red";
		else
			ctx.fillStyle = "#2cb4e8";
		ctx.fillText(myvar,posX*w,posY*h);
	
		
		/* -------------------- PRICES ----------------------- */
		<?php
			// Read JSON file
			$json = file_get_contents('/home/pi/scripts/consumptionData/electricityPriceData.txt');

			//Decode JSON
			$pyPrice = json_decode($json,true);	
		?>
		posX = 5;
		posY = 76.5;
		
		ctx.fillStyle = "#2cb4e8";

		ctx.fillText("Cena za včera: "+<?php echo $pyPrice['priceLastDay'];?>+" kč",posX*w,posY*h);posY+=offsetH;
		ctx.fillText("Plnění ročního zúčtování: "+<?php echo $pyPrice['yearPerc'];?>+" %",posX*w,posY*h);posY+=offsetH;
		ctx.fillText("Denní přírůstek: "+ShowFloat(<?php echo $pyPrice['dailyIncrease'];?>,1)+" %",posX*w,posY*h);posY+=offsetH;
	}
	
	</script>
	
   <body bgcolor="#404040"onload="winResize()">
   
		<svg class="svg-background" viewBox="0 0 800 400" >
			<?php echo file_get_contents("graphics/background.svg"); ?>
		</svg>
	
	
	<canvas id="myCanvas" style="border:1px solid #d3d3d3;">
		Your browser does not support the canvas element.
	</canvas>
	
	

	
	<br><br><br><br><br><br><br><br><br><br><br><br>
	<br><br><br><br><br><br><br><br><br><br><br><br>
	<br><br><br><br><br><br><br><br><br><br><br><br>
	<br><br><br><br><br><br><br><br><br><br><br><br>
	<br><br><br><br><br><br>
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
