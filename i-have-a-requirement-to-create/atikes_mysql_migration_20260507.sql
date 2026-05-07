-- ATIKES IAM migration for existing MySQL databases
-- Use this when the app code has been updated but you do not want to drop/recreate data.

USE atikes_iam;

ALTER TABLE `trend`
  ADD COLUMN `generated_content` TEXT NULL AFTER `summary`;

ALTER TABLE `question`
  ADD COLUMN `version` VARCHAR(80) DEFAULT '' AFTER `tags`,
  ADD COLUMN `attachment_filename` VARCHAR(255) DEFAULT '' AFTER `version`,
  ADD COLUMN `attachment_path` VARCHAR(500) DEFAULT '' AFTER `attachment_filename`;

