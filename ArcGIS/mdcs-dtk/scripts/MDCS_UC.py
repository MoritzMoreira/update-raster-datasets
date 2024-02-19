# ------------------------------------------------------------------------------
# Name: MDCS_UC.py
# Description: A class to implement all user functions or to extend the built in MDCS functions/commands chain.
# Version: 20220228
# Requirements: ArcGIS 10.1 SP1
# Author: Esri Imagery Workflows team / Mario Hohensee(BKG)
# ------------------------------------------------------------------------------
#!/usr/bin/env python
import os
import sys
import arcpy
from datetime import datetime as dt


class UserCode:

    def __init__(self, data):
        pass    # initialize variables that need to be shared between multiple user commands.

    def ClipFootprints(self, data):
        """clip footprints with specified AOI and reimport footprint shape
        """
        base = data['base']
        base_workspace = data['workspace']  # base.m_geoPath
        md = data['mosaicdataset']
        log = data['log']
        xmlDOM = data['mdcs']
        ds = os.path.join(base_workspace, md)
        node = base.getXMLNode(xmlDOM, 'ClipFootprints')
        in_feature_class = os.path.normpath(base.getXMLNodeValue(node, 'in_feature_class'))
        where = base.getXMLNodeValue(node, 'where_clause')
        out_feature_class = os.path.normpath(base.getXMLNodeValue(node, 'out_feature_class'))

        # log.Message("Clipping Footprints", base.const_general_text)

        # testing output workspace
        out_wksp, out_f = os.path.split(out_feature_class)
        if not out_wksp:
            # used FeatureClass Name without Database --> assuming that FeatureClass should be created in base.m_geoPath
            out_wksp = base.m_geoPath
        if not arcpy.Exists(out_wksp):
            log.Message("\tCreating Footprint Database: {}".format(out_wksp), base.const_general_text)
            out_wksp_parent_dir, out_wksp_name = os.path.split(out_wksp)
            try:
                arcpy.CreateFileGDB_management(out_wksp_parent_dir, out_wksp_name)
            except arcpy.ExecuteError as e:
                log.Message(arcpy.GetMessages(), base.const_critical_text)
                return False
            except Exception as e:
                log.Message(str(e), base.const_critical_text)
                return False

        fullpath = os.path.join(out_wksp, out_f)

        # make layer
        md_lyr = "mdlyr_{}_{}".format(md, dt.strftime(dt.now(), "%Y%m%d%H%M%S"))
        arcpy.MakeMosaicLayer_management(ds, md_lyr, "Category = 1")

        in_feature_class_basename = os.path.basename(in_feature_class)
        log.Message("\tSelecting feature from {0} where {1}".format(in_feature_class_basename, where), base.const_general_text)
        clipper_lyr = "clipper_{}".format(dt.strftime(dt.now(), "%Y%m%d%H%M%S"))
        arcpy.MakeFeatureLayer_management(in_feature_class, clipper_lyr, where)

        # test if clipper layer contains at least 1 feature
        item_count = int(arcpy.GetCount_management(clipper_lyr)[0])
        if item_count == 0:
            log.Message("No features selected. Nothing to clip.", base.const_warning_text)
            return True

        # clip footprints to polygon
        footprint_sub_layer = md_lyr + "/Footprint"
        log.Message("\tClip footprints", base.const_general_text)
        try:
            arcpy.analysis.Clip(footprint_sub_layer, clipper_lyr, fullpath)
        except arcpy.ExecuteError as e:
            log.Message(arcpy.GetMessages(), base.const_warning_text)
        except Exception as e:
            log.Message(str(e), base.const_critical_text)
            return False
        log.Message("\t\tCreated clipped footprint geometry: {}.".format(fullpath), base.const_general_text)

        # import footprints to mosaic
        log.Message("\tImport clipped footprint geometry", base.const_general_text)
        try:
            arcpy.ImportMosaicDatasetGeometry_management(md_lyr, 'FOOTPRINT', "Name", fullpath, "Name")
        except arcpy.ExecuteError as e:
            log.Message(arcpy.GetMessages(), base.const_critical_text)
            return False
        except Exception as e:
            log.Message(str(e), base.const_critical_text)
            return False

        arcpy.Delete_management([md_lyr, clipper_lyr])
        del md_lyr
        del clipper_lyr
        return True

    def RemoveRastersOutside(self, data):
        """remove raster items outside a given AOI
        """
        base = data['base']
        base_workspace = data['workspace']   # base.m_geoPath
        md = data['mosaicdataset']
        log = data['log']
        xmlDOM = data['mdcs']
        ds = os.path.join(base_workspace, md)
        node = base.getXMLNode(xmlDOM, 'RemoveRastersOutside')
        in_feature_class = base.getXMLNodeValue(node, 'in_feature_class')
        where = base.getXMLNodeValue(node, 'where_clause')

        # make layer
        md_lyr = "mdlyr_{}_{}".format(md, dt.strftime(dt.now(), "%Y%m%d%H%M%S"))
        # log.Message("DS: %s \t MD: %s \t MD Layer: %s" % (ds, md, md_lyr), base.const_general_text)
        mlyr = arcpy.MakeMosaicLayer_management(ds, md_lyr) #, "Category = 1")
        footprint_sub_layer = md_lyr + "/Footprint"

        feature_lyr = "fclyr_{}".format(dt.strftime(dt.now(), "%Y%m%d%H%M%S"))
        # log.Message("infc: %s \t flyr: %s \t where: %s" % (in_feature_class, feature_lyr, where), base.const_general_text)
        arcpy.MakeFeatureLayer_management(in_feature_class, feature_lyr, where)

        # arcpy.SelectLayerByAttribute_management(md_lyr, selection_type="CLEAR_SELECTION")
        sel = arcpy.SelectLayerByLocation_management(in_layer=md_lyr,  # footprint_sub_layer,
                                                     overlap_type='ARE_IDENTICAL_TO',
                                                     select_features=feature_lyr,
                                                     search_distance=None,
                                                     selection_type='NEW_SELECTION',
                                                     invert_spatial_relationship='INVERT')
        sel_count = int(sel[2])
        lyr_count = int(arcpy.GetCount_management(footprint_sub_layer)[0])
        log.Message("\tItems selected: {}".format(sel_count), base.const_general_text)
        try:
            if sel_count > 0 and sel_count == lyr_count:
                # if 0 or all items are selected, non will be removed
                arcpy.RemoveRastersFromMosaicDataset_management(md_lyr)
                log.Message(arcpy.GetMessages(), base.const_general_text)

        except arcpy.ExecuteError as e:
            log.Message(arcpy.GetMessages(), base.const_critical_text)
            return False
        except Exception as e:
            log.Message(str(e), base.const_critical_text)
            return False

        arcpy.Delete_management([md_lyr, feature_lyr])
        del md_lyr
        del feature_lyr

        return True
