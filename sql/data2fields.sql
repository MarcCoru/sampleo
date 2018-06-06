drop table if exists wms.fields;
create table wms.fields (id serial primary key, geom geometry, class text, year text, origin text);
insert into wms.fields(geom, class, year, origin)
select geom, m.class as class, year, origin from data d, map m where d.name=m.name and m.class is not Null;
create index fields_idx on wms.fields using gist(geom);
