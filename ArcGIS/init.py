import copy, sys, os, arcpy, importlib
import sys
sys.path.insert(0, r'D:\Praktikanten\Hackenberg_Moritz\DTK-Workflow-test\Services_test\mdcs-dtk\scripts')
import logger, Base, solutionsLib, MDCS
from pathlib import Path
from datetime import datetime
import DTK_Nummern_Bestand, clip, aktualisiere_Raster, color_map

importlib.reload(aktualisiere_Raster)
importlib.reload(color_map)
importlib.reload(clip)

def ScriptTool(neue_Raster_p):
    # ID-String zusammenstellen     W:\dtk100\he\2023-03-27  D:\Praktikanten\Hackenberg_Moritz\DOP\sl\2022\2022-09-19
    bundesland = "TH"  #str(Path(neue_Raster_p).parents[0])[-2:].upper()
    if str(Path(neue_Raster_p).parents[2])[-3:] == "DOP":
        bundesland = str(Path(neue_Raster_p).parents[1])[-2:].upper()
        vertr_pfad = r"M:\DTK-N-Repository\Ressourcen\SDE\Vertriebseinheiten@lsvpgsql2.sde\vertriebseinheiten.kacheln.dop_k1_utm32s"
        cellsize = 0.2

    datum = datetime.today().strftime('%Y-%m-%d')+"_3"

    # Maßstab und UTM-Zone aus Pfad holen
    if bundesland == "BE" or bundesland == "BB" or bundesland == "MV" or bundesland == "SN":
        srs = "25833"
        utm = "3"
        if str(Path(neue_Raster_p).parents[2])[-3:] == "DOP":
            vertr_pfad = r"M:\DTK-N-Repository\Ressourcen\SDE\Vertriebseinheiten@lsvpgsql2.sde\vertriebseinheiten.kacheln.dop_k1_utm33s"


    else:
        srs = "25832"
        utm = "2"

    massstab = "50"  #str(Path(neue_Raster_p).parents[1])[-2:]
    if massstab == "00":
        massstab = "100"
        cellsize = 5
        vertr_pfad = r"M:\DTK-N-Repository\Ressourcen\SDE\Vertriebseinheiten@lsvpgsql2.sde\vertriebseinheiten.kacheln.dtk100_k40_utm32s"
    if massstab == "25":
        cellsize = 1.25
        vertr_pfad = r"M:\DTK-N-Repository\Ressourcen\SDE\Vertriebseinheiten@lsvpgsql2.sde\vertriebseinheiten.kacheln.dtk25_k10_utm32s"
    elif massstab == "50":
        cellsize = 2.5
        vertr_pfad = r"M:\DTK-N-Repository\Ressourcen\SDE\Vertriebseinheiten@lsvpgsql2.sde\vertriebseinheiten.kacheln.dtk50_k20_utm32s"

    # Pfade festlegen
    config =   os.path.dirname(__file__) + r"\mdcs-dtk\Parameter\Config\DTK_Source.xml"
    config_d = os.path.dirname(__file__) + r"\mdcs-dtk\Parameter\Config\DTK_Derived.xml"
    if str(Path(neue_Raster_p).parents[2])[-3:] == "DOP":
        config =   os.path.dirname(__file__) + r"\mdcs-dtk\Parameter\Config\DOP_Source.xml"
        config_d = os.path.dirname(__file__) + r"\mdcs-dtk\Parameter\Config\DOP_Derived.xml"
    workspace_pfad = str(os.path.dirname(__file__))
    data_pfad = Path(neue_Raster_p).as_posix()
    arcpy.MakeFeatureLayer_management(vertr_pfad, "vertriebskacheln_lyr")
    arcpy.env.workspace = Path(str(os.path.dirname(__file__)) + f"\dtk{massstab}_{bundesland}_{datum}.gdb").as_posix()
    if arcpy.Exists(arcpy.env.workspace):
        pass
    else:
        arcpy.management.CreateFileGDB(workspace_pfad, r"dtk%s_%s_%s.gdb"%(massstab,bundesland,datum))

    # Parameterliste für config-Datei
    param_s = ["x", f"-i:{config}", f"-p:{workspace_pfad}$workspace", f"-p:{bundesland}$land", f"-p:{srs}$srs", f"-p:{cellsize}$cellsize",
               f"-p:{data_pfad}$dataPath", f"-p:{utm}$utm", f"-p:{massstab}$massstab", "-p:8_BIT_UNSIGNED$pixeltype", f"-p:{datum}$datum"]
    param_d = copy.deepcopy(param_s)
    param_d[1] = f"-i:{config_d}"

    LAYERS = ['col', 'brac'] #, 'park', 'hrot', 'baum' , 'grau', 'babl', 'brac', 'grbr','haus', 'heid', 'hrot', 'mrot', 'rebr','schw', 'sebl', 'stge', 'stor', 'swtx', 'trup', 'utmg', 'viol', 'wald', 'watt', 'weis', 'wies']

    dop_nummern = ''
    if str(Path(neue_Raster_p).parents[2])[-3:] == "DOP":
        LAYERS = ["DOP"]
        for root, dirs, files in os.walk(neue_Raster_p):  # neue Raster in Verzeichnis suchen und Pfade in Liste speichern
            for file in files:
                if file.endswith('.tif'):
                    pfad = os.path.join(root, file)
                    dop_nr = "dop_"+file[10:12]+file[13:23]
                    dop_nummern += "'"+dop_nr+"',"
        dop_nummern = dop_nummern[:-1]

    # for-loop durch DTK-Layer
    kachel_liste = aktualisiere_Raster.aktualisiere_Raster(LAYERS, massstab, param_d, param_s, bundesland, datum, dop_nummern)

    pass

if __name__ == '__main__':
    neue_Raster = arcpy.GetParameterAsText(0)
    ScriptTool(neue_Raster)




