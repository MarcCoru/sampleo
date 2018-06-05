drop table if exists map;
create table map (id serial primary key, name text, parcels int, class text, classid int);

insert into map (name, parcels)
select
  name as name,
  count(name) as parcels
from data
group by name
order by parcels desc;
