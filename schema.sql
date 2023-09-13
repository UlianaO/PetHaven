CREATE TABLE Users(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL, password TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'inactive', privilage TEXT NOT NULL DEFAULT 'low', CHECK (privilage in ('low', 'admin')));
---- one user(admin) is able to manage everything. ---- just one volunteer, the rest are users
---- NEED VOLUNTEER TABLE
---- boolean admin = when admin is 1 its a volunteer, when its 0 its an applicant.
--- whenever user is created, the default is 0.
--- inside of HTML: you user['admin'] == 0 :


CREATE TABLE Applicants(id INTEGER REFERENCES Users (id), name VARCHAR(40) NOT NULL, phone TEXT, address TEXT, employment TEXT,
reason TEXT NOT NULL, dob DATE, status TEXT NOT NULL DEFAULT 'pending', dateofapplication DATE NOT NULL DEFAULT CURRENT_DATE,
admin BOOLEAN NOT NULL DEFAULT '0', pet INTEGER REFERENCES Pets (pid),
PRIMARY KEY(id),
CHECK (status in ('approved', 'declined', 'pending')));

CREATE TABLE Pets (pid INTEGER PRIMARY KEY AUTOINCREMENT, kennel_id varchar(5) references Kennels (id), type varchar(1) not null, status VARCHAR(15) NOT NULL DEFAULT 'available', pname VARCHAR(40),
sex CHAR(1), dob DATE, image TEXT, dateofintake DATE NOT NULL DEFAULT CURRENT_DATE, description TEXT,
CHECK (status in ('available', 'pre-adopted', 'adopted')), CHECK (type in ('Dog', 'Cat', 'Other')));

CREATE TABLE Adopters (id INTEGER PRIMARY KEY REFERENCES Users (id), pid INTEGER REFERENCES Pets (pid), name VARCHAR(40) NOT NULL, phone TEXT, address TEXT, employment TEXT, 
dob DATE, dateOfAdoption DATE, admin BOOLEAN NOT NULL DEFAULT '0');

CREATE TABLE Volunteer( id INTEGER REFERENCES Users(id), name VARCHAR(50), dateofapplication DATE NOT NULL DEFAULT CURRENT_DATE);  
create table Kennels(id VARCHAR(4) primary key, status varchar(5) not null default 'empty');

------INSERTION INITAL DATABASE---------
insert into Kennels(id) values('K001');
insert into Kennels(id) values('K232');
insert into Kennels(id) values('K631');
insert into Kennels(id) values('K935');
insert into Kennels(id) values('K505');
insert into Kennels(id) values('K781');
insert into Kennels(id) values('K749');
insert into Kennels(id) values('K342');
insert into Kennels(id) values('K370');
insert into Kennels(id) values('K913');
insert into Kennels(id) values('K874');
insert into Kennels(id) values('K117');

insert into Kennels(id) values('K182');
insert into Kennels(id) values('K318');
insert into Kennels(id) values('K923');


INSERT INTO Pets(kennel_id, type, pname, sex, dob, image, dateofintake, description)
            values ('K232','Cat', 'Marsha', 'F', '2021-06-17', 'Marsha.png', '2022-07-07', 'She loves to play, very good around other kids and cats');


INSERT INTO Pets(kennel_id, type, pname, sex, dob, image, dateofintake, description)
            values ('K935','Cat', 'Shadow', 'M', '2015-12-19', 'Shadow.png', '2022-05-07', 'His name completely reflects his personality - he will shadow you around the house wherever you go.');


INSERT INTO Pets(kennel_id, type, pname, sex, dob, image, dateofintake, description)
            values ('K505', 'Dog', 'Little Doodly', 'F', '2022-01-01', 'LittleDoodly.png', '2022-07-12', 'She needs a big fenced backyard and a playmate so they can bring our the best in each other.');

INSERT INTO Pets(kennel_id, type, pname, sex, dob, image, dateofintake, description)
            values ('K923','Dog', 'Foody', 'F', '2021-12-30', 'Foody.png', '2022-07-15', 'Guess where I got my name from! I will love you forever, for food. The staff thinks it is because my previous owner didn`t feed me much - I got here very skinny and skittish.');

INSERT INTO Pets(kennel_id, type, pname, sex, dob, image, dateofintake, description)
            values ('K182', 'Cat', 'Jasper', 'M', '2022-04-03', 'Jasper.png', '2022-07-08', 'I`m very fluffy and chill');

INSERT INTO Pets(kennel_id, type, pname, sex, dob, image, dateofintake, description)
            values ('K117', 'Other', 'Fluffy Pooh', 'F', '2022-05-01', 'Fluffy Pooh.png', '2022-07-08', 'I know how to use litter box, and love cats. Dogs, however, scare me :( ');

INSERT INTO Pets(kennel_id, type, pname, sex, dob, image, dateofintake, description)
            values ('K370', 'Cat', 'Jewel', 'F', '2022-05-11', 'Jewel.png', '2022-07-01', "Apparently, I`m a mix of snowshoe and DSH. I live by 'if you want people to treat you like a princess, you have to bee one.' Looking for fur-ever servers. ");

INSERT INTO Pets(kennel_id, type, pname, sex, dob, image, dateofintake, description)
            values ('K631','Other', 'Mr. Laps', 'M', '2020-03-19', 'Mr. Laps.png', '2022-04-12', 'Although I`m a bully, I don`t bully. I`m scared of EVERY LITTLE THING. Especially flying ones!!! ');

INSERT INTO Pets(kennel_id, type, pname, sex, dob, image, dateofintake, description)
            values ('K781', 'Dog', 'Robbery Jack', 'F', '2022-01-01', 'Robbery Jack.png', '2022-05-01', 'My name is Robbery because I will rob you of love!!! Also, I`m Jack because the staff thought I was a boy. I`m very playful and need a playmate.');

INSERT INTO Pets(kennel_id, type, pname, sex, dob, image, dateofintake, description)
            values ('K342', 'Dog', 'Scarf', 'M', '2019-03-19', 'Scarf.png', '2022-02-26', 'I`m NOT OLD I`m experienced! I befriend everyone and like to lay on your neck. I`m small and low-energy, want a home without children. ');

INSERT INTO Pets(kennel_id, type, pname, sex, dob, image, dateofintake, description)
            values ('K874', 'Cat', 'Wobbl', 'M', '2022-04-23', 'Wobbl.png', '2022-07-12', 'I have a very rare condition and it doesn`t let me walk still. But I`m not bothered by it and am very playful! Ready for you to take me home!');