<?php
 /* CAT:Area Chart */

 /* pChart library inclusions */
 include("class/pData.class.php");
 include("class/pDraw.class.php");
 include("class/pImage.class.php");

$dataCount = 48;

$data1 = json_decode(exec('python3 getMeas.py hour m_key_rh '.$dataCount),true);
$data2 = json_decode(exec('python3 getMeas.py hour m_met_p '.$dataCount),true);


$arrA 	 = array();
$arrAmax = array();
$arrAmin = array();

$arrB 	 = array();
$arrBmax = array();
$arrBmin = array();

$time = array();
for ($x = $dataCount-1; $x >=0 ; $x--) {
	if($data1[$x][1] != null):
		array_push($arrA,$data1[$x][1]);
		array_push($arrAmin,$data1[$x][2]);
		array_push($arrAmax,$data1[$x][3]);
	else:
		array_push($arrA,VOID);
		array_push($arrAmin,VOID);
		array_push($arrAmax,VOID);
	endif;
	if($data2[$x][1] != null):
		array_push($arrB,$data2[$x][1]);
		array_push($arrBmin,$data2[$x][2]);
		array_push($arrBmax,$data2[$x][3]);
	else:
		array_push($arrB,VOID);
		array_push($arrBmin,VOID);
		array_push($arrBmax,VOID);
	endif;
	if($x==0 or $x==$dataCount-1):
		array_push($time,substr($data1[$x][0], 0, -3));
	elseif($x < $dataCount-5 and $x%5==0):
		array_push($time,substr($data1[$x][0], 11,5));
	else:
		array_push($time,' ');
	endif;
} 


 /* Create and populate the pData object */
 $MyData = new pData();  
 
 $MyData->addPoints($arrA,"Vlhkost doma");
 $MyData->addPoints($arrAmin,"Vlhkost doma min");
 $MyData->addPoints($arrAmax,"Vlhkost doma max");
 
 $MyData->addPoints($arrB,"Tlak venku");
 $MyData->addPoints($arrBmin,"Tlak venku min");
 $MyData->addPoints($arrBmax,"Tlak venku max");
 
 /* dotted line for min and max */
 $MyData->setSerieTicks("Tlak venku min",4);
 $MyData->setSerieTicks("Tlak venku max",4);
 $MyData->setSerieTicks("Vlhkost doma min",4);
 $MyData->setSerieTicks("Vlhkost doma max",4);
 
 $MyData->setSerieOnAxis("Vlhkost doma",0);
 $MyData->setSerieOnAxis("Vlhkost doma min",0);
 $MyData->setSerieOnAxis("Vlhkost doma max",0);
 $MyData->setSerieOnAxis("Tlak venku",1);
 $MyData->setSerieOnAxis("Tlak venku min",1);
 $MyData->setSerieOnAxis("Tlak venku max",1);
 
 $MyData->setAxisName(0,"Vlhkost");
 $MyData->setAxisName(1,"Tlak");
 $MyData->addPoints($time,"Labels");
 $MyData->setSerieDescription("Labels","Months");
 $MyData->setAbscissa("Labels");

 /* color of lines */
 $serieSettings = array("R"=>230,"G"=>210,"B"=>30,"Alpha"=>80);
 $MyData->setPalette("Tlak venku",$serieSettings);
 $MyData->setPalette("Tlak venku min",$serieSettings);
 $MyData->setPalette("Tlak venku max",$serieSettings);
 
 $MyData->setAxisColor(1,$serieSettings);
 /* color of lines */
 $serieSettings = array("R"=>80,"G"=>110,"B"=>160,"Alpha"=>80);
 $MyData->setPalette("Vlhkost doma",$serieSettings);
 $MyData->setPalette("Vlhkost doma min",$serieSettings);
 $MyData->setPalette("Vlhkost doma max",$serieSettings);
 
 $MyData->setAxisColor(0,$serieSettings);
 
 /* Create the pChart object */
 $myPicture = new pImage(700,230,$MyData);

 /* Turn of Antialiasing */
 $myPicture->Antialias = FALSE;

 /* Draw the background */ 
 $Settings = array("R"=>170, "G"=>183, "B"=>87, "Dash"=>1, "DashR"=>190, "DashG"=>203, "DashB"=>107);
 $myPicture->drawFilledRectangle(0,0,700,230,$Settings); 

 /* Overlay with a gradient */ 
 $Settings = array("StartR"=>219, "StartG"=>231, "StartB"=>139, "EndR"=>1, "EndG"=>138, "EndB"=>68, "Alpha"=>50);
 $myPicture->drawGradientArea(0,0,700,230,DIRECTION_VERTICAL,$Settings); 
 
 /* Add a border to the picture */
 $myPicture->drawRectangle(0,0,699,229,array("R"=>0,"G"=>0,"B"=>0));
 
 /* Write the chart title */ 
 $myPicture->setFontProperties(array("FontName"=>"fonts/Forgotte.ttf","FontSize"=>11));
 $myPicture->drawText(150,35,"Vlhkost a tlak za posledních 48h",array("FontSize"=>20,"Align"=>TEXT_ALIGN_BOTTOMMIDDLE));

 /* Set the default font */
 $myPicture->setFontProperties(array("FontName"=>"fonts/pf_arma_five.ttf","FontSize"=>8));

 /* Define the chart area */
 $myPicture->setGraphArea(105,40,650,200);

 /* Draw the scale */
 $scaleSettings = array("XMargin"=>10,"YMargin"=>10,"Floating"=>TRUE,"GridR"=>255,"GridG"=>255,"GridB"=>255,"DrawSubTicks"=>TRUE,"CycleBackground"=>TRUE);
 $myPicture->drawScale($scaleSettings);

 /* Write the chart legend */
 $MyData->setSerieDrawable("Vlhkost doma min", FALSE);
 $MyData->setSerieDrawable("Vlhkost doma max", FALSE);
 $MyData->setSerieDrawable("Tlak venku min", FALSE);
 $MyData->setSerieDrawable("Tlak venku max", FALSE);
 
 $myPicture->drawLegend(430,20,array("Style"=>LEGEND_NOBORDER,"Mode"=>LEGEND_HORIZONTAL));

 $MyData->setSerieDrawable("Vlhkost doma min", TRUE);
 $MyData->setSerieDrawable("Vlhkost doma max", TRUE);
 $MyData->setSerieDrawable("Tlak venku min", TRUE);
 $MyData->setSerieDrawable("Tlak venku max", TRUE);
 
 /* Turn on Antialiasing */
 $myPicture->Antialias = TRUE;

 /* Draw the area chart */
 //$myPicture->drawAreaChart();

 /* Draw a line and a plot chart on top */
 $myPicture->setShadow(TRUE,array("X"=>1,"Y"=>1,"R"=>0,"G"=>0,"B"=>0,"Alpha"=>10));
 $myPicture->drawLineChart();
 
 $MyData->setSerieDrawable("Vlhkost doma min", FALSE);
 $MyData->setSerieDrawable("Vlhkost doma max", FALSE);
 $MyData->setSerieDrawable("Tlak venku min", FALSE);
 $MyData->setSerieDrawable("Tlak venku max", FALSE);
 
 $myPicture->drawPlotChart(array("PlotBorder"=>TRUE,"PlotSize"=>3,"BorderSize"=>1,"Surrounding"=>-60,"BorderAlpha"=>80));

 /* Render the picture (choose the best way) */
 //$myPicture->autoOutput("resources/example.drawAreaChart.simple.png");
 //header("Content-Type: image/png");
 $myPicture->stroke();
 ?>
