<?php
/*** set the content type header ***/
/*** Without this header, it wont work ***/
header("Content-type: text/css");


$font_family = 'Arial, Helvetica, sans-serif';
$font_size = '0.7em';
$border = '1px solid';
?>

table {
margin: 8px;
}

th {
font-family: <?=$font_family?>;
font-size: <?=$font_size?>;
background: #666;
color: #FFF;
padding: 2px 6px;
border-collapse: separate;
border: <?=$border?> #000;
}

td {
font-family: <?=$font_family?>;
font-size: <?=$font_size?>;
border: <?=$border?> #DDD;
}
body {
   display: block;
   background: no-repeat;
   background-image: url(visu.svg);
   background-size: 100%;
   background-color: #cccccc;
   color: white;
}

/*Strong signal*/
.iconic-signal.iconic-signal-strong .iconic-signal-base {
    fill:#569e26;
}
.iconic-signal.iconic-signal-strong .iconic-signal-wave * {
    stroke:#569e26;
}