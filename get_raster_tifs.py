from geetools import tools
import ee
import geojson
import geopandas as gpd
import argparse

def parse_args():
        
    description="""
    Queries GEE and returns raster time series as tif images

    python get_raster_tifs.py --geojson 'data/7777.geojson' --bucket 'sampleo' --folder tif/7777 --startdate 2016-01-01 --enddate 2016-12-31 --collection "COPERNICUS/S2"
    """

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('--geojson', type=str,
                        help="jsonfile defining geojson location",
                        default='data/7777.geojson')              
    parser.add_argument('-ts','--startdate', type=str, 
                        default='2016-01-01', 
                        help='format YYYY-MM-DD')
    parser.add_argument('-te','--enddate', type=str, 
                        default='2016-12-31',
                        help='format YYYY-MM-DD')
    parser.add_argument('-b','--bucket', 
                        type=str, default="sampleo", 
                        help='folder name')
    parser.add_argument('-f','--folder', 
                        type=str, default="tif/7777", 
                        help='folder name')
    parser.add_argument('-c','--collection', 
                        type=str, default='COPERNICUS/S1_GRD', 
                        help='GEE id as collection e.g., COPERNICUS/S2')
    parser.add_argument('-s','--scale', 
                        type=int, default=10, 
                        help='scale or ground sampling distance of output image')

    return parser.parse_args()

def main(geojson_file="data/7777.geojson", 
    bucket='sampleo', 
    folder="tif/7777", 
    collection_id="COPERNICUS/S2",
    datefrom='2017-01-01', 
    dateto='2017-12-31',
    scale=10):

    ee.Initialize()

    with open(geojson_file) as f:
        gj = geojson.load(f)
    pt_list = gj['features'][0]["geometry"]["coordinates"][0]
    geom = ee.Geometry.Polygon(pt_list)

    aoi_bounds = gpd.read_file(geojson_file).bounds
    xmin, ymin, xmax, ymax =aoi_bounds.values[-1]
    bbox=(xmin, ymin, xmax, ymax)

    tasks = query(
            collection_id, 
            bbox, 
            bucket, 
            folder+'/'+collection_id.replace("/","")+"/", 
            datefrom=datefrom, 
            dateto=dateto,
            scale=scale)


def query(collection_id, bbox, bucket, prefix, datefrom="2018-01-01", dateto="2018-05-01", scale=10):

    xmin,ymin,xmax,ymax = bbox
    region=ee.Geometry.Rectangle([xmin,ymin,xmax,ymax])

    collection = ee.ImageCollection(collection_id).filterDate(datefrom, dateto).filterBounds(region)

    tasks=list()

    if collection_id == "COPERNICUS/S2":
        
        if scale==10:
            col = collection.select(['B2','B3','B4','B8'])
            tasks += col2gcs(col, bucket, fileNamePrefix=prefix, region=region, scale=scale)
        elif scale==20:
            col = collection.select(['B5','B6','B7','B8A','B11','B12'])
            tasks += col2gcs(col, bucket, fileNamePrefix=prefix, region=region, scale=scale)
        elif scale==60:
            col = collection.select(['B1','B9','B10'])
            tasks += col2gcs(col, bucket, fileNamePrefix=prefix, region=region, scale=scale)
        else:
            raise ValueError("{} is not a valid scale at {}. allowed are 10, 20 or 60".format(scale,collection_id))

    elif collection_id == "COPERNICUS/S1_GRD":
        if scale==10:
            col = collection.select(["HH", "HV"])
            tasks += col2gcs(col, bucket, fileNamePrefix=prefix, region=region, scale=scale)
        else:
            raise ValueError("{} is not a valid scale at {}. allowed is 10".format(scale,collection_id))

    elif collection_id == "LANDSAT/LC08/C01/T1_SR":
        if scale==30:
            col = collection.select(["B1", "B2", "B3", "B4", "B5", "B6", "B7"])
            tasks += col2gcs(col, bucket,fileNamePrefix=prefix, region=region, scale=scale)
        elif scale==100:
            col = collection.select(["B10","B11"])
            tasks += col2gcs(col, bucket,fileNamePrefix=prefix, region=region, scale=scale)
        else:
            raise ValueError("{} is not a valid scale at {}. allowed is 30 or 100".format(scale,collection_id))

    else:
        raise ValueError("no valid collection_id inserted: implemented are 'COPERNICUS/S2', 'COPERNICUS/S1_GRD', 'LANDSAT/LC08/C01/T1_SR' ")

    return tasks


def col2gcs(col, bucket, fileNamePrefix=None, scale=30, dataType="float", region=None, **kwargs):
    """ Upload all images from one collection to Google Drive. You can use the
    same arguments as the original function ee.batch.export.image.toDrive
    :param col: Collection to upload
    :type col: ee.ImageCollection
    :param region: area to upload. Defualt to the footprint of the first
        image in the collection
    :type region: ee.Geometry.Rectangle or ee.Feature
    :param scale: scale of the image (side of one pixel). Defults to 30
        (Landsat resolution)
    :type scale: int
    :param maxImgs: maximum number of images inside the collection
    :type maxImgs: int
    :param dataType: as downloaded images **must** have the same data type in all
        bands, you have to set it here. Can be one of: "float", "double", "int",
        "Uint8", "Int8" or a casting function like *ee.Image.toFloat*
    :type dataType: str
    :return: list of tasks
    :rtype: list
    """
    TYPES = {'float': ee.Image.toFloat,
         'int': ee.Image.toInt,
         'Uint8': ee.Image.toUint8,
         'int8': ee.Image.toInt8,
         'double': ee.Image.toDouble}

    size = col.size().getInfo()
    alist = col.toList(size)
    tasklist = []

    #region = ee.Image(alist.get(0)).geometry().getInfo()["coordinates"]
    region = tools.getRegion(region)

    for idx in range(0, size):
        img = alist.get(idx)
        img = ee.Image(img)
        name = img.id().getInfo().split("/")[-1] + "_" + str(scale) + "m"

        if dataType in TYPES:
            typefunc = TYPES[dataType]
            img = typefunc(img)
        elif dataType in dir(ee.Image):
            img = dataType(img)
        else:
            raise ValueError("specified data type is not found")

        if fileNamePrefix is None:
            fileNamePrefix = name

        task = ee.batch.Export.image.toCloudStorage(image=img,
                                             description=name,
                                             bucket=bucket,
                                             fileNamePrefix=fileNamePrefix+name,
                                             region=region,
                                             scale=scale)
        
        print("starting task {}/{} of {}".format(idx,size,name))
        task.start()
        tasklist.append(task)

    return tasklist

if __name__ == "__main__":
    args = parse_args()
    main(args.geojson, 
        args.bucket, 
        args.folder, 
        args.collection, 
        args.startdate, 
        args.enddate,
        args.scale)