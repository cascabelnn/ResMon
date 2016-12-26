drop table if exists reslist;
create table reslist (
  id integer primary key autoincrement,
  url CHAR(24) not null,
  times integer DEFAULT 10,
  status CHAR(2) DEFAULT NA  
);