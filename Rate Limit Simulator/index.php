<?php  
/*
created by SecuritySura for hacksmith 4.0 demo purposes
*/   
 function countint(){
  $ip = $_SERVER['REMOTE_ADDR'];
  global $countfile , $ipfile, $ipvalue, $ip, $connection;
 $connection = new mysqli("localhost", "badass", "badbadass", "hacksmith");
   if ($connection->errno) {
    printf("Connect failed: %s\n", $connection->error);
    exit();
}
  // echo 'Connected to the database.<br>';
$stmt = $connection->prepare("INSERT INTO hacksmith.rl (ip) values (?)");
$stmt->bind_param('s', $_SERVER['REMOTE_ADDR']);
if ($result = $stmt->execute()){
 // echo "success";
  $stmt->free_result();
}
else {
  echo "error";
}
 }
blockips3m();
blockips1m();
countint();
function blockips1m(){
  global $countfile , $ipfile, $ipvalue, $ip2, $connection;
  $connection = new mysqli("localhost", "badass", "badbadass", "hacksmith");
 // $query = "SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 100 minute) AND ip= ?";
  $stmt = $connection->prepare("SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 1 minute) AND ip= ?");
  $stmt->bind_param("s", $_SERVER['REMOTE_ADDR']);
  $stmt->execute();
  $result = $stmt->get_result();
  $value = $result->fetch_row()[0] ?? false;
//echo $value;
if ($value >= 10){
  $ip2 = $_SERVER['REMOTE_ADDR'];
$test2 = exec("sudo /home/sura/script1m.sh $ip2");
}
}
function blockips3m(){
  global $countfile , $ipfile, $ipvalue, $ip1, $connection;
  $connection = new mysqli("localhost", "badass", "badbadass", "hacksmith");
 // $query = "SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 100 minute) AND ip= ?";
  $stmt = $connection->prepare("SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 3 minute) AND ip= ?");
  $stmt->bind_param("s", $_SERVER['REMOTE_ADDR']);
  $stmt->execute();
  $result = $stmt->get_result();
  $value = $result->fetch_row()[0] ?? false;
if ($value >= 25
){
  $ip1 = $_SERVER['REMOTE_ADDR'];
$test1 = exec("sudo /home/sura/script3m.sh $ip1");
}
}
$connection->close();