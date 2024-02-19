import sys, os, copy, arcpy, importlib
sys.path.insert(0, r'D:\Praktikanten\Hackenberg_Moritz\DTK-Workflow-test\Services_test\mdcs-dtk\scripts')
import logger, Base, solutionsLib, MDCS
from pathlib import Path
from datetime import datetime
import DTK_Nummern_Bestand, clip

importlib.reload(clip)
importlib.reload(DTK_Nummern_Bestand)

def aktualisiere_Raster(LAYERS, massstab, param_d, param_s, bundesland, datum, dop_nummern):
    for layer in LAYERS:
        # Layer an Paramenterliste anfügen
        param_s.append(f"-p:{layer}$layer")
        param_d.append(f"-p:{layer}$layer")

        if arcpy.Exists(f"{arcpy.env.workspace}\S_{layer}"):
            pass
        else:
            arcpy.AddMessage("else")
            MDCS.main(len(param_s), param_s)

        # DTK-Nummern der Bestandskacheln, die mit den neuen Daten überlappen in Liste speichern (Vertriebseinheiten)
        if layer == "col" or "DOP":
            return_dtkNum = DTK_Nummern_Bestand.ermittle_dtkNum(massstab, bundesland, datum)
            kachel_str = return_dtkNum[0]
            kachel_liste = return_dtkNum[1]

        # Anhand der DTK-Nummern die relevanten Bestandskacheln selektieren
        if layer != "DOP":
            arcpy.management.MakeMosaicLayer(r"D:\Praktikanten\Hackenberg_Moritz\DTK-Workflow-test\dtk%s_Bestand.gdb\dtk%s_%s_utm32s"%(massstab,massstab,layer), "bestand_%s_lyr"%layer)
            arcpy.management.SelectLayerByAttribute(r"bestand_%s_lyr"%layer, 'NEW_SELECTION', f"GroupName IN ({kachel_str})")
        else:
            arcpy.management.MakeMosaicLayer(r"D:\Praktikanten\Hackenberg_Moritz\DTK-Workflow-test\Services_test\Services_test.gdb\dop20_de_rgbi", "bestand_%s_lyr"%layer)
            arcpy.AddMessage(dop_nummern+"   dop nummern")
            arcpy.management.SelectLayerByAttribute(r"bestand_%s_lyr"%layer, 'NEW_SELECTION', f"GroupName IN ({dop_nummern})")

        if arcpy.Exists(f"{arcpy.env.workspace}\{layer}_md_d"):
            pass
        else:                                            # Mosaikdataset für Bestandsraster erstellen
            if layer == "col":
                arcpy.CreateMosaicDataset_management(arcpy.env.workspace, "%s_md_d" % layer, "25832", "1", "8_BIT_UNSIGNED")
                arcpy.management.SetMosaicDatasetProperties("%s_md_d" % layer, allowed_compressions = "NONE")
            if layer == "DOP":
                arcpy.CreateMosaicDataset_management(arcpy.env.workspace, "%s_md_d" % layer, "25832", "4", "8_BIT_UNSIGNED")
                arcpy.management.SetMosaicDatasetProperties("%s_md_d" % layer, allowed_compressions= "NONE")
            else:
                arcpy.CreateMosaicDataset_management(arcpy.env.workspace, "%s_md_d"%layer, "25832", "1", "1_BIT")
                arcpy.management.SetMosaicDatasetProperties("%s_md_d" % layer, allowed_compressions = "NONE")

            arcpy.management.MakeMosaicLayer("%s\%s_md_d"%(arcpy.env.workspace, layer), f"{layer}_md_d_lyr")
            arcpy.env.pyramid = "NONE"
            arcpy.env.compression = "NONE"
            arcpy.env.rasterStatistics = "NONE"
            arcpy.management.AddRastersToMosaicDataset(f"{layer}_md_d_lyr", "Table", "bestand_%s_lyr"%layer)

        if arcpy.Exists("%s\D_%s"%(arcpy.env.workspace, layer)):                # abgeleitetes Mosaik-Dataset mit neuen und alten Rastern erstellen
            pass
        else:
            MDCS.main(len(param_d), param_d)

        # Clip Raster für Ausstanzen der Vertriebseinheiten aus Mosaikdatasets
        clip.clip_D(layer, kachel_liste)


        #Layerparameter aus Parameterliste löschen
        param_s.pop()
        param_d.pop()

        if layer == "col":
            # Modifikation des Pixeltyps in den Parameterlisten für die schwarz-weiß-Layer
            param_s[9] = "-p:1_BIT$pixeltype"
            param_d[9] = "-p:1_BIT$pixeltype"

    return kachel_liste



