-- 用户账号表（可重复执行：先删后建）
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY          COMMENT '用户ID',
    username      VARCHAR(50)  NOT NULL UNIQUE            COMMENT '用户名（唯一）',
    password_hash VARCHAR(255) NOT NULL                   COMMENT '加盐密码哈希（绝不存明文）',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户账号';
