drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  name text not null,
  lastCrawl integer not null,
  imgURL text not null,
  hash text not null
);
