-- setup file for Bon Appetit Review Application
-- EECS 395, Group 14
-- Divya Manoharan

-- create database
create database review;

-- select database and add tables
use review;

create table contacts (
  dietician varchar(225) not null,
  leutner varchar(225) not null,
  fribley varchar(225) not null,
  general varchar(225) not null
);

create table user (
  id varchar(225) primary key,
  name varchar(225) not null
);

create table review (
  id int not null primary key,
  user varchar(225) not null,
  rating int not null,
  comments varchar(140) not null,
  item varchar(225) not null,
  time_stamp timestamp not null default current_timestamp,
);

create table statuses (
  id int not null auto_increment primary key,
  item_id int not null,
  status varchar(225) not null,
  dining_hall varchar(225) not null,
  time_stamp timestamp not null default current_timestamp,
  user varchar(225) not null
);

create table menu_item (
  id int not null auto_increment primary key,
  name varchar(225) not null,
  dining_hall varchar(225) not null
);

create table dining_hall (
  name varchar(225) not null primary key,
  breakfast varchar(225),
  lunch varchar(225),
  dinner varchar(225),
  brunch varchar(225)
);

create table facilities (
  id int not null auto_increment primary key,
  name varchar(225) not null
);

-- represent relations
create table reviews (
  user_id varchar(225) not null references user (id),
  review_id int not null references review (id),
  primary key (user_id, review_id)
);

create table status_of (
  status_id int not null references statues (item_id),
  facilities_id int not null references facilities (id),
  primary key (status_id, facilities_id)
);

create table inventories (
  user_id varchar(225) not null references user (id),
  status_id int not null references status (id),
  primary key (user_id, status_id)
);

create table review_of (
  review_id int not null references review (id),
  menu_item_id int not null references menu_item (id),
  primary key (review_id, menu_item_id)
);

create table serves (
  menu_item_id int not null references menu_item (id),
  dining_hall_name varchar(225) not null references dining_hall (name),
  primary key (menu_item_id, dining_hall_name),
  date_of timestamp not null
);

-- restrict ratings to (0,5)
create table allowed_scores (
  score int not null primary key
);

insert into allowed_scores (score) values (1), (2), (3), (4), (5);

alter table review add foreign key (rating) references allowed_scores (score);

-- add foreign key constraints
alter table statuses add foreign key (item_id) references menu_item (id);
alter table menu_item add foreign key (dining_hall) references dining_hall (name);
