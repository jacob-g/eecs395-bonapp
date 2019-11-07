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
  name varchar(225) not null,
  role varchar(225) not null
);

create table review (
  id int not null auto_increment primary key,
  user varchar(225) not null,
  rating int not null,
  comments varchar(140) not null,
  item int not null,
  time_stamp timestamp not null default current_timestamp
);

create table statuses (
  id int not null auto_increment primary key,
  item_id int not null,
  status varchar(225) not null,
  dining_hall varchar(225) not null references dining_hall (name),
  time_stamp timestamp not null default current_timestamp,
  user varchar(225) not null
);

create table menu_item (
  id int not null auto_increment primary key,
  name varchar(225) not null
);

create table dining_hall (
  name varchar(225) not null primary key,
  breakfast varchar(225),
  lunch varchar(225),
  dinner varchar(225),
  brunch varchar(225)
);

create table inventory_item (
  id int not null auto_increment primary key,
  name varchar(225) not null
);

-- represent relations
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
  id int not null auto_increment primary key,
  menu_item_id int not null references menu_item (id),
  dining_hall_name varchar(225) not null references dining_hall (name),
  meal varchar(225) not null,
  date_of date not null
);

create table alert (
  id int not null auto_increment primary key,
  user varchar(225) not null references user (id),
  menu_item_id int not null references menu_item (id)
);

-- restrict ratings to (0,5)
create table allowed_scores (
  score int not null primary key
);

insert into allowed_scores (score) values (1), (2), (3), (4), (5);
alter table review add foreign key (rating) references allowed_scores (score);
alter table status add foreign key (status) references allowed_scores (score);

-- add foreign key constraints
alter table review add foreign key (user) references user (id);
alter table review add foreign key (item) references serves (id);
alter table statuses add foreign key (item_id) references inventory_item (id);
