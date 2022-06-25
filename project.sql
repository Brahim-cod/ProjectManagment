use project;
CREATE TABLE `departement` (
  `dpt_id` int NOT NULL AUTO_INCREMENT,
  `dpt_name` varchar(50) NOT NULL,
  PRIMARY KEY (`dpt_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `emp` (
  `emp_id` int NOT NULL AUTO_INCREMENT,
  `fullName` varchar(50) NOT NULL,
  `dpt_id` int NOT NULL,
  `joinDate` date NOT NULL DEFAULT '2022-01-01',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `pass` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `phone` varchar(15) NOT NULL,
  `status` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`emp_id`),
  CONSTRAINT `dpt_fk` FOREIGN KEY (`dpt_id`) REFERENCES `departement` (`dpt_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `chef_projet` (
  `chef_id` int NOT NULL,
  PRIMARY KEY (`chef_id`),
  CONSTRAINT `emp_fk` FOREIGN KEY (`chef_id`) REFERENCES `emp` (`emp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `equipe` (
  `equipe_id` int NOT NULL AUTO_INCREMENT,
  `nomEQ` varchar(50) DEFAULT NULL,
  `chef_id` int NOT NULL,
  PRIMARY KEY (`equipe_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `emp_equipe` (
  `emp_id` int NOT NULL,
  `equipe_id` int NOT NULL,
  PRIMARY KEY (`equipe_id`,`emp_id`),
  KEY `emp_fk` (`emp_id`),
  CONSTRAINT `emps_fk` FOREIGN KEY (`emp_id`) REFERENCES `emp` (`emp_id`),
  CONSTRAINT `equie_fk` FOREIGN KEY (`equipe_id`) REFERENCES `equipe` (`equipe_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `categorie` (
  `cat_id` int NOT NULL AUTO_INCREMENT,
  `cat_name` varchar(50) NOT NULL,
  PRIMARY KEY (`cat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `projet` (
  `projet_id` int NOT NULL AUTO_INCREMENT,
  `nomP` varchar(50) DEFAULT NULL,
  `datedebut` date DEFAULT NULL,
  `datefin` date DEFAULT NULL,
  `descriptionP` text,
  `cat_id` int NOT NULL,
  `equipe_id` int NOT NULL,
  PRIMARY KEY (`projet_id`),
  KEY `equipe_id` (`equipe_id`),
  CONSTRAINT `cat_fk` FOREIGN KEY (`cat_id`) REFERENCES `categorie` (`cat_id`),
  CONSTRAINT `projet_ibfk_1` FOREIGN KEY (`equipe_id`) REFERENCES `equipe` (`equipe_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `tache` (
  `tache_id` int NOT NULL AUTO_INCREMENT,
  `nomT` varchar(50) DEFAULT NULL,
  `dateF` date DEFAULT NULL,
  `dateD` date NOT NULL,
  `etat` int DEFAULT NULL,
  `priority` varchar(10) NOT NULL,
  `status` varchar(10) DEFAULT 'Dealy',
  `projet_id` int NOT NULL,
  `emp_id` int NOT NULL,
  PRIMARY KEY (`tache_id`),
  KEY `projet_id` (`projet_id`),
  CONSTRAINT `empl_fk` FOREIGN KEY (`emp_id`) REFERENCES `emp` (`emp_id`),
  CONSTRAINT `tache_ibfk_1` FOREIGN KEY (`projet_id`) REFERENCES `projet` (`projet_id`)
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `event` (
  `event_id` int NOT NULL AUTO_INCREMENT,
  `nomE` varchar(50) DEFAULT NULL,
  `dateD` date NOT NULL,
  `dateF` date DEFAULT NULL,
  `emp_id` int NOT NULL,
  PRIMARY KEY (`event_id`),
  CONSTRAINT `empls_fk` FOREIGN KEY (`emp_id`) REFERENCES `emp` (`emp_id`)
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
