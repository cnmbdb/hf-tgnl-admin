-- 创建 tg_users 表
CREATE TABLE IF NOT EXISTS `tg_users` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `tg_user_id` bigint NOT NULL COMMENT 'Telegram用户ID',
  `username` varchar(255) DEFAULT NULL COMMENT 'Telegram用户名',
  `first_name` varchar(255) DEFAULT NULL COMMENT '名',
  `last_name` varchar(255) DEFAULT NULL COMMENT '姓',
  `phone_number` varchar(50) DEFAULT NULL COMMENT '手机号',
  `is_bot` tinyint(1) DEFAULT 0 COMMENT '是否为机器人',
  `is_premium` tinyint(1) DEFAULT 0 COMMENT '是否为Premium用户',
  `language_code` varchar(10) DEFAULT 'en' COMMENT '语言代码',
  `status` enum('active','banned','inactive') DEFAULT 'active' COMMENT '状态',
  `membership_type` enum('free','vip','premium') DEFAULT 'free' COMMENT '会员类型',
  `membership_expires` datetime DEFAULT NULL COMMENT '会员到期时间',
  `last_activity` datetime DEFAULT NULL COMMENT '最后活跃时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `tg_user_id` (`tg_user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_membership_type` (`membership_type`),
  KEY `idx_last_activity` (`last_activity`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Telegram用户表';
