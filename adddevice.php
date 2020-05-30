<?php

include('config.php');

$ip_addr = $_GET['ip_addr'];
$port_no = $_GET['port_no'];
$community = $_GET['community'];
$version = $_GET['version'];

if(empty($ip_addr) || empty($port_no) || empty($community) || empty($version)) {
    echo "please provide proper input" ;   
}

else {

    $db->exec("INSERT INTO info (IP,PORT,COMMUNITY,VERSION) VALUES ('$ip','$port','$community','$version')");
        echo "\n";
        echo "OK";
    
    }
$db->close();

?>