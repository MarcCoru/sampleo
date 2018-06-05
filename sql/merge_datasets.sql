DROP TABLE IF EXISTS data;

CREATE TABLE data (id serial primary key, geom geometry, name text, year text, origin text);

INSERT INTO data(geom, name, year, origin)
(select st_transform(geom,4326) as geom, cult_nom as name, campagne as year, 'belgium2015' as origin from belgium2015)
union all
(select st_transform(geom,4326) as geom, cult_nom as name, campagne as year, 'belgium2016' as origin from belgium2015)
union all
(select st_transform(geom,4326) as geom, nutzung as name, '2016' as year, 'bavaria2016' as origin from bavaria2016)
union all
(select st_transform(geom,4326) as geom, nutzung as name, '2017' as year, 'bavaria2017' as origin from bavaria2017)
union all
(select st_transform(geom,4326) as geom, c.nom_culture as name, '2016' as year, 'toulouse' as origin from toulouse as d, rpg_codes_cultures_2016 as c where d.code_cultu=c.code_culture)
union all
(select st_transform(geom,4326) as geom, mai_2016 as name, '2016' as year, 'brazil_2015_2016' as origin from brazil_2015_2016);

CREATE INDEX IF NOT EXISTS data_geom_idx ON data USING GIST (geom);
