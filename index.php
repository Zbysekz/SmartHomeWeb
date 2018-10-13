<!DOCTYPE html>

<html>

   <head>
	<head>
	  <link rel="stylesheet" href="style.css" media="screen">
	</head>
    <!-- <meta http-equiv="refresh" content="<?php echo $sec?>;URL='<?php echo $page?>'"> -->
    
      <title>Home system visualization</title>
   </head>

   <body bgcolor="#404040">
	   
	<?php echo file_get_contents("graphics/background.svg"); ?>
	
	<canvas id="myCanvas" width="300" height="200"
	style="border:1px solid #d3d3d3;">
	Your browser does not support the canvas element.
	</canvas>

	<script>
	var canvas = document.getElementById("myCanvas");
	var ctx=canvas.getContext("2d");
	ctx.font="30px Comic Sans MS";
	ctx.fillStyle = "red";
	ctx.textAlign = "center";
	ctx.fillText("Hello World", canvas.width/2, canvas.height/2);
	</script>
</body>

</html>
