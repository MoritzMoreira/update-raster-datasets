import arcpy

def clip_D(layer, kachel_liste):
    arcpy.AddMessage(layer)
    for dtk_nummer in kachel_liste:
        dtk_nummer_str = str(dtk_nummer)[1:-2]
        arcpy.management.SelectLayerByAttribute("vertriebskacheln_lyr", 'NEW_SELECTION', f"id LIKE {dtk_nummer_str}")

        if arcpy.Exists(f"{arcpy.env.workspace}\{layer}_{dtk_nummer_str[1:-1]}"):
            pass
        else:
            arcpy.env.pyramid = "NONE"
            arcpy.env.compression = "NONE"
            arcpy.env.rasterStatistics = "NONE"
            arcpy.management.Clip("%s\D_%s"%(arcpy.env.workspace, layer), "#", f"{arcpy.env.workspace}/{layer}_{dtk_nummer_str[1:-1]}", "vertriebskacheln_lyr", "#", "ClippingGeometry", "NO_MAINTAIN_EXTENT")
            if layer == "col":
                arcpy.management.AddColormap(f"{arcpy.env.workspace}/col_{dtk_nummer_str[1:-1]}", "#", r"M:\DTK-N-Repository\Ressourcen\Colormaps\DTK-N_PQS1.0.clr")
    pass