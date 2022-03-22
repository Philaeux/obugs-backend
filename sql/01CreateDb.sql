DROP TABLE contributions;
DROP TABLE bugs;
DROP TABLE roles;
DROP TABLE labels;
DROP TABLE users;
DROP TABLE software;

CREATE TABLE software (
  code varchar(16) NOT NULL PRIMARY KEY,
  name varchar(255) NOT NULL
);

CREATE TABLE users (
  name varchar(32) NOT NULL PRIMARY KEY,
  is_admin boolean NOT NULL
);

CREATE TABLE roles (
  software_code varchar(16) NOT NULL references software(code),
  users_name varchar(32) NOT NULL references users(name),
  is_developer boolean NOT NULL,
  is_moderator boolean NOT NULL,
  PRIMARY KEY (software_code, users_name)
);

CREATE TABLE labels (
  tag_code varchar(16) NOT NULL,
  software_code varchar(16) NOT NULL references software(code),
  description varchar(255),
  PRIMARY KEY (tag_code, software_code)
);

CREATE TABLE bugs (
  id int NOT NULL,
  software_code varchar(16) NOT NULL references software(code),
  title varchar(255) NOT NULL,
  status varchar(16) NOT NULL,
  PRIMARY KEY (id, software_code)
);

CREATE TABLE contributions (
  id int NOT NULL,
  software_code varchar(16) NOT NULL,
  bugs_id int NOT NULL,
  value varchar(255) NOT NULL,
  PRIMARY KEY (id, bugs_id),
  FOREIGN KEY (software_code, bugs_id) references bugs(software_code, id)
);

INSERT INTO software(code, name) VALUES('dota-2', 'Dota 2');
