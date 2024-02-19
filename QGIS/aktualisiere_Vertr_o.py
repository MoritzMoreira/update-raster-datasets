from osgeo import gdal
import os
from qgis.core import (QgsApplication, QgsProcessingFeedback, QgsVectorLayer, QgsProject, QgsVectorFileWriter, QgsRasterLayer, QgsCoordinateReferenceSystem, QgsProcessingFeatureSourceDefinition, QgsFeatureRequest)
import processing
from qgis.utils import iface
import importlib
from datetime import datetime
import lade_erfassungseinheiten, pixel_tauschen, Dateien_loeschen, bundeslandpoly_selekt, rel_besKacheln, vrt2poly, clip

importlib.reload(pixel_tauschen)
importlib.reload(Dateien_loeschen)
importlib.reload(lade_erfassungseinheiten)
importlib.reload(bundeslandpoly_selekt)
importlib.reload(vrt2poly)
importlib.reload(rel_besKacheln)
importlib.reload(clip)

proj = QgsProject.instance().readPath("./")

def aktualisiere_Vertriebskacheln(neue_Raster_p, bundesland, massstab, utm, layer, dtk_nummern):

    # 1. neue Raster
    # 1.1 neue Raster holen und ggf. auf Kartenblätter begrenzen **************************************************************************************************************************************************************
    raster_clip_kb = []
    poly_pfade = []
    if layer == "col":
        lade_erfassungseinheiten.lade_erf(massstab, utm, proj)
    DOP_dateinamen = []
    for root, dirs, files in os.walk(neue_Raster_p):  # neue Raster in Verzeichnis suchen und Pfade in Liste speichern
        for file in files:
            if file.endswith(f'{layer}.tif'):
                pfad = os.path.join(root, file)
                dtk_nr = file[:5]
                if massstab == "25":
                    dtk_nr = file[:4]
                if layer != "col":                      # Pixelwerte der schwarz-weiß-Layer tauschen für Zusammenführung mit Bestandsrastern
                    pfad = pixel_tauschen.tausche_pix(dtk_nr, layer, pfad)

                if QgsProject.instance().mapLayersByName(f'neue_kbClip_{layer}'):
                    pass
                else:
                    Dateien_loeschen.loesche_dat(dtk_nr, layer, proj)           #ggf. alte Dateien im Verzeichnis löschen

                    erfassungseinheiten = QgsProject.instance().mapLayersByName("erfassungskacheln%s" % massstab)[0]  # Das zum Raster zugehörige Polygon über die DTK-Nummer selektieren
                    erfassungseinheiten.selectByExpression(f'"dtknr" LIKE \'{dtk_nr}\'')
                    if erfassungseinheiten.selectedFeatureCount() == 0:  # Wenn die neuen Daten nicht im Kartenblattformat kommen wird nicht geclipped (kein Feature wird im vorigen schritt selektiert)
                        raster_clip_kb.append(pfad)  #r"%s/Zwischenschritte/Raster/neu/neu_%s_%s.vrt" % (proj, dtk_nr, layer)
                    else:
                        if layer == "col":
                            processing.runAndLoadResults('gdal:translate', {'INPUT': pfad, 'OUTPUT': r"%s/Zwischenschritte/Raster/neu/translate_%s_%s.vrt"%(proj,dtk_nr,layer),'EXTRA': '-b 1','NODATA': 0})
                            raster = QgsRasterLayer(r"%s/Zwischenschritte/Raster/neu/translate_%s_%s.vrt"%(proj, dtk_nr, layer), f"vrt_{dtk_nr}")
                            QgsProject.instance().addMapLayer(raster)
                            processing.run("gdal:rastercalculator", {'INPUT_A': r"%s/Zwischenschritte/Raster/neu/translate_%s_%s.vrt"%(proj,dtk_nr,layer),
                                                                     'BAND_A':1, 'FORMULA':'(A!=0)','NO_DATA':0,'RTYPE':5,'OPTIONS':'','EXTRA':'',
                                                                     'OUTPUT':r"%s/Zwischenschritte/Raster/neu/calc_%s.tif"%(proj, dtk_nr)})
                            c = datetime.now()
                            processing.runAndLoadResults('gdal:polygonize', {'INPUT':  r"%s/Zwischenschritte/Raster/neu/calc_%s.tif"%(proj, dtk_nr),  #r"%s/Zwischenschritte/Raster/neu/translate2.tif" % proj
                                                                             'OUTPUT': r"%s/Zwischenschritte/Vektor/p_%s.shp"%(proj, dtk_nr),  #r"%s/Zwischenschritte/Vektor/p_%s.gpkg"%(proj, dtk_nr)
                                                                             'BAND':1,'FIELD':'DN','EIGHT_CONNECTEDNESS':False,'EXTRA':''})
                            poly_pfade.append(r"%s/Zwischenschritte/Vektor/p_%s.shp"%(proj, dtk_nr))
                            d = datetime.now()
                            print("Zeit polygonize: ", d - c)
                        else:
                            processing.runAndLoadResults('gdal:translate', {'INPUT': pfad, 'OUTPUT': r"%s/Zwischenschritte/Raster/neu/translate_%s_%s.vrt"%(proj,dtk_nr,layer),'EXTRA': '-b 1','NODATA': 1})
                        raster_clip_kb.append(r"%s/Zwischenschritte/Raster/neu/translate_%s_%s.vrt"%(proj, dtk_nr, layer))
                    if len(raster_clip_kb) == 0:
                        return dtk_nummern

            if layer == "DOP" and file.endswith(".tif"):
                pfad = os.path.join(root, file)
                raster_clip_kb.append(pfad)
                DOP_dateinamen.append(file[10:12] + file[13:23])
    if layer == "col":
        if os.path.isfile(r"%s/Zwischenschritte/Vektor/polygon_footprint.gpkg"%proj):
            os.remove(r"%s/Zwischenschritte/Vektor/polygon_footprint.gpkg"%proj)
        processing.runAndLoadResults("native:mergevectorlayers", {'LAYERS': poly_pfade,'CRS': None, 'OUTPUT': r"%s/Zwischenschritte/Vektor/polygon_footprint.gpkg"%proj})

    # vrt mit allen neuen und ggf. auf Kartenblätter geclippten Rastern erstellen
    if QgsProject.instance().mapLayersByName(f'neue_kbClip_{layer}'):
        print("la",layer)
        pass
    else:
        print(layer)
        gdal.BuildVRT(r'%s/Zwischenschritte/Raster/neu/neue_kbClip_%s.vrt' % (proj, layer), raster_clip_kb)
        iface.addRasterLayer(r'%s/Zwischenschritte/Raster/neu/neue_kbClip_%s.vrt' % (proj, layer))

    '''
    # 1.2 neue Raster auf Bundesland begrenzen **************************************************************************************************************************************************************
    if layer == "col" or layer == "DOP":
        bundeslandpoly_selekt.selektiere_BLpoly(bundesland, proj, massstab)

    if QgsProject.instance().mapLayersByName(f'r_clip2x_{layer}'):
        pass
    else:
        clip_param = {'INPUT': r'%s/Zwischenschritte/Raster/neu/neue_kbClip_%s.vrt'%(proj, layer),
                      'MASK': QgsProcessingFeatureSourceDefinition(r'%s/Ressourcen/laenderpolygone%s.shp'%(proj, massstab), selectedFeaturesOnly=True, featureLimit=-1, geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid), \
                      'CROP_TO_CUTLINE': False, 'KEEP_RESOLUTION': True,
                      'OUTPUT': r"%s/Zwischenschritte/Raster/neu/r_clip2x_%s.vrt" % (proj, layer), 'NODATA': 0}
        if layer != "col":
            clip_param['NODATA'] = None
        if raster_clip_kb[0][0] == "r" and layer != "col":
            clip_param['NODATA'] = 1


        processing.run("gdal:cliprasterbymasklayer", clip_param)

        iface.addRasterLayer(r"%s/Zwischenschritte/Raster/neu/r_clip2x_%s.vrt" % (proj, layer))
    '''
    # 2. Bestandsraster
    if layer == "col" or layer == "DOP":
        # 2.1 relevante Vertriebskacheln ermitteln **************************************************************************************************************************************************************
        dtk_nummern = rel_besKacheln.ermittle_relKach(proj, massstab, layer, "")

    # 2.2 Bestandskacheln in Verzeichnis suchen und Pfade in Liste speichern
    l_raster_alt = []
    if layer == "DOP":
        for root, dirs, files in os.walk(r"\\lsv896\Dop20\%s"%bundesland.lower()):  # neue Raster in Verzeichnis suchen und Pfade in Liste speichern
            for file in files:
                if file.endswith(".tif"):
                    if file[10:12]+file[13:23] == DOP_dateinamen[0] or file[10:12]+file[13:23] == DOP_dateinamen[1]:
                        l_raster_alt.append(os.path.join(root, file))

    # ToDo: Bestands - VRT editieren
    else:
        for root, dirs, files in os.walk(r'S:\dtk%s\utm32s/vertrieb'%massstab):
            for file in files:
                if massstab == "100":  # ToDo: Regular Expression
                    if file[0:20] in dtk_nummern and file.endswith(f'{layer}.tif'):
                        l_raster_alt.append(os.path.join(root, file))
                else:
                    if file[0:19] in dtk_nummern and file.endswith(f'{layer}.tif'):
                        l_raster_alt.append(os.path.join(root, file))
                    if file[10:23] in dtk_nummern and file.endswith('.tif'):
                        l_raster_alt.append(os.path.join(root, file))

    # 3. alte Raster mit neuen zusammenfügen (zweites Listenelement liegt über erstem) **************************************************************************************************************************************************************
    if QgsProject.instance().mapLayersByName(f'vr_{layer}'):
        pass
    else:
        gdal.BuildVRT(r'%s/Zwischenschritte/Raster/alt/%s_%s_%s_vr.vrt' % (proj, bundesland, massstab, layer), l_raster_alt)            #Bestandsraster
        gdal.BuildVRT(r'%s/Zwischenschritte/Raster/zusammen/vr_%s.vrt' % (proj, layer),
                     [r'%s/Zwischenschritte/Raster/alt/%s_%s_%s_vr.vrt' % (proj, bundesland, massstab, layer), r"%s/Zwischenschritte/Raster/neu/r_clip2x_%s.vrt"%(proj, layer)])
        iface.addRasterLayer(r'%s/Zwischenschritte/Raster/zusammen/vr_%s.vrt' % (proj, layer))

    # Vertriebseinheiten vom Mosaik ausstanzen ************************************************************************************************************************************************
    clip.clip_D(dtk_nummern, layer, proj, massstab)

    return dtk_nummern

if __name__ == '__main__':
    aktualisiere_Vertriebskacheln("a","b","c","d", "e")