-- OCHAT MySQL schema, used by normal runs.

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(20) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(32) NOT NULL,
    avatar VARCHAR(255) NOT NULL DEFAULT '',
    signature VARCHAR(120) NOT NULL DEFAULT '',
    contact VARCHAR(80) NOT NULL DEFAULT '',
    birthday VARCHAR(20) NOT NULL DEFAULT '',
    gender VARCHAR(16) NOT NULL DEFAULT '',
    address VARCHAR(160) NOT NULL DEFAULT '',
    age INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS friendships (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    friend_id INT NOT NULL,
    remark VARCHAR(32) NOT NULL DEFAULT '',
    group_name VARCHAR(32) NOT NULL DEFAULT 'Friends',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_friendships_pair (user_id, friend_id),
    INDEX idx_friendships_user (user_id),
    CONSTRAINT fk_friendships_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_friendships_friend FOREIGN KEY(friend_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS friend_requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    requester_id INT NOT NULL,
    receiver_id INT NOT NULL,
    message VARCHAR(240) NOT NULL DEFAULT '',
    status ENUM('pending', 'accepted', 'rejected') NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    responded_at DATETIME NULL,
    UNIQUE KEY uk_friend_requests_open (requester_id, receiver_id, status),
    INDEX idx_friend_requests_receiver (receiver_id, status),
    INDEX idx_friend_requests_requester (requester_id, status),
    CONSTRAINT fk_friend_requests_requester FOREIGN KEY(requester_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_friend_requests_receiver FOREIGN KEY(receiver_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS chat_groups (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(40) NOT NULL,
    owner_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_chat_groups_owner (owner_id),
    CONSTRAINT fk_chat_groups_owner FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS group_members (
    id INT PRIMARY KEY AUTO_INCREMENT,
    group_id INT NOT NULL,
    user_id INT NOT NULL,
    role VARCHAR(16) NOT NULL DEFAULT 'member',
    role_order INT NOT NULL DEFAULT 0,
    alias VARCHAR(32) NOT NULL DEFAULT '',
    group_remark VARCHAR(120) NOT NULL DEFAULT '',
    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_group_members_pair (group_id, user_id),
    INDEX idx_group_members_user (user_id),
    CONSTRAINT fk_group_members_group FOREIGN KEY(group_id) REFERENCES chat_groups(id) ON DELETE CASCADE,
    CONSTRAINT fk_group_members_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS group_invitations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    group_id INT NOT NULL,
    inviter_id INT NOT NULL,
    receiver_id INT NOT NULL,
    message VARCHAR(240) NOT NULL DEFAULT '',
    status ENUM('pending', 'accepted', 'rejected') NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    responded_at DATETIME NULL,
    UNIQUE KEY uk_group_invitations_open (group_id, receiver_id, status),
    INDEX idx_group_invitations_receiver (receiver_id, status),
    INDEX idx_group_invitations_group (group_id, status),
    CONSTRAINT fk_group_invitations_group FOREIGN KEY(group_id) REFERENCES chat_groups(id) ON DELETE CASCADE,
    CONSTRAINT fk_group_invitations_inviter FOREIGN KEY(inviter_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_group_invitations_receiver FOREIGN KEY(receiver_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS files (
    id INT PRIMARY KEY AUTO_INCREMENT,
    uploader_id INT NOT NULL,
    original_name VARCHAR(120) NOT NULL,
    storage_name VARCHAR(180) NOT NULL UNIQUE,
    size INT NOT NULL,
    mime_type VARCHAR(80) NOT NULL DEFAULT 'application/octet-stream',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_files_uploader (uploader_id),
    CONSTRAINT fk_files_uploader FOREIGN KEY(uploader_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT NOT NULL,
    conversation_type ENUM('direct', 'group') NOT NULL,
    target_id INT NOT NULL,
    message_type VARCHAR(16) NOT NULL DEFAULT 'text',
    content TEXT NOT NULL,
    file_id INT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'sent',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_messages_direct (conversation_type, sender_id, target_id),
    INDEX idx_messages_group (conversation_type, target_id),
    FULLTEXT INDEX idx_messages_content (content),
    CONSTRAINT fk_messages_sender FOREIGN KEY(sender_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_messages_file FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS message_reads (
    user_id INT NOT NULL,
    message_id INT NOT NULL,
    read_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(user_id, message_id),
    INDEX idx_message_reads_message (message_id),
    CONSTRAINT fk_message_reads_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_message_reads_message FOREIGN KEY(message_id) REFERENCES messages(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
