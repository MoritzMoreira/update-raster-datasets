import processing
from qgis.core import (QgsProject, QgsVectorFileWriter, QgsProcessingFeatureSourceDefinition, QgsFeatureRequest)
from qgis.utils import iface

def clip_D(dtk_nummern, layer, proj, massstab):
    for dtkNummer in dtk_nummern:
        if QgsProject.instance().mapLayersByName(f"raster_{dtkNummer}_{layer}"):
            pass
        else:
            vertr = QgsProject.instance().mapLayersByName("vertriebskacheln%s"%massstab)[0]
            vertr.selectByExpression(f'"id" = \'{dtkNummer}\'')
            param_clip_final = {'INPUT': r'%s/Zwischenschritte/Raster/zusammen/vr_%s.vrt' % (proj, layer),
                                'MASK': QgsProcessingFeatureSourceDefinition(  r"%s/Ressourcen/vertriebskachelnDOP20.shp" % proj, selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                                'CROP_TO_CUTLINE': True,
                                'OUTPUT': r"%s/Ergebnis/raster_%s_%s.tif" % (proj, dtkNummer, layer)}
            if layer != "DOP":
                param_clip_final['MASK'] = QgsProcessingFeatureSourceDefinition(r"%s/Ressourcen/vertriebskacheln%s.shp"%(proj, massstab),
                                                                                selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid)

            processing.run("gdal:cliprasterbymasklayer", param_clip_final)

            iface.addRasterLayer(r"%s/Ergebnis/raster_%s_%s.tif"%(proj, dtkNummer, layer))
    pass