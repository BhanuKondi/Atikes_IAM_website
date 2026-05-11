-- ATIKES IAM Community MySQL schema and starter data
-- Import example:
--   mysql -u root -p < atikes_mysql_schema_seed.sql

CREATE DATABASE IF NOT EXISTS atikes_iam
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE atikes_iam;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `answer`;
DROP TABLE IF EXISTS `question_attachment`;
DROP TABLE IF EXISTS `question`;
DROP TABLE IF EXISTS `expert_profile`;
DROP TABLE IF EXISTS `trend`;
DROP TABLE IF EXISTS `trend_source`;
DROP TABLE IF EXISTS `upcoming_event`;
DROP TABLE IF EXISTS `user`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(120) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `title` VARCHAR(160) DEFAULT 'IAM Community Member',
  `company` VARCHAR(160) DEFAULT '',
  `bio` TEXT,
  `role` VARCHAR(30) DEFAULT 'user',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_email` (`email`),
  KEY `ix_user_email` (`email`),
  KEY `ix_user_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `trend_source` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(160) NOT NULL,
  `feed_url` VARCHAR(500) NOT NULL,
  `website_url` VARCHAR(500) DEFAULT '',
  `category` VARCHAR(120) NOT NULL,
  `is_active` BOOLEAN DEFAULT TRUE,
  `last_fetched_at` DATETIME NULL,
  `last_error` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_trend_source_name` (`name`),
  UNIQUE KEY `uq_trend_source_feed_url` (`feed_url`),
  KEY `ix_trend_source_category` (`category`),
  KEY `ix_trend_source_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `trend` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(300) NOT NULL,
  `summary` TEXT,
  `generated_content` TEXT,
  `image_url` VARCHAR(700) DEFAULT '',
  `image_path` VARCHAR(500) DEFAULT '',
  `url` VARCHAR(700) NOT NULL,
  `source_domain` VARCHAR(180) DEFAULT '',
  `category` VARCHAR(120) NOT NULL,
  `score` INT DEFAULT 0,
  `published_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `fetched_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `status` VARCHAR(30) DEFAULT 'pending',
  `approved_at` DATETIME NULL,
  `approved_by_id` INT NULL,
  `source_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_trend_url` (`url`(255)),
  KEY `ix_trend_category` (`category`),
  KEY `ix_trend_score` (`score`),
  KEY `ix_trend_published_at` (`published_at`),
  KEY `ix_trend_fetched_at` (`fetched_at`),
  KEY `ix_trend_status` (`status`),
  KEY `ix_trend_approved_by_id` (`approved_by_id`),
  KEY `ix_trend_source_id` (`source_id`),
  CONSTRAINT `fk_trend_approved_by`
    FOREIGN KEY (`approved_by_id`) REFERENCES `user` (`id`)
    ON DELETE SET NULL,
  CONSTRAINT `fk_trend_source`
    FOREIGN KEY (`source_id`) REFERENCES `trend_source` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `question` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(220) NOT NULL,
  `body` TEXT NOT NULL,
  `tags` VARCHAR(255) DEFAULT '',
  `version` VARCHAR(80) DEFAULT '',
  `attachment_filename` VARCHAR(255) DEFAULT '',
  `attachment_path` VARCHAR(500) DEFAULT '',
  `status` VARCHAR(30) DEFAULT 'pending',
  `approved_at` DATETIME NULL,
  `approved_by_id` INT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `author_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_question_created_at` (`created_at`),
  KEY `ix_question_status` (`status`),
  KEY `ix_question_approved_by_id` (`approved_by_id`),
  KEY `ix_question_author_id` (`author_id`),
  CONSTRAINT `fk_question_approved_by`
    FOREIGN KEY (`approved_by_id`) REFERENCES `user` (`id`)
    ON DELETE SET NULL,
  CONSTRAINT `fk_question_author`
    FOREIGN KEY (`author_id`) REFERENCES `user` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `answer` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `body` TEXT NOT NULL,
  `status` VARCHAR(30) DEFAULT 'pending',
  `approved_at` DATETIME NULL,
  `approved_by_id` INT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `author_id` INT NOT NULL,
  `question_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_answer_created_at` (`created_at`),
  KEY `ix_answer_status` (`status`),
  KEY `ix_answer_approved_by_id` (`approved_by_id`),
  KEY `ix_answer_author_id` (`author_id`),
  KEY `ix_answer_question_id` (`question_id`),
  CONSTRAINT `fk_answer_approved_by`
    FOREIGN KEY (`approved_by_id`) REFERENCES `user` (`id`)
    ON DELETE SET NULL,
  CONSTRAINT `fk_answer_author`
    FOREIGN KEY (`author_id`) REFERENCES `user` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_answer_question`
    FOREIGN KEY (`question_id`) REFERENCES `question` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `question_attachment` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `question_id` INT NOT NULL,
  `filename` VARCHAR(255) NOT NULL,
  `file_path` VARCHAR(500) NOT NULL,
  `uploaded_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_question_attachment_question_id` (`question_id`),
  CONSTRAINT `fk_question_attachment_question`
    FOREIGN KEY (`question_id`) REFERENCES `question` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `expert_profile` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `display_name` VARCHAR(120) NOT NULL,
  `title` VARCHAR(160) DEFAULT 'IAM Community Expert',
  `company` VARCHAR(160) DEFAULT '',
  `bio` TEXT,
  `answer_total` INT DEFAULT 0,
  `question_total` INT DEFAULT 0,
  `is_listed` BOOLEAN DEFAULT FALSE,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_expert_profile_user_id` (`user_id`),
  KEY `ix_expert_profile_answer_total` (`answer_total`),
  KEY `ix_expert_profile_is_listed` (`is_listed`),
  CONSTRAINT `fk_expert_profile_user`
    FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `upcoming_event` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(220) NOT NULL,
  `description` TEXT,
  `event_type` VARCHAR(80) DEFAULT 'Webinar',
  `organizer` VARCHAR(160) DEFAULT '',
  `location` VARCHAR(180) DEFAULT 'Online',
  `starts_at` DATETIME NOT NULL,
  `ends_at` DATETIME NULL,
  `registration_url` VARCHAR(700) DEFAULT '',
  `source_url` VARCHAR(700) DEFAULT '',
  `is_published` BOOLEAN DEFAULT TRUE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_upcoming_event_event_type` (`event_type`),
  KEY `ix_upcoming_event_starts_at` (`starts_at`),
  KEY `ix_upcoming_event_is_published` (`is_published`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `trend_source`
  (`id`, `name`, `feed_url`, `website_url`, `category`, `is_active`)
VALUES
  (1, 'Okta Blog', 'https://www.okta.com/blog/feed/', 'https://www.okta.com/blog/', 'Identity Platform', TRUE),
  (2, 'Curity Blog', 'https://curity.io/news-feed.xml', 'https://curity.io/blog/', 'API Security', TRUE),
  (3, 'IDSA Blog', 'https://www.idsalliance.org/blog/feed/', 'https://www.idsalliance.org/blog/', 'Identity Security', TRUE),
  (4, 'SecurityWeek Identity & Access', 'https://www.securityweek.com/category/identity-access/feed/', 'https://www.securityweek.com/category/identity-access/', 'Cybersecurity', TRUE),
  (5, 'SailPoint Blog', 'https://www.sailpoint.com/blog/feed/', 'https://www.sailpoint.com/blog/', 'Identity Governance', TRUE),
  (6, 'Identity Management Institute', 'https://identitymanagementinstitute.org/feed/', 'https://identitymanagementinstitute.org/', 'IAM Careers', TRUE);

-- Demo password for all seeded accounts, including admin@atikes.com: Atikes@123
-- Change these passwords before any real deployment.
INSERT INTO `user`
  (`id`, `name`, `email`, `password_hash`, `title`, `company`, `bio`, `role`, `created_at`)
VALUES
  (1, 'ATIKES Admin', 'admin@atikes.com', 'scrypt:32768:8:1$o1lW4yMdpXeNUitY$169b6909b5fedc6266d750bc70a546ee90bc871e4da2b05e9c8b71518e8b9d6c87163b7ce58e594fb9f3a2219165d9e9f197950a5b6a879d8f8ab90ab1cb757b', 'Platform Administrator', 'ATIKES', 'Reviews and publishes IAM trends, questions, and answers.', 'admin', NOW()),
  (2, 'Anika Rao', 'anika.rao@example.com', 'scrypt:32768:8:1$o1lW4yMdpXeNUitY$169b6909b5fedc6266d750bc70a546ee90bc871e4da2b05e9c8b71518e8b9d6c87163b7ce58e594fb9f3a2219165d9e9f197950a5b6a879d8f8ab90ab1cb757b', 'SailPoint IAM Architect', 'ATIKES Community', 'Designs identity governance programs, access certifications, and lifecycle automation.', 'user', NOW()),
  (3, 'Michael Brown', 'michael.brown@example.com', 'scrypt:32768:8:1$L1u6sZaKVYnuTmOV$f861aa7c58f869c8c21ed2b077a4f8f754422c8ff18e792fb4881d3ebbc21f6ea1eda957c66fbaa343e6c0c91358f7e89b360ed339ad3f0cc9b9ca59cb2aafa8', 'Okta and Workforce Identity Consultant', 'ATIKES Community', 'Specializes in SSO, MFA, adaptive authentication, and application onboarding.', 'user', NOW()),
  (4, 'Sara Johnson', 'sara.johnson@example.com', 'scrypt:32768:8:1$TuZgv4Leh5Z9n8Ez$26d98b1087a47e8ce095ddca16f2ca04059256c330f004418c4bbe5b6545fdb55001ab7c238bd39917b1ecd033e7d39281d4bce4630ca4240153967251377c3a', 'Privileged Access Management Specialist', 'ATIKES Community', 'Helps teams reduce standing privilege and improve audit readiness.', 'user', NOW()),
  (5, 'Rahul Mehta', 'rahul.mehta@example.com', 'scrypt:32768:8:1$2U0A4dtGiKEycLoC$1ce887eca30c1a0a18919547fe73639641c74c4f759ffe70f7ec0514f556e8f47b51539d65f00c3728eaf28052980341e44c0c921b98c0ba4e42a26267a136ef', 'IAM Engineer', 'ATIKES Community', 'Works on provisioning, RBAC, and joiner-mover-leaver workflows.', 'user', NOW());

INSERT INTO `question`
  (`id`, `title`, `body`, `tags`, `version`, `attachment_filename`, `attachment_path`, `status`, `approved_at`, `approved_by_id`, `created_at`, `author_id`)
VALUES
  (1, 'How should we design mover access reviews in SailPoint?', 'Our organization has frequent department changes and manager changes. What is a good approach to automate mover access reviews while avoiding unnecessary access removal?', 'SailPoint IIQ', 'IIQ 8.4', '', '', 'approved', NOW(), 1, DATE_SUB(NOW(), INTERVAL 5 DAY), 5),
  (2, 'What is the best way to roll out MFA for legacy applications?', 'We have a mix of modern SaaS applications and older internal applications. How should we plan MFA rollout without breaking business workflows?', 'Okta', 'Okta OIE', '', '', 'approved', NOW(), 1, DATE_SUB(NOW(), INTERVAL 4 DAY), 2),
  (3, 'How do we start RBAC when access is already messy?', 'The current access model is mostly request-based and there are many one-off entitlements. What practical steps help build RBAC without a huge first-phase project?', 'Saviynt', '2026', '', '', 'approved', NOW(), 1, DATE_SUB(NOW(), INTERVAL 3 DAY), 3),
  (4, 'How often should privileged access be certified?', 'For admin access across servers, cloud consoles, and databases, what review frequency is reasonable and audit friendly?', 'Ping Identity', 'PingOne', '', '', 'approved', NOW(), 1, DATE_SUB(NOW(), INTERVAL 2 DAY), 5);

INSERT INTO `answer`
  (`id`, `body`, `status`, `approved_at`, `approved_by_id`, `created_at`, `author_id`, `question_id`)
VALUES
  (1, 'Start by separating business mover events from technical entitlement cleanup. In SailPoint, map authoritative HR attributes, trigger mover policies from department or manager changes, and route only high-risk or out-of-policy access for review. Keep low-risk birthright access automated so reviewers are not overloaded.', 'approved', NOW(), 1, DATE_SUB(NOW(), INTERVAL 4 DAY), 2, 1),
  (2, 'For legacy applications, avoid a single big-bang MFA rollout. Put applications behind an access gateway or identity-aware proxy where possible, pilot with low-risk user groups, then move high-risk apps first. Track exceptions with expiry dates so temporary bypasses do not become permanent.', 'approved', NOW(), 1, DATE_SUB(NOW(), INTERVAL 3 DAY), 3, 2),
  (3, 'Begin RBAC with discovery, not role creation. Pull entitlement usage, identify common access bundles by job function, and create a small set of business roles for the highest-volume teams. Keep exception access visible and review it separately until the model matures.', 'approved', NOW(), 1, DATE_SUB(NOW(), INTERVAL 2 DAY), 2, 3),
  (4, 'For privileged access, quarterly certification is common for high-risk production access, with monthly review for break-glass and domain admin groups. The stronger control is not only frequency, but whether access is time-bound, approved, monitored, and removed automatically when no longer needed.', 'approved', NOW(), 1, DATE_SUB(NOW(), INTERVAL 1 DAY), 4, 4),
  (5, 'A useful pattern is to combine RBAC with policy-based access. Roles handle predictable job access, while policies check risk signals such as location, device posture, manager, and employment status. This keeps the role model smaller and easier to govern.', 'approved', NOW(), 1, DATE_SUB(NOW(), INTERVAL 1 DAY), 3, 3);

INSERT INTO `expert_profile`
  (`id`, `user_id`, `display_name`, `title`, `company`, `bio`, `answer_total`, `question_total`, `is_listed`, `updated_at`)
VALUES
  (1, 2, 'Anika Rao', 'SailPoint IAM Architect', 'ATIKES Community', 'Designs identity governance programs, access certifications, and lifecycle automation.', 2, 1, TRUE, NOW()),
  (2, 3, 'Michael Brown', 'Okta and Workforce Identity Consultant', 'ATIKES Community', 'Specializes in SSO, MFA, adaptive authentication, and application onboarding.', 2, 1, TRUE, NOW()),
  (3, 4, 'Sara Johnson', 'Privileged Access Management Specialist', 'ATIKES Community', 'Helps teams reduce standing privilege and improve audit readiness.', 1, 0, TRUE, NOW()),
  (4, 5, 'Rahul Mehta', 'IAM Engineer', 'ATIKES Community', 'Works on provisioning, RBAC, and joiner-mover-leaver workflows.', 0, 2, FALSE, NOW());

INSERT INTO `upcoming_event`
  (`id`, `title`, `description`, `event_type`, `organizer`, `location`, `starts_at`, `ends_at`, `registration_url`, `source_url`, `is_published`)
VALUES
  (1, 'IAM Governance Readiness Workshop', 'A practical session on access reviews, role cleanup, and identity lifecycle controls.', 'Workshop', 'ATIKES', 'Online', '2026-06-10 10:00:00', '2026-06-10 11:30:00', 'https://atikes.com/', 'https://atikes.com/', TRUE),
  (2, 'Modern MFA and Passwordless Planning', 'Discussion on MFA rollout patterns, phishing resistance, and legacy application coverage.', 'Webinar', 'ATIKES', 'Online', '2026-06-24 14:00:00', '2026-06-24 15:00:00', 'https://atikes.com/', 'https://atikes.com/', TRUE),
  (3, 'Privileged Access Review Roundtable', 'Community roundtable for PAM certification frequency, break-glass governance, and audit evidence.', 'Roundtable', 'ATIKES', 'Online', '2026-07-08 11:00:00', '2026-07-08 12:00:00', 'https://atikes.com/', 'https://atikes.com/', TRUE);
