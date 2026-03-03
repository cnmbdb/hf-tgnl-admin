-- MySQL dump 10.13  Distrib 8.0.24, for Linux (x86_64)
--
-- Host: localhost    Database: nl-admin
-- ------------------------------------------------------
-- Server version	8.0.24

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `tgnl`
--

CREATE DATABASE IF NOT EXISTS `tgnl` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `tgnl`;

--
-- Table structure for table `license_history`
--

DROP TABLE IF EXISTS `license_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `license_history` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `order_number` varchar(255) NOT NULL COMMENT '订单号',
  `action` enum('activate','deactivate','renew','expire') NOT NULL COMMENT '操作类型',
  `server_ip` varchar(50) DEFAULT NULL COMMENT '服务器IP',
  `details` text COMMENT '操作详情',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`id`),
  KEY `idx_order_number` (`order_number`),
  KEY `idx_action` (`action`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='授权操作历史表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `license_history`
--

LOCK TABLES `license_history` WRITE;
/*!40000 ALTER TABLE `license_history` DISABLE KEYS */;
-- 初始化时不插入授权历史记录
/*!40000 ALTER TABLE `license_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `licenses`
--

DROP TABLE IF EXISTS `licenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `licenses` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `order_number` varchar(255) NOT NULL COMMENT '订单号',
  `order_id` varchar(255) DEFAULT NULL COMMENT 'WordPress订单ID',
  `email` varchar(255) DEFAULT NULL COMMENT '客户邮箱',
  `customer_name` varchar(255) DEFAULT NULL COMMENT '客户姓名',
  `product_info` text COMMENT '产品信息(JSON)',
  `license_type` enum('standard','professional','enterprise','monthly','yearly') DEFAULT 'standard' COMMENT '授权类型',
  `status` enum('active','inactive','expired') DEFAULT 'inactive' COMMENT '授权状态',
  `activated_at` datetime DEFAULT NULL COMMENT '激活时间',
  `expiry_date` date DEFAULT NULL COMMENT '到期日期',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_number` (`order_number`),
  KEY `idx_order_number` (`order_number`),
  KEY `idx_email` (`email`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='授权许可证表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `licenses`
--

LOCK TABLES `licenses` WRITE;
/*!40000 ALTER TABLE `licenses` DISABLE KEYS */;
-- 初始化时不插入授权记录，用户需要自行激活
/*!40000 ALTER TABLE `licenses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_number` varchar(100) NOT NULL,
  `chat_id` bigint NOT NULL,
  `username` varchar(255) DEFAULT NULL,
  `plan` varchar(100) DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL DEFAULT '0.00',
  `status` varchar(50) NOT NULL DEFAULT 'pending',
  `payment_method` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_number` (`order_number`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,'ORD-CHZ-20251101-001',276600603,'test_user','充值TRX',100.50,'completed','USDT','2025-11-01 02:23:15','2025-11-01 02:23:15'),(2,'ORD-CHZ-20251102-002',825512163,'HFTGID','充值TRX',50.00,'completed','TRX','2025-11-02 06:35:22','2025-11-02 06:35:22'),(3,'ORD-CHZ-20251103-003',923284681,'AER00001','充值TRX',200.00,'pending','USDT','2025-11-03 01:15:33','2025-11-03 01:15:33'),(4,'ORD-CHZ-20251104-004',6833491453,'ccy888888888','充值TRX',30.00,'completed','TRX','2025-11-04 08:45:12','2025-11-04 08:45:12'),(5,'ORD-CHZ-20251105-005',5987552454,'swcl857','充值TRX',150.00,'completed','USDT','2025-11-05 03:20:45','2025-11-05 03:20:45'),(6,'ORD-YCK-20251101-006',276600603,'test_user','预存扣费-自动充能',5.00,'completed','预存余额','2025-11-01 07:30:00','2025-11-01 07:30:00'),(7,'ORD-YCK-20251102-007',825512163,'HFTGID','预存扣费-自动充能',5.00,'completed','预存余额','2025-11-02 10:22:11','2025-11-02 10:22:11'),(8,'ORD-YCK-20251103-008',5987552454,'swcl857','预存扣费-自动充能',5.00,'completed','预存余额','2025-11-03 04:45:30','2025-11-03 04:45:30'),(9,'ORD-YCK-20251104-009',6833491453,'ccy888888888','预存扣费-自动充能',5.00,'completed','预存余额','2025-11-04 12:15:22','2025-11-04 12:15:22'),(10,'ORD-YCK-20251105-010',923284681,'AER00001','预存扣费-自动充能',5.00,'completed','预存余额','2025-11-05 00:30:45','2025-11-05 00:30:45'),(11,'ORD-NLT-20251101-011',276600603,'test_user','能量套餐-65000能量',3.50,'completed','账户余额','2025-11-01 08:10:20','2025-11-01 08:10:20'),(12,'ORD-NLT-20251102-012',825512163,'HFTGID','能量套餐-130000能量',6.80,'completed','账户余额','2025-11-02 11:25:33','2025-11-02 11:25:33'),(13,'ORD-NLT-20251103-013',5987552454,'swcl857','能量套餐-65000能量',3.50,'completed','账户余额','2025-11-03 05:40:15','2025-11-03 05:40:15'),(14,'ORD-NLT-20251104-014',6833491453,'ccy888888888','能量套餐-195000能量',10.20,'pending','账户余额','2025-11-04 13:55:40','2025-11-04 13:55:40'),(15,'ORD-NLT-20251105-015',923284681,'AER00001','能量套餐-65000能量',3.50,'cancelled','账户余额','2025-11-05 01:20:12','2025-11-05 01:22:30'),(16,'ORD-NLT-20251106-016',5158269587,'jnd28_vip','能量套餐-130000能量',6.80,'completed','账户余额','2025-11-06 06:30:25','2025-11-06 06:30:25'),(17,'ORD-NLT-20251107-017',2064967864,'mableb','能量套餐-65000能量',3.50,'completed','账户余额','2025-11-07 02:15:50','2025-11-07 02:15:50'),(18,'ORD-CHZ-20251106-018',5158269587,'jnd28_vip','充值TRX',80.00,'completed','USDT','2025-11-06 05:25:18','2025-11-06 05:25:18'),(19,'ORD-CHZ-20251107-019',2064967864,'mableb','充值TRX',60.00,'completed','TRX','2025-11-07 01:40:35','2025-11-07 01:40:35'),(20,'ORD-CHZ-20251107-020',5453498619,'MonkeyMonkeyhappy','充值TRX',120.00,'pending','USDT','2025-11-07 03:55:20','2025-11-07 03:55:20');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_configs`
--

DROP TABLE IF EXISTS `system_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_configs` (
  `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'UUID主键',
  `config_key` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置键',
  `config_value` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '配置值',
  `updated_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '更新者',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_configs`
--

LOCK TABLES `system_configs` WRITE;
/*!40000 ALTER TABLE `system_configs` DISABLE KEYS */;
INSERT INTO `system_configs` VALUES ('099d720f-80ee-481e-aa5e-b047b5a3e8db','adminEmail','admin@hfcloud.com','d3dbc343-5d77-49c5-a538-014565764a77','2025-09-14 00:26:03'),('360aa343-eb22-4d2b-b155-cc4f424ff790','maintenanceMode','false','d3dbc343-5d77-49c5-a538-014565764a77','2025-09-14 00:26:03'),('4de61f8c-7a3e-4fa6-99c6-a4a8cbfdb868','faviconUrl','/favicon.ico','d3dbc343-5d77-49c5-a538-014565764a77','2025-09-14 00:26:03'),('7a48bc4c-8737-4686-ba71-4731d461f636','announcement','欢迎使用 HFCloud 系统','d3dbc343-5d77-49c5-a538-014565764a77','2025-09-14 00:26:03'),('8c0f497a-10ba-4cee-b941-ec9bf7a979b8','logoSize','128','d3dbc343-5d77-49c5-a538-014565764a77','2025-09-14 00:26:03'),('a45cf867-c0c7-450a-8ca3-0d7d27eb1c98','logoUrl','https://hfstore.xyz/wp-content/uploads/2025/08/未命名-份-份-份-份-份-16.png','d3dbc343-5d77-49c5-a538-014565764a77','2025-09-14 00:26:03'),('c1e6ba59-876b-4bef-888a-cfb74235ce02','systemName','HFCloud 系统','d3dbc343-5d77-49c5-a538-014565764a77','2025-09-14 00:26:03');
/*!40000 ALTER TABLE `system_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_users`
--

DROP TABLE IF EXISTS `system_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `role` enum('admin','user') NOT NULL DEFAULT 'user',
  `status` enum('active','inactive') NOT NULL DEFAULT 'active',
  `last_login` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_users`
--

LOCK TABLES `system_users` WRITE;
/*!40000 ALTER TABLE `system_users` DISABLE KEYS */;
INSERT INTO `system_users` VALUES (1,'admin','e4bc385e124d61823445cbd9720c82cd:98308327583cb8e20cd7eb547428e5f20aabe7bacafd1c631a9089307fbdcd156c045fae09f7adf79c825e05bf872eadae89e192111e9db0f533047c11911fd6','admin@example.com','admin','active','2025-11-21 01:08:59','2025-11-06 13:27:35','2025-11-24 01:24:48');
/*!40000 ALTER TABLE `system_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `chat_id` bigint NOT NULL,
  `user_nickname` varchar(255) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  `amount` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `user_sessions`
--

DROP TABLE IF EXISTS `user_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_token` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `expires_at` timestamp NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_token` (`session_token`),
  KEY `idx_session_token` (`session_token`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_expires_at` (`expires_at`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_sessions`
--

LOCK TABLES `user_sessions` WRITE;
/*!40000 ALTER TABLE `user_sessions` DISABLE KEYS */;
INSERT INTO `user_sessions` VALUES (1,'d3dbc343-5d77-49c5-a538-014565764a77','nqr1quzcf9mfwyc1oz','2025-09-30 19:32:12','2025-09-23 19:32:13');
/*!40000 ALTER TABLE `user_sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'UUID主键',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '邮箱',
  `password_hash` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码哈希',
  `role` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'user' COMMENT '角色',
  `role_label` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '普通用户' COMMENT '角色标签',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'active' COMMENT '状态',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_role` (`role`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('8e853808-0336-49d2-a415-746f1d2da754','admin','admin@hfcloud.com','admin123','admin','管理员','active','2025-08-07 17:15:11','2025-10-14 05:08:13','$2b$10$n0rBljothcdIpkDG5SYMNeTgH9psXrz6nU7PjNwnrEiNpjjKPPETq'),('afa5af83-a822-11f0-b77d-525400ec1c03','test','test@example.com','test123','admin','普通用户','active','2025-10-13 10:52:17','2025-10-13 10:52:17',''),('fdb081b7-7682-4a30-acfa-1af64ac6d81b','user1','user1@hfcloud.com','admin123','user','普通用户','active','2025-08-07 17:15:11','2025-08-07 17:15:11','');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bishu_packages`
--

DROP TABLE IF EXISTS `bishu_packages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bishu_packages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `chat_id` bigint NOT NULL COMMENT '用户Telegram ID',
  `address` varchar(64) NOT NULL COMMENT '绑定的钱包地址',
  `package_type` varchar(20) NOT NULL COMMENT '套餐类型: 5笔/15T, 15笔/45T, 50笔/150T等',
  `package_count` int NOT NULL COMMENT '笔数',
  `package_energy` int NOT NULL COMMENT '能量数量',
  `status` enum('active','inactive','sleeping') NOT NULL DEFAULT 'active' COMMENT '状态: active-激活, inactive-关闭, sleeping-休眠',
  `last_transfer_time` datetime DEFAULT NULL COMMENT '最后一次转账时间',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_chat_id` (`chat_id`),
  KEY `idx_address` (`address`),
  KEY `idx_status` (`status`),
  KEY `idx_last_transfer_time` (`last_transfer_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='笔数套餐表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bishu_packages`
--

LOCK TABLES `bishu_packages` WRITE;
/*!40000 ALTER TABLE `bishu_packages` DISABLE KEYS */;
/*!40000 ALTER TABLE `bishu_packages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'nl-admin'
--

--
-- Dumping routines for database 'nl-admin'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-19 13:58:02
