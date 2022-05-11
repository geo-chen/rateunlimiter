<?php

$db="rl";
$db_user="rl";
$db_pass="isactuallyzero?";

$reqid = $_REQUEST['reqid'] ?? '';

function countint()
{
    global $connection, $db_user, $db_pass, $db, $reqid;
    $connection = new mysqli("localhost", $db_user, $db_pass, $db);
    if ($connection->errno)
    {
        printf("Connect failed: %s\n", $connection->error);
        exit();
    }
    // echo 'Connected to the database.<br>';
    $stmt = $connection->prepare("INSERT INTO rl.sim (ip, reqid, ts) values (?,?,NOW())");
    $stmt->bind_param('ss', $_SERVER['REMOTE_ADDR'], $reqid);
    if ($result = $stmt->execute())
    {
        // echo "success";
        $stmt->free_result();
    }
    else
    {
        echo $connection->error;
    }
}
// checkblocks();
policy2();
policy1();
countint();


/* 

function checkblocks() {
    // check table, if current time <= block_expiry:
    // header("HTTP/1.1 429");
    // return;
}
*/

function policy1()
{
    global $connection, $db_user, $db_pass, $db, $reqid;
    $connection = new mysqli("localhost", $db_user, $db_pass, $db);
    // $query = "SELECT COUNT(ip) FROM rl.sim where ts > date_sub(now(), interval 100 minute) AND ip= ?";
    $stmt = $connection->prepare("SELECT COUNT(ip) FROM rl.sim where ts > date_sub(now(), interval 1 minute) AND ip=? AND reqid=?");
    $stmt->bind_param('ss', $_SERVER['REMOTE_ADDR'], $reqid);
    $stmt->execute();
    $result = $stmt->get_result();
    $value1 = $result->fetch_row() [0]??false;
    $stmt = $connection->prepare("SELECT COUNT(ip) FROM rl.sim where ts > date_sub(now(), interval 120 second) AND ts < date_sub(now(), INTERVAL 60 SECOND) AND ip=? AND reqid=?");
    $stmt->bind_param('ss', $_SERVER['REMOTE_ADDR'], $reqid);
    $stmt->execute();
    $result = $stmt->get_result();
    $value2 = $result->fetch_row() [0]??false;
    if ($value1 > 10 || $value2 > 10)
    {
        header('HTTP/1.1 429');
// insert block entry into new table, expiry now + 1 min
        echo "Too Many Requests 1m policy hit\n";
    }
}

function policy2()
{
    global $connection, $db_user, $db_pass, $db, $reqid;
    $threshold2 = 18; // MODIFY THIS
    $connection = new mysqli("localhost", $db_user, $db_pass, $db);
    // $query = "SELECT COUNT(ip) FROM rl.sim where ts > date_sub(now(), interval 100 minute) AND ip= ?";
    $stmt = $connection->prepare("SELECT COUNT(ip) FROM rl.sim where ts > date_sub(now(), interval 3 minute) AND ip=? AND reqid=?");
    $stmt->bind_param('ss', $_SERVER['REMOTE_ADDR'], $reqid);
    $stmt->execute();
    $result = $stmt->get_result();
    $value1 = $result->fetch_row() [0]??false;
    $stmt = $connection->prepare("SELECT COUNT(ip) FROM rl.sim where ts > date_sub(now(), interval 4 minute) AND ts < date_sub(now(), INTERVAL 1 minute) AND ip=? AND reqid=?");
    $stmt->bind_param('ss', $_SERVER['REMOTE_ADDR'], $reqid);
    $stmt->execute();
    $result = $stmt->get_result();
    $value2 = $result->fetch_row() [0]??false;
    $stmt = $connection->prepare("SELECT COUNT(ip) FROM rl.sim where ts > date_sub(now(), interval 5 minute) AND ts < date_sub(now(), INTERVAL 2 minute) AND ip=? AND reqid=?");
    $stmt->bind_param('ss', $_SERVER['REMOTE_ADDR'], $reqid);
    $stmt->execute();
    $result = $stmt->get_result();
    $value3 = $result->fetch_row() [0]??false;
    $stmt = $connection->prepare("SELECT COUNT(ip) FROM rl.sim where ts > date_sub(now(), interval 6 minute) AND ts < date_sub(now(), INTERVAL 3 minute) AND ip=? AND reqid=?");
    $stmt->bind_param('ss', $_SERVER['REMOTE_ADDR'], $reqid);
    $stmt->execute();
    $result = $stmt->get_result();
    $value4 = $result->fetch_row() [0]??false;
    if ($value1 > $threshold2 || $value2 > $threshold2 || $value3 > $threshold2 || $value4 > $threshold2)
    {
        header('HTTP/1.1 429');
        echo "Too Many Requests 3m policy hit \n";
        //sleep for 300 seconds
        //sleep(300);        
    }
}

function blockips1m()
{
    global $connection, $db_user, $db_pass, $db, $reqid;
    $connection = new mysqli("localhost", $db_user, $db_pass, $db);
    // $query = "SELECT COUNT(ip) FROM rl.sim where ts > date_sub(now(), interval 100 minute) AND ip= ?";
    $stmt = $connection->prepare("SELECT COUNT(ip) FROM rl.sim where ts > date_sub(now(), interval 1 minute) AND ip=? AND reqid=?");
    $stmt->bind_param('ss', $_SERVER['REMOTE_ADDR'], $reqid);
    $stmt->execute();
    $result = $stmt->get_result();
    $value = $result->fetch_row() [0]??false;
    //echo $value;
    if ($value > 10)
    {
        header('HTTP/1.1 429');
        echo "Too Many Requests 1m policy hit\n";
        //sleep for 60 seconds
        //sleep(60);
    }
}

function blockips3m()
{
    global $connection, $db_user, $db_pass, $db, $reqid;
    $connection = new mysqli("localhost", $db_user, $db_pass, $db);
    // $query = "SELECT COUNT(ip) FROM rl.sim where ts > date_sub(now(), interval 100 minute) AND ip= ?";
    $stmt = $connection->prepare("SELECT COUNT(ip) FROM rl.sim where ts > date_sub(now(), interval 3 minute) AND ip=? AND reqid=?");
    $stmt->bind_param('ss', $_SERVER['REMOTE_ADDR'], $reqid);
    $stmt->execute();
    $result = $stmt->get_result();
    $value = $result->fetch_row() [0]??false;
    //echo $value;
    if ($value > 22)
    {
        header('HTTP/1.1 429');
        echo "Too Many Requests 3m policy hit \n";
        //sleep for 300 seconds
        //sleep(300);
    }
}

$connection->close();
