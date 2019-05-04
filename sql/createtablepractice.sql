use kgp;

create table company_tb (
    register_id integer primary key auto_increment not null,
    company_nm char(100) not null unique,
    service_nm varchar(100),
    address varchar(200) not null
);
alter table company_tb add unique(company_nm);

create table library_opiton_tb (
    id integer primary key auto_increment not null,
    company_fk integer not null 
    references company_tb(register_id) ON DELETE CASCADE,
    option_name char(100) not null,
    search_option varchar(100)
);

create table user_tb (
    userkey_id varchar(255) primary key not null,
    library integer not null default 0
    references company_tb(register_id),
    user_status integer not null default 0
);


create table qna_tb (
  id integer auto_increment not null primary key,
  userkey_fk char(50) references user_tb(userkey_id),
  library_fk integer not null,
  created datetime,
  content varchar(255),
  managerkey_fk integer default 0,
  answer varchar(255),
  answerdate datetime
) charset=utf8;

use kgp;
create table qna_tb (
  id integer auto_increment not null primary key,
  userkey_fk char(50) references user_tb(userkey_id),
  created datetime,
  content varchar(255),
  managerkey_fk integer default 0,
  answer varchar(255),
  answerdate datetime
) charset=utf8;


create table nfc_tb (
    id integer not null PRIMARY key,
    shelf_height INTEGER not null,
    shelf_height INTEGER not null,
    shelf_location char(100) not null,
    image_source char(255)
) charset=utf8;

create table book_tb (
    id integer auto_increment not null PRIMARY key,
    isbn char(50) not null,
    title varchar(255) not null,
    book_location char(50) not null default -1,
    update_date datetime not null,
    nfc_id_fk integer REFERENCES nfc_tb(id),
    image_source char(255),
    company_fk INTEGER REFERENCES company_tb(register_id)
) charset=utf8;

alter table company_tb add latitude double;
alter table company_tb add longitude double;

insert into company_tb(company_nm, address, service_nm) values ("충북대학교","충청북도 청주시 서원구 개신동 1 충북대학교", "chungbukNational");
insert into library_opiton_tb(company_fk, option_name, search_option) 
    values(1,"중앙도서관","&f=(BR%3A%26quot%3B01%26quot%3B)");
insert into library_opiton_tb(company_fk, option_name, search_option) 
    values(2,"과학기술도서관","&f=(BR%3A%26quot%3B02%26quot%3B)");
insert into library_opiton_tb(company_fk, option_name, search_option) 
    values(3,"의학도서관","&f=(BR%3A%26quot%3B03%26quot%3B)");
insert into library_opiton_tb(company_fk, option_name, search_option) 
    values(4,"법학도서관","&f=(BR%3A%26quot%3B04%26quot%3B)");



    CREATE TABLE `company_tb` (
  `register_id` int(11) NOT NULL AUTO_INCREMENT,
  `company_nm` char(100) NOT NULL,
  `service_nm` varchar(100) DEFAULT NULL,
  `address` varchar(200) NOT NULL,
  PRIMARY KEY (`register_id`),
  UNIQUE KEY `company_nm` (`company_nm`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `user_tb` (
  `userkey_id` char(50) NOT NULL,
  `library` int(11) NOT NULL DEFAULT 0
  references company_tb(register_id) ON DELETE CASCADE,
  `user_status` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`userkey_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `qna_tb` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userkey_fk` char(50) DEFAULT NULL references user_tb(userkey_id) ON DELETE CASCADE,
  `created` datetime DEFAULT NULL,
  `content` varchar(255) DEFAULT NULL,
  `managerkey_fk` int(11) DEFAULT 0,
  `answer` varchar(255) DEFAULT NULL,
  `answerdate` datetime DEFAULT NULL,
  `library_fk` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `library_opiton_tb` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `option_name` varchar(255) DEFAULT NULL,
  `search_option` varchar(100) DEFAULT NULL,
  `company_fk` int(11) NOT NULL
  references company_tb(register_id) ON DELETE CASCADE,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `isbn_tb` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `isbn` char(20) NOT NULL,
  `book_nm` varchar(200) DEFAULT NULL,
  `author` char(80) NOT NULL,
  `keyword` varchar(255) DEFAULT NULL,
  `publish_year` year(4) NOT NULL DEFAULT 0000,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


insert into company_tb(company_nm, address, service_nm) values ("충북대학교","충청북도 청주시 서원구 개신동 1 충북대학교", "ChungbukNational");
insert into library_opiton_tb(company_fk, option_name, search_option) 
    values(1,"중앙도서관","&f=(BR%3A%26quot%3B01%26quot%3B)");
insert into library_opiton_tb(company_fk, option_name, search_option) 
    values(1,"의학도서관","&f=(BR%3A%26quot%3B02%26quot%3B)");
insert into library_opiton_tb(company_fk, option_name, search_option) 
    values(1,"법학도서관","&f=(BR%3A%26quot%3B03%26quot%3B)");
insert into library_opiton_tb(company_fk, option_name, search_option) 
    values(1,"과학기술도서관","&f=(BR:04)");
insert into library_opiton_tb(company_fk, option_name, search_option) 
    values(1,"출판내림차순","&s=S_PYB&st=DESC");
insert into library_opiton_tb(company_fk, option_name, search_option) 
    values(1,"출판오름차순","&s=S_PYB&st=ASC");
insert into library_opiton_tb(company_fk, option_name, search_option) 
    values(1,"인기내림차순","&s=S_CHGCNT&st=DESC");
insert into library_opiton_tb(company_fk, option_name, search_option) 
    values(1,"인기오름차순","&s=S_CHGCNT&st=ASC");

insert into comapny_tb(register_id, company_nm, address) values(0,"temp","-");
alter table book_tb add foreign key(nfc_id_fk) references nfc_tb(id) on delete cascade;
alter table book_tb add foreign key(company_fk) references company_tb(register_id) on delete cascade;
alter table qna_tb add foreign key(userkey_fk) references user_tb(userkey_id) on delete cascade;
alter table user_tb add foreign key(library) references company_tb(register_id) on delete cascade;
alter table library_opiton_tb add foreign key(company_fk) references company_tb(register_id) on delete cascade;
alter table company_tb modify latitude char(50);
alter table company_tb modify longitude char(50);

alter table nfc_tb add company_fk integer default 0;
alter table nfc_tb add foreign key(company_fk) references company_tb(register_id) on delete cascade;
alter table book_tb drop company_fk; 