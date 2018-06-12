<?php   
 


$page = $_SERVER['PHP_SELF'];
$sec = "30";


$actualData = json_decode(exec('python3 getMeas.py actual'),true);

$eventTable = json_decode(exec('python3 getEvents.py'),true);

$state = json_decode(exec('python3 getState.py'),true);

?>


<html>

   <head>
    <meta http-equiv="refresh" content="<?php echo $sec?>;URL='<?php echo $page?>'">
    
      <title>Home system visualization</title>
   </head>
<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 15%;
    color: #F6F6E8;
}

td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}
</style>
   <body bgcolor="#404040">
	   
</br>
</br>

<div style="float:right; width:10%;">
		<a href="graphsPage.php" style="color: #F6F6E8">Dlouhodobé grafy</a> 
</div>
<div style="float:right; width:10%;">
		<a href="serviceGraphs.php" style="color: #F6F6E8">Servisní grafy</a> 
</div>
      <font color="#F6F6E8" size = "8">Aktuální stav:</font></br>
<blockquote>
	<font color="#F6F6E8" size = "8">Doma:</font></br>
<blockquote>

	<div style="float:right; width:50%;">
		<IMG SRC = 'graph1.php'/IMG>
	</div>
      <font color="#D43F3F" size = "8">T:<?php echo $actualData['m_key_t'][0]?> °C</font>
	</br>
      <font color="#00ACE9" size = "8">RH:<?php echo $actualData['m_key_rh'][0]?> %</font></br>   
	
<font color="#F6F6E8" size = "8">Dveře:</font>

<?php if($actualData['m_key_d'][0]=='1'): ?> <font color="#D43F3F" size = "8">Otevřeny</font> <?php else: ?> <font color="#6A9A1F" size = "8">Zavřeny</font> <?php endif ?>
</br></br></br>

<?php if($state['state']==0): ?> <font color="#F6F6E8" size = "8">Stand-by</font> <?php endif ?>
<?php if($state['state']==1): ?> <font color="#6A9A1F" size = "8">Zabezpečeno</font> <?php endif ?>
<?php if($state['state']==2): ?> <font color="#D43F3F" size = "8">BEZPEČNOSTNÍ ALARM!</font> <?php endif ?>

</br></br>
<font color="#F6F6E8" size = "3"> Stáří dat: <?php echo $actualData['m_key_t'][1] ?></font>

</br></br></br>
</blockquote>

	<div style="float:right; width:50%;">
		<IMG SRC = 'graph2.php'/IMG>
	</div>

<font color="#F6F6E8" size = "8">Venku:</font></br>  
<blockquote>
<font color="#D43F3F" size = "8">T:<?php echo number_format($actualData['m_met_t'][0],1)?> °C</font></br>
<font color="#00ACE9" size = "8">P:<?php echo number_format($actualData['m_met_p'][0]/1000.0,2)?> kPa</font></br>  
<font color="#6A9A1F" size = "8">U:<?php echo number_format($actualData['m_met_u'][0],2)?> V</font>
 
 <?php if($actualData['m_met_u'][2]>=0):?> 
	<font color="#6A9A1F" size = "5">
 <?php else:?> 
	<font color="#D43F3F" size = "5">
 <?php endif ?>
 
 <?php echo sprintf("%+.4f",$actualData['m_met_u'][2]) ?> V
 </font> 
 
</br>
<font color="#F6F6E8" size = "3"> Stáří dat: <?php echo $actualData['m_met_t'][1] ?></font>

</blockquote>
</blockquote>


</br>
<font color="#F6F6E8" size = "8">Tabulka událostí:</font></br>
<blockquote>
<?php


echo "<table>";
foreach($eventTable as $k=>$v)
    echo "<tr><td>$v[0]</td><td>$v[1]</td><td>$v[2]</td><td>$v[3]</td></tr>";
echo "</table>";

    
?>
</blockquote>


</body>

</html>
