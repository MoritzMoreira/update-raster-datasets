import vrt2poly
from qgis.core import (QgsProject, QgsVectorLayer)
from qgis.utils import iface
import os
import importlib
importlib.reload(vrt2poly)
import processing

def ermittle_relKach(proj, massstab, layer, raster):
    if QgsProject.instance().mapLayersByName('polygon_footprint'):
        pass
    else:
        if os.path.exists(r"%s/Zwischenschritte/Vektor/polygon_footprint.gpkg" % proj):
            os.remove(r"%s/Zwischenschritte/Vektor/polygon_footprint.gpkg" % proj)
        vrt2poly.vrt2poly(proj, layer, raster)

    if QgsProject.instance().mapLayersByName(f'vertriebskacheln{massstab}'):
        pass
    else:
        if layer == "col":
            vector_vertrKach = QgsVectorLayer(r"%s/Ressourcen/vertriebskacheln%s.shp"%(proj, massstab),  f"vertriebskacheln{massstab}", "ogr")
        else:
            vector_vertrKach = QgsVectorLayer(r"%s/Ressourcen/vertriebskachelnDOP20.shp"%proj, f"vertriebskacheln{massstab}", "ogr")
        QgsProject.instance().addMapLayer(vector_vertrKach)

    processing.run("qgis:selectbylocation",
                  {"INPUT": f'vertriebskacheln{massstab}', "PREDICATE": 0, "INTERSECT": "polygon_footprint", "METHOD": 0})   #r"%s/Zwischenschritte/Vektor/poly_Ftpr.gpkg"%proj
    processing.run("qgis:selectbylocation",
                   {"INPUT": f'vertriebskacheln{massstab}', "PREDICATE": 4, "INTERSECT": "polygon_footprint", "METHOD": 3})

    dtk_nummern = []
    vertr_kach = QgsProject.instance().mapLayersByName(f'vertriebskacheln{massstab}')[0]
    for feature in vertr_kach.selectedFeatures():
        dtk_nummern.append(feature['id'])
    return dtk_nummern