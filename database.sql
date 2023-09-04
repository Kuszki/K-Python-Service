SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

CREATE DATABASE IF NOT EXISTS docs DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE docs;
CREATE TABLE `doclist` (
`id` int(10) unsigned
,`path` text
);
CREATE TABLE `docprivs` (
`doc` int(10) unsigned
,`usr` int(10) unsigned
,`can_view` tinyint(1)
,`can_mod` tinyint(1)
,`can_move` tinyint(1)
,`can_status` tinyint(1)
);

CREATE TABLE documents (
  id int(10) UNSIGNED NOT NULL,
  name varchar(256) NOT NULL,
  date_add datetime NOT NULL DEFAULT current_timestamp(),
  date_cre datetime NOT NULL,
  date_mod datetime NOT NULL DEFAULT current_timestamp(),
  user_add int(10) UNSIGNED NOT NULL,
  user_mod int(10) UNSIGNED NOT NULL,
  type_id int(11) UNSIGNED NOT NULL,
  path_id int(11) UNSIGNED NOT NULL,
  status_id int(11) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE groups (
  id int(10) UNSIGNED NOT NULL,
  name varchar(64) NOT NULL,
  comment text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE paths (
  id int(10) UNSIGNED NOT NULL,
  name varchar(256) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE privs (
  id int(10) UNSIGNED NOT NULL,
  path int(10) UNSIGNED NOT NULL,
  grp int(10) UNSIGNED NOT NULL,
  can_view tinyint(1) NOT NULL DEFAULT 0,
  can_add tinyint(1) NOT NULL DEFAULT 0,
  can_mod tinyint(1) NOT NULL DEFAULT 0,
  can_move tinyint(1) NOT NULL DEFAULT 0,
  can_status tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE statuses (
  id int(10) UNSIGNED NOT NULL,
  name varchar(64) NOT NULL,
  comment text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE types_main (
  id int(10) UNSIGNED NOT NULL,
  name varchar(2) NOT NULL,
  comment text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE types_sub (
  id int(10) UNSIGNED NOT NULL,
  name varchar(2) NOT NULL,
  type int(11) UNSIGNED NOT NULL,
  comment text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE users (
  id int(10) UNSIGNED NOT NULL,
  name varchar(64) NOT NULL,
  pass varchar(64) NOT NULL,
  admin tinyint(1) NOT NULL DEFAULT 0,
  timeout int(10) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE user_groups (
  id int(10) UNSIGNED NOT NULL,
  usr int(10) UNSIGNED NOT NULL,
  grp int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
DROP TABLE IF EXISTS `doclist`;

CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW doclist  AS SELECT d.`id` AS `id`, concat(p.`name`,'/',d.`name`) AS `path` FROM (documents d join paths p on(d.path_id = p.`id`)) ;
DROP TABLE IF EXISTS `docprivs`;

CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW docprivs  AS SELECT d.`id` AS `doc`, u.`id` AS `usr`, r.can_view AS `can_view`, r.can_mod AS `can_mod`, r.can_move AS `can_move`, r.can_status AS `can_status` FROM ((((documents d join paths p on(d.path_id = p.`id`)) join privs r on(d.`id` = r.`path`)) join user_groups g on(r.grp = g.grp)) join users u on(g.usr = u.`id`)) ;


ALTER TABLE documents
  ADD PRIMARY KEY (id),
  ADD UNIQUE KEY NAME (name),
  ADD KEY TYPE (type_id),
  ADD KEY PATH (path_id),
  ADD KEY STATUS (status_id),
  ADD KEY USERADD (user_add),
  ADD KEY USERMOD (user_mod);

ALTER TABLE groups
  ADD PRIMARY KEY (id),
  ADD UNIQUE KEY NAME (name);

ALTER TABLE paths
  ADD PRIMARY KEY (id),
  ADD UNIQUE KEY NAME (name);

ALTER TABLE privs
  ADD PRIMARY KEY (id),
  ADD UNIQUE KEY COMBO (path,grp),
  ADD KEY PATH (path),
  ADD KEY GRP (grp);

ALTER TABLE statuses
  ADD PRIMARY KEY (id),
  ADD UNIQUE KEY NAME (name);

ALTER TABLE types_main
  ADD PRIMARY KEY (id),
  ADD UNIQUE KEY NAME (name);

ALTER TABLE types_sub
  ADD PRIMARY KEY (id),
  ADD UNIQUE KEY NAME (name),
  ADD KEY TYPE (type);

ALTER TABLE users
  ADD PRIMARY KEY (id),
  ADD UNIQUE KEY NAME (name);

ALTER TABLE user_groups
  ADD PRIMARY KEY (id),
  ADD UNIQUE KEY COMBO (usr,grp),
  ADD KEY USR (usr),
  ADD KEY GRP (grp);


ALTER TABLE documents
  MODIFY id int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

ALTER TABLE groups
  MODIFY id int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

ALTER TABLE paths
  MODIFY id int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

ALTER TABLE privs
  MODIFY id int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

ALTER TABLE statuses
  MODIFY id int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

ALTER TABLE types_main
  MODIFY id int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

ALTER TABLE types_sub
  MODIFY id int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

ALTER TABLE users
  MODIFY id int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

ALTER TABLE user_groups
  MODIFY id int(10) UNSIGNED NOT NULL AUTO_INCREMENT;


ALTER TABLE documents
  ADD CONSTRAINT DOC_PATH_REL FOREIGN KEY (path_id) REFERENCES `paths` (id) ON UPDATE CASCADE,
  ADD CONSTRAINT DOC_STATUS_REL FOREIGN KEY (status_id) REFERENCES statuses (id) ON UPDATE CASCADE,
  ADD CONSTRAINT DOC_TYPE_REL FOREIGN KEY (type_id) REFERENCES types_sub (id) ON UPDATE CASCADE,
  ADD CONSTRAINT DOC_USERADD_REL FOREIGN KEY (user_add) REFERENCES `users` (id) ON UPDATE CASCADE,
  ADD CONSTRAINT DOC_USERMOD_REL FOREIGN KEY (user_mod) REFERENCES `users` (id) ON UPDATE CASCADE;

ALTER TABLE privs
  ADD CONSTRAINT PRIV_GRP_REL FOREIGN KEY (grp) REFERENCES `groups` (id) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT PRIV_PATH_REL FOREIGN KEY (path) REFERENCES `paths` (id) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE types_sub
  ADD CONSTRAINT TYP_SUB_REL FOREIGN KEY (type) REFERENCES types_main (id) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE user_groups
  ADD CONSTRAINT UG_GRP_REL FOREIGN KEY (grp) REFERENCES `groups` (id) ON UPDATE CASCADE,
  ADD CONSTRAINT UG_USR_REL FOREIGN KEY (usr) REFERENCES `users` (id) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
