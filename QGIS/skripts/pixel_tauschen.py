import processing

def tausche_pix(dtk_nr, layer, pfad, proj):
    pfad_neu = r"%s\Zwischenschritte\Raster\neu\%s_%s.tif"%(proj, dtk_nr, layer)

    # Formel Ausdruck "A==0": logischer Test. Das Ergebnis (1 wahr, 0 falsch) ist der neue Pixelwert. Also 1 für 0 und 0 für 1
    processing.run("gdal:rastercalculator", {'INPUT_A': pfad, 'BAND_A': 1, 'FORMULA': '(A==0)', 'RTYPE': 0, 'NO_DATA': 1, 'OUTPUT': pfad_neu})
    pfad = pfad_neu

    return pfad