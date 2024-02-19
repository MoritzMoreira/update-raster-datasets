from qgis.core import (QgsProject, QgsVectorLayer)

def lade_erf(massstab, utm, proj):
    if QgsProject.instance().mapLayersByName(f'erfassungskacheln{massstab}'):  # Erfassungseinheiten einladen
        pass
    else:
        erfassungseinheiten = QgsVectorLayer(r"%s/Ressourcen/erfassungskacheln%s%s.shp"%(proj, massstab, utm), "erfassungskacheln%s"%massstab, "ogr")
        QgsProject.instance().addMapLayer(erfassungseinheiten)
    pass