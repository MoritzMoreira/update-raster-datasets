import processing
from datetime import datetime

def vrt2poly(proj, layer, raster):
     # Umwandlung des Rasters in Polygon in 3 Schritten:
    if layer == "col":
        processing.run('gdal:translate',       # Parameter "-b: band mask": "maskiert" das erste Band des Input-Rasters, projeziert alle Pixelwerte außer 0 auf 255 => Raster mit 2 Pixelwerten
                               {'INPUT': r"%s/Zwischenschritte/Raster/neu/r_clip2x_%s_%s.vrt" % (proj, layer, raster[-7:-4]),
                                'OUTPUT': r"%s/Zwischenschritte/Raster/neu/translate_mask.vrt" % proj, 'EXTRA': '-b mask', 'NODATA': 0})
        processing.run('gdal:translate',                    # durch 2. translate mit Nodata=0 werden die Null-Pixel eliminiert => Raster mit einem Pixelwert
                       {'INPUT': r"%s/Zwischenschritte/Raster/neu/translate_mask.vrt" % proj,'OUTPUT': r"%s/Zwischenschritte/Raster/neu/translate2.tif" % proj, 'EXTRA': '-b 1', 'NODATA': 0})

        c = datetime.now()
        processing.runAndLoadResults('gdal:polygonize',                   # Umwandlung in Polygon
                                    {'INPUT': r"%s/Zwischenschritte/Raster/neu/translate2.tif" % proj, 'OUTPUT': r"%s/Zwischenschritte/Vektor/polygon_footprint.gpkg" % proj, 'BAND': 1})
        d = datetime.now()
        print("Zeit polygonize: ", d - c)
    pass

