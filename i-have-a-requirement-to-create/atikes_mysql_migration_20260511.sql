USE atikes_iam;

ALTER TABLE `trend`
  ADD COLUMN `image_url` VARCHAR(700) DEFAULT '' AFTER `generated_content`,
  ADD COLUMN `image_path` VARCHAR(500) DEFAULT '' AFTER `image_url`;

CREATE TABLE IF NOT EXISTS `question_attachment` (
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

