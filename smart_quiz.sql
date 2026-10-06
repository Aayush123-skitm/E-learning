-- MySQL dump 10.13  Distrib 5.5.28, for Win64 (x86)
--
-- Host: localhost    Database: mydb
-- ------------------------------------------------------
-- Server version	5.5.28

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin` (
  `Name` varchar(70) DEFAULT NULL,
  `Email` varchar(70) DEFAULT NULL,
  `set_pss` varchar(70) DEFAULT NULL,
  `secu_ans` varchar(70) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES ('Aayush Tamboliya','Aayu123@gmail.com','skitmaiml24','01nov2005'),('Vishnu Dangaya','Vish123@gmail.com','skitmaiml24','02sep2004'),('test',NULL,'kk','os01');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `certificate`
--

DROP TABLE IF EXISTS `certificate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `certificate` (
  `certi_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) DEFAULT NULL,
  `subject` varchar(70) DEFAULT NULL,
  `score` int(11) DEFAULT NULL,
  `status` varchar(30) DEFAULT NULL,
  `certi_file` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`certi_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `certificate`
--

LOCK TABLES `certificate` WRITE;
/*!40000 ALTER TABLE `certificate` DISABLE KEYS */;
INSERT INTO `certificate` VALUES (1,2,'python',4,'PASS','c:\\Users\\a\\OneDrive\\Desktop\\vs code 1st python\\minor hu me\\certificates\\Krishna dadda_python.pdf'),(2,4,'cpp',4,'PASS','c:\\Users\\a\\OneDrive\\Desktop\\vs code 1st python\\minor hu me\\certificates\\Harshit Minare_cpp.pdf'),(5,10,'python',5,'PASS','c:\\Users\\a\\OneDrive\\Desktop\\vs code 1st python\\minor hu me\\certificates\\nick_python.pdf'),(6,10,'aptitude',3,'PASS','c:\\Users\\a\\OneDrive\\Desktop\\vs code 1st python\\minor hu me\\certificates\\nick_aptitude.pdf'),(7,10,'dbms',5,'PASS','c:\\Users\\a\\OneDrive\\Desktop\\vs code 1st python\\minor hu me\\certificates\\nick_dbms.pdf'),(8,11,'python',4,'PASS','c:\\Users\\a\\OneDrive\\Desktop\\vs code 1st python\\minor hu me\\certificates\\saa_python.pdf'),(9,10,'cpp',3,'PASS','c:\\Users\\a\\OneDrive\\Desktop\\vs code 1st python\\minor hu me\\certificates\\nick_cpp.pdf'),(10,10,'c',4,'PASS','c:\\Users\\a\\OneDrive\\Desktop\\vs code 1st python\\minor hu me\\certificates\\nick_c.pdf');
/*!40000 ALTER TABLE `certificate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `result`
--

DROP TABLE IF EXISTS `result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `result` (
  `result_id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) DEFAULT NULL,
  `subject` varchar(70) DEFAULT NULL,
  `tq` int(11) DEFAULT NULL,
  `score` int(11) DEFAULT NULL,
  `percentage` int(11) DEFAULT NULL,
  `time_taken` int(11) DEFAULT NULL,
  `status` varchar(30) DEFAULT NULL,
  `medium` varchar(40) DEFAULT NULL,
  `name` varchar(70) DEFAULT NULL,
  `st_0f_certi` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`result_id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `result`
--

LOCK TABLES `result` WRITE;
/*!40000 ALTER TABLE `result` DISABLE KEYS */;
INSERT INTO `result` VALUES (22,2,'python',5,4,75,23,'PASS','EASY','Krishna dadda','Genrated'),(23,4,'cpp',5,4,75,39,'PASS','EASY','Harshit Minare','Genrated'),(26,10,'python',5,5,100,30,'PASS','EASY','nick','Genrated'),(27,10,'aptitude',5,3,55,52,'PASS','EASY','nick','Genrated'),(28,10,'dbms',5,5,100,42,'PASS','EASY','nick','Genrated'),(29,4,'cpp',5,5,100,39,'PASS','EASY','Harshit Minare','Genrated'),(30,11,'python',5,4,80,25,'PASS','EASY','saa','Genrated'),(31,10,'cpp',5,3,50,35,'PASS','EASY','nick','Genrated'),(32,10,'c',5,4,75,34,'PASS','EASY','nick','Genrated');
/*!40000 ALTER TABLE `result` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `students` (
  `student_id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(60) DEFAULT NULL,
  `Email` varchar(60) DEFAULT NULL,
  `set_pss` varchar(60) DEFAULT NULL,
  `ph_no` int(11) DEFAULT NULL,
  `clg_name` varchar(100) DEFAULT NULL,
  `course` varchar(60) DEFAULT NULL,
  `secu_ans` varchar(60) DEFAULT NULL,
  `subject` varchar(60) DEFAULT NULL,
  `photo` varchar(500) DEFAULT NULL,
  `branch` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (2,'Krishna Dantlaya','kd@gmail.com','dhar@123',57,'smriti','pharmacy','13nov2002',NULL,'st_photo/Krishna Dantlaya.jpg','b.pharm'),(3,'Aayush Tamboliya','at123@gmail.com','dhar@123',1,'Skitm','b.tech','01nov2005',NULL,'st_photo/Aayush Tamboliya.jpg','aiml'),(4,'Harshit Minare','har123@gmail.com','dhar@123',29,'smriti','pharmacy','09nov2005',NULL,'st_photo/Harshit Minare.jpg','b.pharm'),(10,'nick','nick123@gmail.com','8989',1,'skitm','b.tech','01nov2005',NULL,'c:\\Users\\a\\OneDrive\\Desktop\\vs code 1st python\\minor hu me\\sample ke photo\\nick','aiml'),(11,'saa','sawan@gmail.com','Sawan@1234',12,'cdgi','b','ss90id',NULL,'c:\\Users\\a\\OneDrive\\Desktop\\vs code 1st python\\minor hu me\\sample ke photo\\saa','s');
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-02 22:57:03
