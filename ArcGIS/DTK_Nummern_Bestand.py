import arcpy

def ermittle_dtkNum(massstab, bundesland, datum):
    arcpy.management.SelectLayerByLocation("vertriebskacheln_lyr", "INTERSECT",
                                           f"D:\Praktikanten\Hackenberg_Moritz\DTK-Workflow-test\Services_test\dtk%s_%s_%s.gdb\source_footprints"%(massstab, bundesland, datum), "-10")
    #  arcpy.management.SelectLayerByLocation("vertriebskacheln_lyr", "INTERSECT", f"D:\Praktikanten\Hackenberg_Moritz\DTK-Workflow-test\Services_test\dtk%s_%s_%s.gdb\source_footprints" % (massstab, bundesland, datum), "0")
    kachel_liste = arcpy.da.TableToNumPyArray("vertriebskacheln_lyr", "id")
    kachel_str = ""
    for dtk_nummer in kachel_liste:
        kachel_str += str(dtk_nummer)[1:-1]

    return kachel_str[:-1], kachel_liste