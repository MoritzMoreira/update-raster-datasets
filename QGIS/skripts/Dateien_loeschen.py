import os

def loesche_dat(dtk_nr, layer, proj):
    if os.path.exists(r'%s/Zwischenschritte/Raster/neu/neu_%s_%s.vrt' % (proj, dtk_nr, layer)):
        os.remove(r'%s/Zwischenschritte/Raster/neu/neu_%s_%s.vrt' % (proj, dtk_nr, layer))
    if os.path.exists(r'%s/Zwischenschritte/Raster/neu/neue_kbClip_%s.vrt' % (proj, layer)):
        os.remove(r'%s/Zwischenschritte/Raster/neu/neue_kbClip_%s.vrt' % (proj, layer))
    if os.path.exists(r'%s/Zwischenschritte/Raster/neu/r_neu_%s_%s.vrt' % (proj, dtk_nr, layer)):
        os.remove(r'%s/Zwischenschritte/Raster/neu/r_neu_%s_%s.vrt' % (proj, dtk_nr, layer))
    pass