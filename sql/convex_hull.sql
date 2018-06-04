select st_concavehull(ST_union(geom),.4) as geom from brazil_2015_2016;
