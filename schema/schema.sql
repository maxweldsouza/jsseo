SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

DROP SCHEMA IF EXISTS `jsseo` ;
CREATE SCHEMA IF NOT EXISTS `jsseo` DEFAULT CHARACTER SET utf8 ;
USE `jsseo` ;

-- -----------------------------------------------------
-- Table `jsseo`.`site`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `jsseo`.`site` ;

CREATE TABLE IF NOT EXISTS `jsseo`.`site` (
    `site_hostname` VARCHAR(253) NOT NULL,
    PRIMARY KEY (`site_hostname`),
    UNIQUE INDEX `site_hostname_UNIQUE` (`site_hostname` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `jsseo`.`page`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `jsseo`.`page` ;

CREATE TABLE IF NOT EXISTS `jsseo`.`page` (
    `page_id` INT NOT NULL AUTO_INCREMENT,
    `site_hostname` VARCHAR(253) NOT NULL,
    `page_path` VARCHAR(253) NOT NULL,
    `page_updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `page_expires` TIMESTAMP NULL,
    `page_content` TEXT NULL,
    `page_expiresevery` INT NOT NULL DEFAULT 86400,
    `page_sha1` TINYTEXT NULL,
    PRIMARY KEY (`page_id`),
    INDEX `fk_page_site_idx` (`site_hostname` ASC),
    CONSTRAINT `fk_page_site`
    FOREIGN KEY (`site_hostname`)
    REFERENCES `jsseo`.`site` (`site_hostname`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
