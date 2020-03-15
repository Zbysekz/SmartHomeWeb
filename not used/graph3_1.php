<?php
 /* CAT:Area Chart */

 /* pChart library inclusions */
 include("class/pData.class.php");
 include("class/pDraw.class.php");
 include("class/pImage.class.php");

$dataCount = 60;

$data1 = json_decode(exec('python3 getMeas.py day m_met_u '.$dataCount),true);


$arrA 	 = array();
$arrAmax = array();
$arrAmin = array();


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
	if($x==0 or $x%4==0 or $x==$dataCount-1):
		array_push($time,str_replace('00:00:00','',$data1[$x][0]));
	else:
		array_push($time,' ');
	endif;
} 


 /* Create and populate the pData object */
 $MyData = new pData();  
 
 $MyData->addPoints($arrA,"Napeti akumulatoru");
 $MyData->addPoints($arrAmin,"Napeti akumulatoru min");
 $MyData->addPoints($arrAmax,"Napeti akumulatoru max");
 
 $MyData->setSerieTicks("Napeti akumulatoru min",4);
 $MyData->setSerieTicks("Napeti akumulatoru max",4);
 
 $MyData->setAxisName(0,"Voltage");
 $MyData->addPoints($time,"Labels");
 $MyData->setSerieDescription("Labels","Months");
 $MyData->setAbscissa("Labels");

 /* color of lines */
 $serieSettings = array("R"=>200,"G"=>50,"B"=>68,"Alpha"=>100);
 $MyData->setPalette("Napeti akumulatoru",$serieSettings);
 $MyData->setPalette("Napeti akumulatoru min",$serieSettings);
 $MyData->setPalette("Napeti akumulatoru max",$serieSettings);
 
 /* Create the pChart object */
 $myPicture = new pImage(1550,230,$MyData);

 /* Turn of Antialiasing */
 $myPicture->Antialias = FALSE;

 /* Draw the background */ 
 $Settings = array("R"=>170, "G"=>183, "B"=>87, "Dash"=>1, "DashR"=>190, "DashG"=>203, "DashB"=>107);
 $myPicture->drawFilledRectangle(0,0,1550,230,$Settings); 

 /* Overlay with a gradient */ 
 $Settings = array("StartR"=>219, "StartG"=>231, "StartB"=>139, "EndR"=>1, "EndG"=>138, "EndB"=>68, "Alpha"=>50);
 $myPicture->drawGradientArea(0,0,1550,230,DIRECTION_VERTICAL,$Settings); 
 
 /* Add a border to the picture */
 $myPicture->drawRectangle(0,0,1549,229,array("R"=>0,"G"=>0,"B"=>0));
 
 /* Write the chart title */ 
 $myPicture->setFontProperties(array("FontName"=>"fonts/Forgotte.ttf","FontSize"=>11));
 $myPicture->drawText(150,35,"Napeti za poslednich 60 dni",array("FontSize"=>20,"Align"=>TEXT_ALIGN_BOTTOMMIDDLE));

 /* Set the default font */
 $myPicture->setFontProperties(array("FontName"=>"fonts/pf_arma_five.ttf","FontSize"=>8));

 /* Define the chart area */
 $myPicture->setGraphArea(105,40,1500,200);

 /* Draw the scale */
 $scaleSettings = array("XMargin"=>10,"YMargin"=>10,"Floating"=>TRUE,"GridR"=>255,"GridG"=>255,"GridB"=>255,"DrawSubTicks"=>TRUE,"CycleBackground"=>TRUE);
 $myPicture->drawScale($scaleSettings);

 /* Write the chart legend */
 $MyData->setSerieDrawable("Napeti akumulatoru min", FALSE);
 $MyData->setSerieDrawable("Napeti akumulatoru max", FALSE);
 
 $myPicture->drawLegend(430,20,array("Style"=>LEGEND_NOBORDER,"Mode"=>LEGEND_HORIZONTAL));
 
 $MyData->setSerieDrawable("Napeti akumulatoru min", TRUE);
 $MyData->setSerieDrawable("Napeti akumulatoru max", TRUE);
 
 /* Turn on Antialiasing */
 $myPicture->Antialias = TRUE;

 /* Draw the area chart */
 //$myPicture->drawAreaChart();

 /* Draw a line and a plot chart on top */
 $myPicture->setShadow(TRUE,array("X"=>1,"Y"=>1,"R"=>0,"G"=>0,"B"=>0,"Alpha"=>10));
 $myPicture->drawSplineChart();
 
 $MyData->setSerieDrawable("Napeti akumulatoru min", FALSE);
 $MyData->setSerieDrawable("Napeti akumulatoru max", FALSE);
 
 $myPicture->drawPlotChart(array("PlotBorder"=>TRUE,"PlotSize"=>3,"BorderSize"=>1,"Surrounding"=>-60,"BorderAlpha"=>80));

 /* Render the picture (choose the best way) */
 //$myPicture->autoOutput("resources/example.drawAreaChart.simple.png");
 //header("Content-Type: image/png");
 $myPicture->stroke();
 ?>
