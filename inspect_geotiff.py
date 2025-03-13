#!/usr/bin/env python3

import os
import sys
from osgeo import gdal

def inspect_tiff(tif_path):
    """
    Imprime metadatos clave de un GeoTIFF:
      - Tamaño en disco
      - Dimensiones en píxeles (width, height)
      - Proyección y GeoTransform
      - Metadatos a nivel dataset
      - Metadatos en IMAGE_STRUCTURE (compresión, interleave, etc.)
      - Para cada banda:
          * Tipo de dato
          * Tamaño de bloque (BlockSize)
          * Scale/Offset
          * Nodata
          * Estadísticas (min, max, mean, std)
          * Metadata de la banda
    """
    if not os.path.isfile(tif_path):
        print(f"No existe el archivo: {tif_path}")
        return

    ds = gdal.Open(tif_path)
    if not ds:
        print(f"No se pudo abrir {tif_path}")
        return

    print(f"\n=== Información para: {tif_path} ===")

    # Tamaño en disco
    size_bytes = os.path.getsize(tif_path)
    print(f"  → Tamaño en disco: {size_bytes} bytes (~ {size_bytes/1024/1024:.2f} MB)")

    # Dimensiones y proyección
    width = ds.RasterXSize
    height = ds.RasterYSize
    proj = ds.GetProjection()
    gt = ds.GetGeoTransform()
    print(f"  → Dimensiones: {width} x {height} (cols x rows)")
    print(f"  → Proyección (WKT parcial): {proj[:80]}...")
    print(f"  → GeoTransform: {gt}")

    # Metadata a nivel dataset
    md_ds = ds.GetMetadata()
    print(f"  → Metadata dataset: {md_ds}")

    # IMAGE_STRUCTURE para ver compresión, interleave, etc.
    md_img = ds.GetMetadata("IMAGE_STRUCTURE")
    print(f"  → IMAGE_STRUCTURE: {md_img}")

    # Revisar cada banda
    for i in range(1, ds.RasterCount + 1):
        band = ds.GetRasterBand(i)
        dt = band.DataType
        dt_name = gdal.GetDataTypeName(dt)

        # Bloques
        bx, by = band.GetBlockSize()

        # Scale/offset
        scale = band.GetScale()
        offset = band.GetOffset()

        # Nodata
        nodata = band.GetNoDataValue()

        # Estadísticas (Min, Max, Mean, Std). Esto puede tardar si no existen y se calculan.
        stats = band.GetStatistics(True, True)  # (approx_ok=True, force=True)

        # Metadatos de banda
        band_md = band.GetMetadata()

        print(f"\n  → Banda {i}:")
        print(f"      Tipo de dato: {dt_name}")
        print(f"      BlockSize: {bx} x {by}")
        print(f"      Scale/Offset: {scale} / {offset}")
        print(f"      NoData Value: {nodata}")
        if stats:
            print(f"      Stats (Min,Max,Mean,Std): {stats}")
        print(f"      Metadata banda: {band_md}")

    ds = None  # Cerrar para liberar recursos

if __name__ == "__main__":
    # Rutas de ejemplo para los 2 archivos que deseas comparar
    # Ajusta si difieren en tu sistema.
    tif1 = "/home/contreras/Documents/GitHub/download_20m/crop/CHELSA_ai_1981-2010_V.2.1.tif"
    tif2 = "/home/contreras/Documents/GitHub/download_20m/bio/crops/CHELSA_ai_1981-2010_V.2.1.tif"

    # Llamamos a la función de inspección para cada archivo
    inspect_tiff(tif1)
    inspect_tiff(tif2)
