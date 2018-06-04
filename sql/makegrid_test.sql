SELECT (
		ST_Dump(
			makegrid_2d(
			st_envelope(st_transform(geom,32632)),
			10000) -- cell step in meters
		)
		).geom AS geom 
from 
	regions 
where 
	name='walonne'
