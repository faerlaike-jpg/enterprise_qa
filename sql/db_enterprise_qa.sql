-- =============================================================
-- 企业内部知识库问答 Agent 系统 - 数据库初始化脚本
-- 数据库：db_enterprise_qa    MySQL 8.x    端口：3306
-- 说明：所有测试用户密码均为 123456，存储为 MD5 值
--       e10adc3949ba59abbe56e057f20f883e
-- =============================================================

CREATE DATABASE IF NOT EXISTS db_enterprise_qa
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE db_enterprise_qa;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- -------------------------------------------------------------
-- 1. 系统用户表
-- -------------------------------------------------------------
DROP TABLE IF EXISTS sys_user;
CREATE TABLE sys_user (
  id           INT          NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  username     VARCHAR(50)  NOT NULL COMMENT '登录账号',
  password     VARCHAR(64)  NOT NULL COMMENT '登录密码(MD5)',
  nickname     VARCHAR(50)  DEFAULT NULL COMMENT '昵称',
  role         VARCHAR(20)  NOT NULL DEFAULT 'user' COMMENT '角色：admin 管理员 / user 普通用户',
  avatar       VARCHAR(255) DEFAULT NULL COMMENT '头像地址',
  department   VARCHAR(50)  DEFAULT NULL COMMENT '所属部门',
  status       TINYINT      NOT NULL DEFAULT 1 COMMENT '状态：1 正常 / 0 禁用',
  create_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  update_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户表';

-- -------------------------------------------------------------
-- 2. 知识库表（每个知识库对应一个 Chroma collection）
-- -------------------------------------------------------------
DROP TABLE IF EXISTS knowledge_base;
CREATE TABLE knowledge_base (
  id               INT          NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  name             VARCHAR(100) NOT NULL COMMENT '知识库名称',
  description      VARCHAR(500) DEFAULT NULL COMMENT '知识库描述',
  collection_name  VARCHAR(63)  NOT NULL COMMENT 'Chroma集合名称',
  icon             VARCHAR(50)  DEFAULT 'Collection' COMMENT '图标名称',
  doc_count        INT          NOT NULL DEFAULT 0 COMMENT '文档数量',
  create_by        INT          DEFAULT NULL COMMENT '创建人ID',
  create_time      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  update_time      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_collection (collection_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识库表';

-- -------------------------------------------------------------
-- 3. 知识库文档表
-- -------------------------------------------------------------
DROP TABLE IF EXISTS kb_document;
CREATE TABLE kb_document (
  id           INT          NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  kb_id        INT          NOT NULL COMMENT '所属知识库ID',
  file_name    VARCHAR(255) NOT NULL COMMENT '原始文件名',
  file_path    VARCHAR(500) NOT NULL COMMENT '文件存储路径(相对backend-server)',
  file_type    VARCHAR(20)  NOT NULL COMMENT '文件类型：txt/md/pdf/docx',
  file_size    BIGINT       NOT NULL DEFAULT 0 COMMENT '文件大小(字节)',
  chunk_count  INT          NOT NULL DEFAULT 0 COMMENT '切分片段数',
  status       TINYINT      NOT NULL DEFAULT 0 COMMENT '状态：0 待处理 / 1 已完成 / 2 失败',
  error_msg    VARCHAR(500) DEFAULT NULL COMMENT '失败原因',
  upload_by    INT          DEFAULT NULL COMMENT '上传人ID',
  create_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  update_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_kb_id (kb_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识库文档表';

-- -------------------------------------------------------------
-- 4. 对话会话表
-- -------------------------------------------------------------
DROP TABLE IF EXISTS chat_session;
CREATE TABLE chat_session (
  id           INT          NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  user_id      INT          NOT NULL COMMENT '所属用户ID',
  kb_id        INT          DEFAULT NULL COMMENT '关联知识库ID',
  title        VARCHAR(200) NOT NULL DEFAULT '新对话' COMMENT '会话标题',
  create_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  update_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话会话表';

-- -------------------------------------------------------------
-- 5. 对话消息表
-- -------------------------------------------------------------
DROP TABLE IF EXISTS chat_message;
CREATE TABLE chat_message (
  id           INT          NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  session_id   INT          NOT NULL COMMENT '所属会话ID',
  role         VARCHAR(20)  NOT NULL COMMENT '角色：user 用户 / assistant 助手',
  content      LONGTEXT     NOT NULL COMMENT '消息内容',
  sources      JSON         DEFAULT NULL COMMENT '引用来源(JSON数组)',
  create_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_session_id (session_id),
  KEY idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话消息表';

-- -------------------------------------------------------------
-- 6. 回答反馈表（点赞 / 点踩）
-- -------------------------------------------------------------
DROP TABLE IF EXISTS feedback;
CREATE TABLE feedback (
  id           INT          NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  message_id   INT          NOT NULL COMMENT '消息ID',
  user_id      INT          NOT NULL COMMENT '用户ID',
  type         TINYINT      NOT NULL COMMENT '类型：1 点赞 / -1 点踩',
  create_time  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_msg_user (message_id, user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回答反馈表';

SET FOREIGN_KEY_CHECKS = 1;

-- =============================================================
-- 测试数据
-- =============================================================

-- 用户（密码均为 123456 的 MD5）
INSERT INTO sys_user (id, username, password, nickname, role, department, status, create_time) VALUES
(1, 'admin',    'e10adc3949ba59abbe56e057f20f883e', '系统管理员', 'admin', '信息技术部', 1, DATE_SUB(NOW(), INTERVAL 30 DAY)),
(2, 'zhangsan', 'e10adc3949ba59abbe56e057f20f883e', '张三',       'user',  '人力资源部', 1, DATE_SUB(NOW(), INTERVAL 20 DAY)),
(3, 'lisi',     'e10adc3949ba59abbe56e057f20f883e', '李四',       'user',  '财务部',     1, DATE_SUB(NOW(), INTERVAL 15 DAY)),
(4, 'wangwu',   'e10adc3949ba59abbe56e057f20f883e', '王五',       'user',  '研发中心',   1, DATE_SUB(NOW(), INTERVAL 10 DAY)),
(5, 'zhaoliu',  'e10adc3949ba59abbe56e057f20f883e', '赵六',       'user',  '市场部',     0, DATE_SUB(NOW(), INTERVAL 5 DAY));

-- 知识库
INSERT INTO knowledge_base (id, name, description, collection_name, icon, doc_count, create_by, create_time) VALUES
(1, '人事制度', '员工考勤、请假、薪酬福利、入离职等人事管理制度', 'kb_hr',      'User',     4, 1, DATE_SUB(NOW(), INTERVAL 28 DAY)),
(2, 'IT运维手册', 'VPN、邮箱、办公设备、账号权限等常见IT问题处理指南', 'kb_it',  'Monitor',  4, 1, DATE_SUB(NOW(), INTERVAL 25 DAY)),
(3, '财务报销', '差旅报销、费用标准、发票规范与报销流程说明', 'kb_finance', 'Wallet',   2, 1, DATE_SUB(NOW(), INTERVAL 22 DAY));

-- 文档（指向 backend-server/sample_docs 下的示例文件，状态为待处理，管理员可在后台一键向量化）
INSERT INTO kb_document (id, kb_id, file_name, file_path, file_type, file_size, chunk_count, status, upload_by, create_time) VALUES
(1, 1, '员工考勤与请假制度.md', 'sample_docs/员工考勤与请假制度.md', 'md', 2600, 0, 0, 1, DATE_SUB(NOW(), INTERVAL 27 DAY)),
(2, 1, '薪酬福利管理办法.md',   'sample_docs/薪酬福利管理办法.md',   'md', 2200, 0, 0, 1, DATE_SUB(NOW(), INTERVAL 26 DAY)),
(3, 2, 'VPN与网络使用指南.md',  'sample_docs/VPN与网络使用指南.md',  'md', 2000, 0, 0, 1, DATE_SUB(NOW(), INTERVAL 24 DAY)),
(4, 2, '办公设备与账号管理.md', 'sample_docs/办公设备与账号管理.md', 'md', 1900, 0, 0, 1, DATE_SUB(NOW(), INTERVAL 23 DAY)),
(5, 3, '差旅费用报销规范.md',   'sample_docs/差旅费用报销规范.md',   'md', 2400, 0, 0, 1, DATE_SUB(NOW(), INTERVAL 21 DAY)),
(6, 1, '新员工入职指引.md',           'sample_docs/新员工入职指引.md',           'md',   1711,  0, 0, 1, DATE_SUB(NOW(), INTERVAL 18 DAY)),
(7, 1, '员工行为规范与保密制度.pdf', 'sample_docs/员工行为规范与保密制度.pdf', 'pdf',  57135, 0, 0, 1, DATE_SUB(NOW(), INTERVAL 17 DAY)),
(8, 2, '会议室与打印设备使用说明.txt', 'sample_docs/会议室与打印设备使用说明.txt', 'txt', 1987, 0, 0, 1, DATE_SUB(NOW(), INTERVAL 16 DAY)),
(9, 2, '数据备份与故障处理手册.docx', 'sample_docs/数据备份与故障处理手册.docx', 'docx', 38309, 0, 0, 1, DATE_SUB(NOW(), INTERVAL 15 DAY)),
(10, 3, '业务招待与日常费用报销.docx', 'sample_docs/业务招待与日常费用报销.docx', 'docx', 38122, 0, 0, 1, DATE_SUB(NOW(), INTERVAL 14 DAY));

-- 会话
INSERT INTO chat_session (id, user_id, kb_id, title, create_time, update_time) VALUES
(1, 2, 1, '年假怎么计算',         DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY)),
(2, 3, 3, '出差住宿报销标准',     DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
(3, 4, 2, 'VPN连不上怎么办',      DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY)),
(4, 2, 1, '病假需要什么材料',     DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),
(5, 4, 2, '忘记邮箱密码',         DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY)),
(6, 3, 3, '发票抬头要求',         DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
(7, 1, 1, '加班调休规则',         NOW(), NOW());

-- 消息
INSERT INTO chat_message (session_id, role, content, sources, create_time) VALUES
(1, 'user',      '我入职满3年了，年假有几天？', NULL, DATE_SUB(NOW(), INTERVAL 6 DAY)),
(1, 'assistant', '根据《员工考勤与请假制度》，累计工作满1年不满10年的员工，每年可享受**5天**带薪年假；公司在此基础上，司龄每满1年额外增加1天，最多不超过15天。因此您目前可享受约 **7天** 年假。', '[{"file_name":"员工考勤与请假制度.md","content":"累计工作已满1年不满10年的，年休假5天……"}]', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(2, 'user',      '去上海出差，住宿费报销标准是多少？', NULL, DATE_SUB(NOW(), INTERVAL 5 DAY)),
(2, 'assistant', '根据《差旅费用报销规范》，一线城市（北京、上海、广州、深圳）普通员工住宿标准为 **每晚500元**，经理级为 **每晚650元**，超出部分需自行承担。', '[{"file_name":"差旅费用报销规范.md","content":"一线城市：普通员工500元/晚……"}]', DATE_SUB(NOW(), INTERVAL 5 DAY)),
(3, 'user',      'VPN一直连不上怎么办？', NULL, DATE_SUB(NOW(), INTERVAL 4 DAY)),
(3, 'assistant', '请按以下步骤排查：\n1. 确认本地网络正常；\n2. 检查VPN客户端是否为最新版本；\n3. 确认账号未过期；\n4. 仍无法解决请联系IT服务台，分机 8000。', '[{"file_name":"VPN与网络使用指南.md","content":"常见问题：无法连接VPN……"}]', DATE_SUB(NOW(), INTERVAL 4 DAY)),
(3, 'user',      'VPN支持手机吗？', NULL, DATE_SUB(NOW(), INTERVAL 4 DAY)),
(3, 'assistant', '支持。可在应用商店下载公司指定的VPN客户端，使用域账号登录即可。', NULL, DATE_SUB(NOW(), INTERVAL 4 DAY)),
(4, 'user',      '请病假需要提交什么材料？', NULL, DATE_SUB(NOW(), INTERVAL 3 DAY)),
(4, 'assistant', '病假1天以内可凭口头说明后补系统申请；连续2天及以上需提供二级以上医院出具的**病假证明**及病历。', NULL, DATE_SUB(NOW(), INTERVAL 3 DAY)),
(5, 'user',      '忘记企业邮箱密码怎么重置？', NULL, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(5, 'assistant', '可通过统一身份认证平台的“忘记密码”功能，使用绑定手机号验证后自助重置。', NULL, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(5, 'user',      '新员工电脑怎么申请？', NULL, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(5, 'assistant', '由部门助理在OA系统提交《办公设备申领单》，IT部门审批后3个工作日内发放。', NULL, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(6, 'user',      '报销发票抬头有什么要求？', NULL, DATE_SUB(NOW(), INTERVAL 1 DAY)),
(6, 'assistant', '发票抬头须为公司全称，并填写正确的纳税人识别号，否则财务将不予受理。', NULL, DATE_SUB(NOW(), INTERVAL 1 DAY)),
(7, 'user',      '周末加班可以调休吗？', NULL, NOW()),
(7, 'assistant', '可以。周末加班经审批后可按1:1申请调休，调休需在加班后3个月内使用完毕。', NULL, NOW());

-- 反馈
INSERT INTO feedback (message_id, user_id, type) VALUES
(2, 2, 1), (4, 3, 1), (6, 4, 1), (10, 2, -1);
