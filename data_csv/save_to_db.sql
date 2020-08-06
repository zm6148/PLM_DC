LOAD DATA LOCAL INFILE "~/Desktop/PLM_data_challenge/data_csv/user_symptom.csv"
INTO TABLE innodb.user_symptom
COLUMNS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
ESCAPED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

LOAD DATA LOCAL INFILE "~/Desktop/PLM_data_challenge/data_csv/user_condition.csv"
INTO TABLE innodb.user_condition
COLUMNS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
ESCAPED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;
