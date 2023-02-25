CREATE TABLE emp (
	user_id serial PRIMARY KEY,
	fname VARCHAR ( 50 ) NOT NULL,
	lname VARCHAR ( 50 ) NOT NULL
);

insert into emp (fname, lname) values ('Gilbert', 'Lau');
insert into emp (fname, lname) values ('Robert', 'Lau');
insert into emp (fname, lname) values ('Kai Chung', 'Lau');
insert into emp (fname, lname) values ('Albert', 'Lau');
insert into emp (fname, lname) values ('Abraham', 'Lau');
insert into emp (fname, lname) values ('May', 'Wong');
insert into emp (fname, lname) values ('Henry', 'Ip');

