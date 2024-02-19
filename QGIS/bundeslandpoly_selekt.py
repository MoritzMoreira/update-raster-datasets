from qgis.core import (QgsProject, QgsVectorFileWriter, QgsVectorLayer)

def selektiere_BLpoly(bundesland, proj, massstab):
    if QgsProject.instance().mapLayersByName("laenderpolygone"):
        pass
    else:
        laenderpolygone = QgsVectorLayer(r'%s/Ressourcen/laenderpolygone%s.shp' % (proj, massstab), "laenderpolygone", "ogr")  # Länderpolygone holen
        QgsProject.instance().addMapLayer(laenderpolygone)
        laenderpolygone.selectByExpression(f'"LAND" = \'{bundesland}\'')  # Polygon des betroffenen Bundeslandes selektieren und exportieren
    pass