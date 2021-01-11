<?php  

/*

created by SecuritySura for hacksmith 4.0 demo purposes

*/   



 function countint(){

  $ip = $_SERVER['REMOTE_ADDR'];

  global $countfile , $ipfile, $ipvalue, $ip, $connection;

 $connection = new mysqli("localhost", "badass", "", "hacksmith");

       

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



//blockips3m();

//blockips1m();

policy2();

policy1();

countint();





function policy1(){

  global $countfile , $ipfile, $ipvalue, $ip, $connection;

  $connection = new mysqli("localhost", "badass", "", "hacksmith");

  

  // $query = "SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 100 minute) AND ip= ?";

  $stmt = $connection->prepare("SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 1 minute) AND ip= ?");

  $stmt->bind_param("s", $_SERVER['REMOTE_ADDR']);

  $stmt->execute();

  $result = $stmt->get_result();

  $value1 = $result->fetch_row()[0] ?? false;





  $stmt = $connection->prepare("SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 120 second) AND time < date_sub(now(), INTERVAL 60 SECOND) AND ip= ?");

  $stmt->bind_param("s", $_SERVER['REMOTE_ADDR']);

  $stmt->execute();

  $result = $stmt->get_result();

  $value2 = $result->fetch_row()[0] ?? false;



  if ($value1 > 10 || $value2 > 10){

    header('HTTP/1.1 429');

    echo "Too Many Requests 1m policy hit\n";

  }

} 





function policy2(){

  global $countfile , $ipfile, $ipvalue, $ip, $connection;

  $connection = new mysqli("localhost", "badass", "", "hacksmith");

  

 // $query = "SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 100 minute) AND ip= ?";

  $stmt = $connection->prepare("SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 3 minute) AND ip= ?");

  $stmt->bind_param("s", $_SERVER['REMOTE_ADDR']);

  $stmt->execute();

  $result = $stmt->get_result();

  $value1 = $result->fetch_row()[0] ?? false;



  $stmt = $connection->prepare("SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 4 minute) AND time < date_sub(now(), INTERVAL 1 minute) AND ip= ?");

  $stmt->bind_param("s", $_SERVER['REMOTE_ADDR']);

  $stmt->execute();

  $result = $stmt->get_result();

  $value2 = $result->fetch_row()[0] ?? false;



  $stmt = $connection->prepare("SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 5 minute) AND time < date_sub(now(), INTERVAL 2 minute) AND ip= ?");

  $stmt->bind_param("s", $_SERVER['REMOTE_ADDR']);

  $stmt->execute();

  $result = $stmt->get_result();

  $value3 = $result->fetch_row()[0] ?? false;



  $stmt = $connection->prepare("SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 6 minute) AND time < date_sub(now(), INTERVAL 3 minute) AND ip= ?");

  $stmt->bind_param("s", $_SERVER['REMOTE_ADDR']);

  $stmt->execute();

  $result = $stmt->get_result();

  $value4 = $result->fetch_row()[0] ?? false;



if ($value1 > 25 || $value2 > 25 || $value3 > 25 || $value4 > 25){

header('HTTP/1.1 429');

echo "Too Many Requests 3m policy hit \n";

//sleep for 300 seconds



//sleep(300);

}



}



function blockips1m(){

  global $countfile , $ipfile, $ipvalue, $ip, $connection;

  $connection = new mysqli("localhost", "badass", "", "hacksmith");

  

 // $query = "SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 100 minute) AND ip= ?";

  $stmt = $connection->prepare("SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 1 minute) AND ip= ?");

  $stmt->bind_param("s", $_SERVER['REMOTE_ADDR']);

  $stmt->execute();

  $result = $stmt->get_result();

  $value = $result->fetch_row()[0] ?? false;

//echo $value;

if ($value > 10){

header('HTTP/1.1 429');

echo "Too Many Requests 1m policy hit\n";

//sleep for 60 seconds



//sleep(60);

}



}



function blockips3m(){

  global $countfile , $ipfile, $ipvalue, $ip, $connection;

  $connection = new mysqli("localhost", "badass", "", "hacksmith");

  

 // $query = "SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 100 minute) AND ip= ?";

  $stmt = $connection->prepare("SELECT COUNT(ip) FROM hacksmith.rl where time > date_sub(now(), interval 3 minute) AND ip= ?");

  $stmt->bind_param("s", $_SERVER['REMOTE_ADDR']);

  $stmt->execute();

  $result = $stmt->get_result();

  $value = $result->fetch_row()[0] ?? false;

//echo $value;

if ($value > 22){

header('HTTP/1.1 429');

echo "Too Many Requests 3m policy hit \n";

//sleep for 300 seconds



//sleep(300);

}



}

$connection->close();
