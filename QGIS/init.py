import sys
from datetime import datetime
a = datetime.now()
from pathlib import Path
import aktualisiere_Vertr_o
import aktualisiere_Vertr_e
import aktualisiere_Vertr_t
import aktualisiere_Vertr
import aktualisiere_Vertr_v
import importlib
from qgis.utils import iface

importlib.reload(aktualisiere_Vertr)
importlib.reload(aktualisiere_Vertr_e)
importlib.reload(aktualisiere_Vertr_t)
importlib.reload(aktualisiere_Vertr_o)
importlib.reload(aktualisiere_Vertr_v)

proj = QgsProject.instance().readPath("./")

Optionen= ["1. Berlin (1) DTK100", "2. Rheinland-Pfalz (1) DTK100", "5. Thüringen (2) DTK50", "9. Rheinland-Pfalz (5) DTK100",
           "10. Berlin (4) DTK25", "11. Bremen (1) DTK25", "12. Hessen (4) DTK50", "13. Bremen (5) DTK100", "14. Saarland (2) DOP"]
inputStr = QInputDialog.getItem(None, r"W:\dtk100\rp\2022-11-24", "Ordnerpfad Eingangsdateien:", Optionen, 0, False)[0]
dict_pfade = {"1. Berlin (1) DTK100": r"%s\Testdaten\dtk100\be\2018-02-13"%proj, "2. Rheinland-Pfalz (1) DTK100": r"%s\Testdaten\dtk100\rp\2022-11-24"%proj, "5. Thüringen (2) DTK50": r"%s\Testdaten\dtk50\th\2023-07-10"%proj,
              "9. Rheinland-Pfalz (5) DTK100": r"%s\Testdaten\dtk100\rp\2022-12-13"%proj, "10. Berlin (4) DTK25": r"%s\Testdaten\dtk25\be\2023-07-06"%proj, "11. Bremen (1) DTK25": r"%s\Testdaten\dtk25\hb\2021-08-31"%proj,
              "12. Hessen (4) DTK50": r"%s\Testdaten\dtk50\he\2021-12-21"%proj, "13. Bremen (5) DTK100": r"%s\Testdaten\dtk100\hb\2021-04-30"%proj, "14. Saarland (2) DOP": r"%s\Testdaten\DOP\sl\2022\2022-09-19"%proj}
neue_Raster_p = dict_pfade[inputStr]
print("Eingangsraster: ", neue_Raster_p)
print(str(Path(neue_Raster_p).parents[2])[-3:])

SkriptOptionen = ["ohne Vektorisierung", "Original mit Vektorisierung", "tileindex() statt polygonize()", "ohne Reduzierung der Fläche", "einzelne Vektorisierung"]

if inputStr[0] == "5" or inputStr[0] == "1" or inputStr[0] == "10":
    skript_option = QInputDialog.getItem(None, r"W:\dtk100\rp\2022-11-24", "Skript:", SkriptOptionen, 0, False)[0]
else:
    SkriptOptionen = ["ohne Vektorisierung", "Original mit Vektorisierung", "tileindex() statt polygonize()","einzelne Vektorisierung"]
    skript_option = QInputDialog.getItem(None, r"W:\dtk100\rp\2022-11-24", "Skript:", SkriptOptionen, 0, False)[0]
layer_optionen = ["nur Farblayer", "Farblayer und weiß", "alle Layer"]
layer_auswahl = QInputDialog.getItem(None, r"W:\dtk100\rp\2022-11-24", "Skript:", layer_optionen, 0, False)[0]

bundesland = str(Path(neue_Raster_p).parents[0])[-2:].upper()

utm = "_32"                                                                    # Maßstab und UTM-Zone aus Pfad holen
if bundesland in ["BE", "BB", "MV", "SN"]:
    utm = "_33"

massstab = str(Path(neue_Raster_p).parents[1])[-2:]
if massstab == "00":
    massstab = "100"

layer_dict = {"nur Farblayer": ['col'], "Farblayer und weiß":['col',"weis"], "alle Layer":['col', "weis", "wies", "haus", "brac", 'baum','hrot','baum', 'grau', 'babl', 'grbr', 'heid', 'hrot', 'mrot', 'park', 'rebr','schw', 'sebl', 'stge', 'stor', 'swtx', 'trup', 'utmg', 'viol', 'wald', 'watt', 'weis', 'wies']}
layer = layer_dict[layer_auswahl]

if str(Path(neue_Raster_p).parents[2])[-3:] == "DOP":
    layer = ["DOP"]
    bundesland = str(Path(neue_Raster_p).parents[1])[-2:].upper()
    massstab ="25"

for dtk_layer in layer:
    if skript_option == "ohne Vektorisierung":
        if dtk_layer == "col" or dtk_layer == "DOP":
            dtk_nummern = aktualisiere_Vertr_v.aktualisiere_Vertriebskacheln(neue_Raster_p, bundesland, massstab, utm, dtk_layer, '', proj)
        else:
            aktualisiere_Vertr_v.aktualisiere_Vertriebskacheln(neue_Raster_p, bundesland, massstab, utm, dtk_layer, dtk_nummern, proj)
    elif skript_option == "Original mit Vektorisierung":
        if dtk_layer == "col" or dtk_layer == "DOP":
            dtk_nummern = aktualisiere_Vertr.aktualisiere_Vertriebskacheln(neue_Raster_p, bundesland, massstab, utm, dtk_layer, '')
        else:
            aktualisiere_Vertr.aktualisiere_Vertriebskacheln(neue_Raster_p, bundesland, massstab, utm, dtk_layer, dtk_nummern)
    elif skript_option == "tileindex() statt polygonize()":
        if dtk_layer == "col" or dtk_layer == "DOP":
            dtk_nummern = aktualisiere_Vertr_t.aktualisiere_Vertriebskacheln(neue_Raster_p, bundesland, massstab, utm, dtk_layer, '')
        else:
            aktualisiere_Vertr_t.aktualisiere_Vertriebskacheln(neue_Raster_p, bundesland, massstab, utm, dtk_layer, dtk_nummern)
    elif skript_option == "ohne Reduzierung der Fläche":
        if dtk_layer == "col" or dtk_layer == "DOP":
            dtk_nummern = aktualisiere_Vertr_o.aktualisiere_Vertriebskacheln(neue_Raster_p, bundesland, massstab, utm, dtk_layer, '')
        else:
            aktualisiere_Vertr_o.aktualisiere_Vertriebskacheln(neue_Raster_p, bundesland, massstab, utm, dtk_layer, dtk_nummern)
    elif skript_option == "einzelne Vektorisierung":
        if dtk_layer == "col" or dtk_layer == "DOP":
            dtk_nummern = aktualisiere_Vertr_e.aktualisiere_Vertriebskacheln(neue_Raster_p, bundesland, massstab, utm, dtk_layer, '')
        else:
            aktualisiere_Vertr_e.aktualisiere_Vertriebskacheln(neue_Raster_p, bundesland, massstab, utm, dtk_layer, dtk_nummern)

b = datetime.now()

print("Zeit: ", b-a)

names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
for i in names:
    layer = QgsProject.instance().mapLayersByName(i)[0]
    QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityCheckedParentRecursive(False)
