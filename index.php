<!DOCTYPE html>

<html>

   <head>
	<head>
	  <link rel="stylesheet" href="style.css" media="screen">
	</head>
    
      <title>Home system visualization</title>
   </head>

   <script>
	var backgroundWidth = 800.0;
	var backgroundHeight = 600.0;
	
	
	var locked = false,alarm = false;
	var temp1=0.0,temp2=0.0,humidity=0.0,pressure=0.0,voltageMet=0.0;
	
	function winResize() {
		
		var canvs = document.getElementById("myCanvas");
		canvs.width = window.innerWidth;
		canvs.height = window.innerWidth*backgroundHeight/backgroundWidth;
		
		draw();
	}
	function draw() {
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
		
		ctx.fillText("Temperature1: "+temp1+"°C",60*w,10*h);
		ctx.fillText("Temperature2: "+temp2+"°C",60*w,12*h);
		ctx.fillText("Humidity: "+humidity+"%",60*w,14*h);
		ctx.fillText("Pressure: "+pressure+"kPa",60*w,16*h);
		ctx.fillText("Voltage met: "+voltageMet+"V",60*w,18*h);
		ctx.fillText("Locked: "+locked,60*w,20*h);
	}
	
	function readFromDatabase() {
		<?php
		$db = new SQLite3('/home/pi/main.db');

		$results = $db->query('SELECT * FROM state');
		$row = $results->fetchArray();
		?>
		locked="<?php echo $row['locked']=='1'?'true':'false'; ?>";
		alarm="<?php echo $row['alarm']=='1'?'true':'false'; ?>";
		
		temp1="<?php echo $row['temp1']; ?>";
		temp2="<?php echo $row['temp2']; ?>";
		humidity="<?php echo $row['humidity']; ?>";
		pressure="<?php echo $row['pressure']; ?>";
		voltageMet="<?php echo $row['voltageMet']; ?>";
		
		
		//document.getElementById("textout").innerHTML = str; 
	}
	
	</script>
	
   <body bgcolor="#404040" onload="winResize()">
   
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
	
	<script>
		var uc=true
		window.addEventListener("resize", winResize, uc);
		
		draw();//Draw for first time
		
		readFromDatabase();
		
		
		
	</script>
	
</body>

</html>
