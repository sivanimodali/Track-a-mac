
<?php
class mydb extends SQLite3 {
      function __construct() {
         $this->open('mydatabase.db');
      }
}
$db = new mydb();


$result = $db->exec('CREATE TABLE IF NOT EXISTS List(IP_addr varchar not null, VLANs varchar not null, PORT_no varchar, MACS varchar)');
if(!$result){
   echo $db->lastErrorMsg(); #prints the error which causes SQlite request to fail
}

$result = $db->exec('CREATE TABLE IF NOT EXISTS info(IP_addr varchar not null,PORT_no varchar not null,COMMUNITY string not null ,VERSION varchar not null, FIRST_PROBE varchar, LATEST_PROBE varchar null, FAILED_ATTEMPTS int default 0 not null)');
   if(!$result){
      echo $db->lastErrorMsg();
   }

?>