
<!DOCTYPE html>

<html>

   <head>
	<head>
	</head>
    
      <title>Home system visualization</title>
   </head>
   
   
   <?php
		$price1 = 0;
	   
	   function runPriceScript() {
		    global $price1;
		   
			$command = escapeshellcmd('python3 /home/pi/scripts/electricityPrice.py');
			$output = shell_exec($command);
			$data = json_decode($output);
			
			$price1 = $data->data1;
			
			echo "Variable is:$price1";
		}
		
	?>	
	

   
 
   <body>
   <?php
   echo 'start<p>';  
   
   runPriceScript();
   
   echo '<p>end<p>';
   
   ?>


	
	
   </body>
   
</html>


