-- =============================================
-- CRICKET DATABASE MANAGEMENT SYSTEM - CLEAN VERSION
-- Fixed all errors: losing_team_id spelling
-- =============================================

DROP DATABASE IF EXISTS CricketDB;
CREATE DATABASE CricketDB;
USE CricketDB;

-- =============================================
-- USER MANAGEMENT TABLE
-- =============================================

CREATE TABLE users (
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'user',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert demo users (SHA256 hashed passwords)
-- admin/admin123
-- user/user123
INSERT INTO users (username, password, role) VALUES
  ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin'),
  ('user', '04f8996da763b7a969b1028ee3007569eaf3a635486ddab211d512c85b9df8fb', 'user');

-- =============================================
-- ROLE TABLE
-- =============================================

CREATE TABLE role (
  role_id INT PRIMARY KEY,
  role_name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO role (role_id, role_name) VALUES
  (1, 'Batter'),
  (2, 'Bowler'),
  (3, 'All-Rounder'),
  (4, 'Wicketkeeper');

-- =============================================
-- TEAM TABLE
-- =============================================

CREATE TABLE team (
  team_id INT PRIMARY KEY,
  team_name VARCHAR(50) NOT NULL UNIQUE,
  country VARCHAR(50) NOT NULL
);

INSERT INTO team (team_id, team_name, country) VALUES
  (1, 'India', 'India'),
  (2, 'Australia', 'Australia'),
  (3, 'Sri Lanka', 'Sri Lanka'),
  (4, 'West Indies', 'West Indies');

-- =============================================
-- PLAYER TABLE
-- =============================================

CREATE TABLE player (
  player_id INT PRIMARY KEY,
  f_name VARCHAR(50) NOT NULL,
  l_name VARCHAR(50) NOT NULL,
  dob DATE NOT NULL,
  age INT,
  team_id INT NOT NULL,
  role_id INT NOT NULL,
  FOREIGN KEY (team_id) REFERENCES team(team_id),
  FOREIGN KEY (role_id) REFERENCES role(role_id),
  INDEX idx_team (team_id),
  INDEX idx_role (role_id)
);

INSERT INTO player (player_id, f_name, l_name, dob, age, team_id, role_id) VALUES
  (1, 'Rohit', 'Sharma', '1987-04-30', 37, 1, 1),
  (2, 'Virat', 'Kohli', '1988-11-05', 36, 1, 1),
  (3, 'Shubman', 'Gill', '1999-09-08', 25, 1, 1),
  (4, 'Hardik', 'Pandya', '1993-10-11', 31, 1, 3),
  (5, 'Jasprit', 'Bumrah', '1993-12-06', 31, 1, 2),
  (6, 'Ravindra', 'Jadeja', '1988-12-06', 36, 1, 3),
  (7, 'Rishabh', 'Pant', '1997-10-04', 27, 1, 4),
  (8, 'KL', 'Rahul', '1992-04-18', 32, 1, 4);

-- =============================================
-- TOURNAMENT TABLE
-- =============================================

CREATE TABLE tournament (
  tournament_id INT PRIMARY KEY,
  tournament_name VARCHAR(100) NOT NULL UNIQUE,
  year INT NOT NULL
);

INSERT INTO tournament (tournament_id, tournament_name, year) VALUES
  (1, 'ICC World Cup', 2023),
  (2, 'Asia Cup', 2025),
  (3, 'Indian Premier League', 2025);

-- =============================================
-- TRAINER TABLE
-- =============================================

CREATE TABLE trainer (
  trainer_id INT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  specialization VARCHAR(50) NOT NULL,
  experience INT NOT NULL,
  team_id INT NOT NULL,
  FOREIGN KEY (team_id) REFERENCES team(team_id),
  INDEX idx_team (team_id)
);

INSERT INTO trainer (trainer_id, name, specialization, experience, team_id) VALUES
  (1, 'Ravi Shastri', 'Head Coach', 10, 1),
  (2, 'Bharat Arun', 'Bowling Coach', 7, 1),
  (3, 'R Sridhar', 'Fielding Coach', 5, 1),
  (4, 'Vikram Rathour', 'Batting Coach', 6, 1);

-- =============================================
-- MATCHES TABLE - FIXED: losing_team_id (was loosing_team_id)
-- =============================================

CREATE TABLE matches (
  match_id INT PRIMARY KEY,
  winning_team_id INT NOT NULL,
  losing_team_id INT NOT NULL,
  date_of_match DATE NOT NULL,
  location VARCHAR(50) NOT NULL,
  tournament_id INT NOT NULL,
  FOREIGN KEY (winning_team_id) REFERENCES team(team_id),
  FOREIGN KEY (losing_team_id) REFERENCES team(team_id),
  FOREIGN KEY (tournament_id) REFERENCES tournament(tournament_id),
  INDEX idx_winner (winning_team_id),
  INDEX idx_loser (losing_team_id),
  INDEX idx_tournament (tournament_id)
);

INSERT INTO matches (match_id, winning_team_id, losing_team_id, date_of_match, location, tournament_id) VALUES
  (1, 1, 2, '2025-05-20', 'Mumbai', 1),
  (2, 3, 1, '2025-06-15', 'Delhi', 2),
  (3, 1, 4, '2025-04-10', 'Chennai', 3);

-- =============================================
-- PLAYER_PERFORMANCE TABLE
-- =============================================

CREATE TABLE player_performance (
  performance_id INT PRIMARY KEY,
  player_id INT NOT NULL,
  match_id INT NOT NULL,
  runs_scored INT DEFAULT 0,
  wickets_taken INT DEFAULT 0,
  format VARCHAR(20) NOT NULL,
  avg DECIMAL(5,2) DEFAULT 0,
  FOREIGN KEY (player_id) REFERENCES player(player_id) ON DELETE CASCADE,
  FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
  INDEX idx_player (player_id),
  INDEX idx_match (match_id)
);

INSERT INTO player_performance (performance_id, player_id, match_id, runs_scored, wickets_taken, format, avg) VALUES
  (1, 1, 1, 85, 0, 'One Day', 42.5),
  (2, 2, 1, 58, 0, 'One Day', 29.0),
  (3, 5, 2, 0, 4, 'Test', 30.0),
  (4, 6, 3, 62, 2, 'T20', 31.0);

-- =============================================
-- AWARD TABLE
-- =============================================

CREATE TABLE award (
  award_id INT PRIMARY KEY,
  award_name VARCHAR(50) NOT NULL,
  player_id INT NOT NULL,
  match_id INT NOT NULL,
  day INT NOT NULL,
  month INT NOT NULL,
  year INT NOT NULL,
  description VARCHAR(255),
  FOREIGN KEY (player_id) REFERENCES player(player_id) ON DELETE CASCADE,
  FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
  INDEX idx_player (player_id),
  INDEX idx_match (match_id)
);

INSERT INTO award (award_id, award_name, player_id, match_id, day, month, year, description) VALUES
  (1, 'Man of the Match', 1, 1, 20, 5, 2025, 'Outstanding batting performance'),
  (2, 'Best Bowler', 5, 2, 15, 6, 2025, '4 wickets in the match');

-- =============================================
-- PLAYED_IN TABLE
-- =============================================

CREATE TABLE played_in (
  match_id INT NOT NULL,
  team_id INT NOT NULL,
  PRIMARY KEY (match_id, team_id),
  FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
  FOREIGN KEY (team_id) REFERENCES team(team_id) ON DELETE CASCADE
);

INSERT INTO played_in (match_id, team_id) VALUES
  (1, 1), (1, 2),
  (2, 3), (2, 1),
  (3, 1), (3, 4);

-- =============================================
-- TRIGGERS
-- =============================================

DELIMITER //

CREATE TRIGGER trg_set_age
BEFORE INSERT ON player
FOR EACH ROW
BEGIN
    SET NEW.age = TIMESTAMPDIFF(YEAR, NEW.dob, CURDATE());
END;

//
DELIMITER ;

DELIMITER //

CREATE TRIGGER trg_promote_to_allrounder
AFTER INSERT ON player_performance
FOR EACH ROW
BEGIN
  IF NEW.runs_scored >= 50 AND NEW.wickets_taken >= 3 THEN
    UPDATE player
    SET role_id = 3
    WHERE player_id = NEW.player_id;
  END IF;
END;

//
DELIMITER ;

-- =============================================
-- STORED PROCEDURES
-- =============================================

DELIMITER //

CREATE PROCEDURE GetPlayersByTeam(IN teamName VARCHAR(50))
BEGIN
  SELECT p.player_id, p.f_name, p.l_name, r.role_name
  FROM player p
  JOIN team t ON p.team_id = t.team_id
  JOIN role r ON p.role_id = r.role_id
  WHERE t.team_name = teamName
  ORDER BY p.f_name;
END;

//
DELIMITER ;

-- =============================================
-- FUNCTIONS
-- =============================================

DELIMITER //

CREATE FUNCTION GetPlayerBattingAvg(playerId INT)
RETURNS DECIMAL(5,2)
DETERMINISTIC
READS SQL DATA
BEGIN
  DECLARE avg_runs DECIMAL(5,2);
  SELECT AVG(runs_scored) INTO avg_runs 
  FROM player_performance 
  WHERE player_id = playerId;
  RETURN IFNULL(avg_runs, 0);
END;

//
DELIMITER ;


INSERT INTO player (player_id, f_name, l_name, dob, age, team_id, role_id) VALUES
  (9, 'Ajinkya', 'Rahane', '1988-06-06', 37, 1, 1),
  (10, 'Shikhar', 'Dhawan', '1985-12-05', 39, 1, 1),
  (11, 'Bhuvneshwar', 'Kumar', '1990-02-05', 33, 1, 2),
  (12, 'Yuzvendra', 'Chahal', '1990-07-23', 33, 1, 2),
  (13, 'Ravichandran', 'Ashwin', '1986-09-17', 37, 1, 3),
  (14, 'Dinesh', 'Karthik', '1985-06-01', 39, 1, 4),
  (15, 'Mohammed', 'Shami', '1990-09-03', 33, 1, 2),
  (16, 'Kedar', 'Jadhav', '1985-03-26', 39, 1, 3),
  (17, 'Shreyas', 'Iyer', '1994-12-06', 29, 1, 1),
  (18, 'Washington', 'Sundar', '1999-10-05', 24, 1, 3),
  (19, 'T Natarajan', 'Natarajan', '1991-04-24', 32, 1, 2),
  (20, 'Ishan', 'Kishan', '1998-07-18', 26, 1, 1),
  (21, 'Deepak', 'Chahar', '1992-08-07', 32, 1, 2),
  (22, 'Ravindra', 'Jadeja', '1988-12-06', 36, 1, 3),
  (23, 'Rishabh', 'Pant', '1997-10-04', 27, 1, 4);


INSERT INTO player (player_id, f_name, l_name, dob, age, team_id, role_id) VALUES
  (24, 'Steve', 'Smith', '1989-06-02', 34, 2, 1),
  (25, 'Michael', 'Clarke', '1981-04-02', 42, 2, 3),
  (26, 'Glenn', 'McGrath', '1970-02-09', 52, 2, 2),
  (27, 'Pat', 'Cummins', '1993-05-08', 31, 2, 2),
  (28, 'David', 'Warner', '1986-10-27', 36, 2, 1),
  (29, 'Aaron', 'Finch', '1986-11-17', 36, 2, 1),
  (30, 'Mitchell', 'Starc', '1990-01-30', 34, 2, 2),
  (31, 'Matthew', 'Wade', '1987-11-25', 35, 2, 4),
  (32, 'Alex', 'Carey', '1991-09-27', 32, 2, 4),
  (33, 'Josh', 'Hazlewood', '1991-01-08', 33, 2, 2),
  (34, 'Nathan', 'Lyon', '1987-04-20', 35, 2, 2),
  (35, 'Mitchell', 'Marsh', '1991-10-18', 32, 2, 3),
  (36, 'Brad', 'Haddin', '1977-10-23', 46, 2, 4),
  (37, 'Shane', 'Watson', '1981-06-17', 42, 2, 3),
  (38, 'Steven', 'Smith', '1989-06-02', 34, 2, 1);


INSERT INTO player (player_id, f_name, l_name, dob, age, team_id, role_id) VALUES
  (39, 'Kumar', 'Sangakkara', '1977-10-27', 45, 3, 1),
  (40, 'Muttiah', 'Muralitharan', '1972-04-17', 50, 3, 2),
  (41, 'Mahela', 'Jayawardene', '1977-05-27', 45, 3, 1),
  (42, 'Lasith', 'Malinga', '1983-08-28', 39, 3, 2),
  (43, 'Dinesh', 'Chandimal', '1989-09-18', 33, 3, 1),
  (44, 'Niroshan', 'Dickwella', '1993-06-23', 29, 3, 4),
  (45, 'Angelo', 'Mathews', '1987-06-02', 35, 3, 3),
  (46, 'Thisara', 'Perera', '1989-06-03', 33, 3, 3),
  (47, 'Dhananjaya', 'de Silva', '1991-09-06', 31, 3, 1),
  (48, 'Suranga', 'Lakmal', '1987-10-10', 35, 3, 2),
  (49, 'Kusal', 'Mendis', '1995-02-09', 28, 3, 1),
  (50, 'Charith', 'Asalanka', '1997-01-29', 26, 3, 1),
  (51, 'Wanindu', 'Hasaranga', '1997-07-29', 26, 3, 3),
  (52, 'Akila', 'Dananjaya', '1993-10-02', 29, 3, 2),
  (53, 'Lasith', 'Embuldeniya', '1991-06-08', 31, 3, 2);


INSERT INTO player (player_id, f_name, l_name, dob, age, team_id, role_id) VALUES
  (54, 'Chris', 'Gayle', '1979-09-21', 43, 4, 1),
  (55, 'Brian', 'Lara', '1969-05-02', 53, 4, 1),
  (56, 'Courtney', 'Walsh', '1962-10-30', 60, 4, 2),
  (57, 'Sunil', 'Narine', '1988-05-26', 35, 4, 3),
  (58, 'Kieron', 'Pollard', '1987-05-12', 36, 4, 3),
  (59, 'Jason', 'Holder', '1991-11-05', 32, 4, 3),
  (60, 'Andre', 'Russell', '1988-04-29', 36, 4, 3),
  (61, 'Denesh', 'Rajan', '1990-11-16', 34, 4, 2),
  (62, 'Dwayne', 'Bravo', '1983-10-07', 39, 4, 3),
  (63, 'Shimron', 'Hetmyer', '1996-12-26', 27, 4, 1),
  (64, 'Nicholas', 'Pooran', '1995-10-02', 27, 4, 4),
  (65, 'Shannon', 'Gabriel', '1988-10-20', 36, 4, 2),
  (66, 'Roston', 'Chase', '1989-09-24', 34, 4, 3),
  (67, 'Jerome', 'Taylor', '1984-06-19', 38, 4, 2),
  (68, 'Carlos', 'Brathwaite', '1985-07-19', 38, 4, 3);
INSERT INTO player_performance (performance_id, player_id, match_id, runs_scored, wickets_taken, format, avg) VALUES
  (10, 9, 1, 45, 0, 'One Day', 22.5),
  (11, 10, 1, 78, 0, 'One Day', 39.0),
  (12, 11, 2, 5, 2, 'Test', 15.0),
  (13, 12, 3, 0, 3, 'T20', 18.0),
  (14, 13, 1, 30, 1, 'One Day', 25.0),
  (15, 14, 2, 56, 0, 'Test', 28.0),
  (16, 15, 3, 49, 1, 'T20', 21.0),
  (17, 16, 1, 75, 0, 'One Day', 34.0),
  (18, 17, 2, 35, 0, 'Test', 20.0),
  (19, 18, 3, 60, 3, 'T20', 25.0),
  (20, 19, 1, 22, 0, 'One Day', 20.0),
  (21, 20, 2, 48, 0, 'Test', 23.0),
  (22, 21, 3, 31, 0, 'T20', 15.0),
  (23, 22, 1, 55, 0, 'One Day', 21.7),
  (24, 23, 2, 63, 0, 'Test', 29.1);
INSERT INTO player_performance (performance_id, player_id, match_id, runs_scored, wickets_taken, format, avg) VALUES
  (25, 24, 1, 50, 0, 'One Day', 25.0),
  (26, 25, 1, 40, 1, 'One Day', 23.0),
  (27, 26, 2, 15, 4, 'Test', 18.5),
  (28, 27, 3, 18, 5, 'T20', 20.0),
  (29, 28, 1, 45, 0, 'One Day', 25.0),
  (30, 29, 2, 53, 0, 'Test', 26.0),
  (31, 30, 3, 30, 0, 'T20', 22.0),
  (32, 31, 1, 10, 0, 'One Day', 15.0),
  (33, 32, 2, 67, 0, 'Test', 33.0),
  (34, 33, 3, 42, 0, 'T20', 20.5),
  (35, 34, 1, 19, 2, 'One Day', 23.0),
  (36, 35, 2, 55, 3, 'Test', 30.0),
  (37, 36, 3, 70, 0, 'T20', 35.0),
  (38, 37, 1, 34, 0, 'One Day', 25.0),
  (39, 38, 2, 29, 0, 'Test', 18.0);

INSERT INTO player_performance (performance_id, player_id, match_id, runs_scored, wickets_taken, format, avg) VALUES
  (40, 39, 1, 52, 0, 'One Day', 27.0),
  (41, 40, 1, 45, 4, 'One Day', 25.5),
  (42, 41, 2, 60, 0, 'Test', 30.0),
  (43, 42, 3, 5, 5, 'T20', 20.0),
  (44, 43, 1, 39, 0, 'One Day', 22.0),
  (45, 44, 2, 35, 0, 'Test', 20.0),
  (46, 45, 3, 41, 1, 'T20', 25.0),
  (47, 46, 1, 50, 0, 'One Day', 30.0),
  (48, 47, 2, 28, 0, 'Test', 15.0),
  (49, 48, 3, 57, 2, 'T20', 27.0),
  (50, 49, 1, 61, 0, 'One Day', 29.0),
  (51, 50, 2, 42, 0, 'Test', 20.0),
  (52, 51, 3, 36, 0, 'T20', 24.0),
  (53, 52, 1, 40, 3, 'One Day', 18.0),
  (54, 53, 2, 33, 1, 'Test', 21.0);
INSERT INTO player_performance (performance_id, player_id, match_id, runs_scored, wickets_taken, format, avg) VALUES
  (55, 54, 1, 65, 0, 'One Day', 35.0),
  (56, 55, 1, 55, 0, 'One Day', 28.0),
  (57, 56, 2, 20, 5, 'Test', 20.0),
  (58, 57, 3, 18, 2, 'T20', 22.0),
  (59, 58, 1, 30, 0, 'One Day', 21.0),
  (60, 59, 2, 38, 1, 'Test', 24.0),
  (61, 60, 3, 45, 0, 'T20', 26.0),
  (62, 61, 1, 15, 3, 'One Day', 18.0),
  (63, 62, 2, 50, 0, 'Test', 27.0),
  (64, 63, 3, 55, 0, 'T20', 28.0),
  (65, 64, 1, 35, 3, 'One Day', 19.0),
  (66, 65, 2, 44, 1, 'Test', 22.0),
  (67, 66, 3, 60, 0, 'T20', 30.0),
  (68, 67, 1, 40, 0, 'One Day', 20.0),
  (69, 68, 2, 38, 0, 'Test', 22.0);

-- =============================================
-- VERIFICATION
-- =============================================

SHOW TABLES;
SELECT * FROM users;
SELECT * FROM team;
SELECT * FROM player;

UPDATE users SET password = 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446' WHERE username = 'user';
ALTER TABLE award MODIFY COLUMN award_id INT PRIMARY KEY AUTO_INCREMENT;
