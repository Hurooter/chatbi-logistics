-- 会话元数据表（可重复执行：先删后建）
DROP TABLE IF EXISTS conversations;

CREATE TABLE conversations (
    thread_id  VARCHAR(64)  NOT NULL PRIMARY KEY          COMMENT '会话标识（给 LangGraph 当 thread_id）',
    user_id    INT          NOT NULL                      COMMENT '归属用户',
    title      VARCHAR(100) NOT NULL DEFAULT '新会话'      COMMENT '会话标题',
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后活跃',
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会话元数据';
