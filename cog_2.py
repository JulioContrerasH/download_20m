import glob
from pathlib import Path
from osgeo import gdal

def warp_to_tiff(
    input_tif, 
    output_tif, 
    extent, 
    x_res, 
    y_res, 
    proj
):
    """
    Recorta 'input_tif' a la extensión 'extent' (xmin, ymin, xmax, ymax),
    con la misma resolución que 'elevation.tif' (x_res, y_res) y misma proyección.
    Se usa nearest neighbor para no interpolar valores.
    
    - Para una sola banda no hace falta especificar "INTERLEAVE=PIXEL"
      ni bloques de 1024 (que son más relevantes en un producto final multibanda).
    - Se usa compresión DEFLATE y BIGTIFF por si el archivo crece bastante.
    """
    gdal.Warp(
        str(output_tif),
        str(input_tif),
        format="GTiff",
        outputBounds=extent,
        xRes=x_res,
        yRes=y_res,
        targetAlignedPixels=True,
        resampleAlg="near",
        dstSRS=proj,  # Misma proyección que elevation
        creationOptions=[
            "COMPRESS=DEFLATE",
            "BIGTIFF=YES"
        ]
    )

def merge_bands_to_tiff(
    input_tifs, 
    output_tif
):
    """
    Fusiona múltiples TIFFs (todas del mismo tamaño/proyección) en un solo archivo 
    multibanda (Interleave=PIXEL).
    
    - Cada banda se nombra según el stem (nombre de archivo sin extensión) del TIFF original.
    - Se crea con compresión DEFLATE y bloques de 1024 (útil si el archivo final es grande).
    """
    # Abrimos todos los TIFF
    datasets = [gdal.Open(str(tif)) for tif in input_tifs]
    if not datasets:
        raise RuntimeError("No hay datasets de entrada para fusionar.")
    
    # Tomamos info espacial del primero
    x_size = datasets[0].RasterXSize
    y_size = datasets[0].RasterYSize
    geotrans = datasets[0].GetGeoTransform()
    proj = datasets[0].GetProjection()

    # Creamos salida con tantas bandas como datasets
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(
        str(output_tif),
        x_size,
        y_size,
        len(datasets),
        options=[
            "COMPRESS=DEFLATE",
            "BIGTIFF=YES",
            "TILED=YES",
            "BLOCKXSIZE=1024",
            "BLOCKYSIZE=1024",
            "INTERLEAVE=PIXEL"
        ]
    )

    # Asignamos la info espacial
    out_ds.SetGeoTransform(geotrans)
    out_ds.SetProjection(proj)

    # Copiamos cada banda y le ponemos de descripción el nombre del archivo
    for i, ds in enumerate(datasets):
        data = ds.GetRasterBand(1).ReadAsArray() 
        out_band = out_ds.GetRasterBand(i+1)
        out_band.WriteArray(data)

        # Nombre de la banda = nombre del archivo de entrada (sin extensión)
        band_name = Path(input_tifs[i]).stem
        out_band.SetDescription(band_name)

    # Cerramos todo
    for ds in datasets:
        ds = None
    out_ds = None

# ------------------------------------------------------
#  Lógica principal (sin usar "def main()")
# ------------------------------------------------------

# 1) Leer info de elevation.tif
elev_path = "elevation.tif"
ds_elev = gdal.Open(str(elev_path))
if not ds_elev:
    raise RuntimeError(f"No se pudo abrir {elev_path}")

gt = ds_elev.GetGeoTransform()  # (x0, dx, _, y0, _, dy)
x0, dx, _, y0, _, dy = gt
x_size = ds_elev.RasterXSize
y_size = ds_elev.RasterYSize
proj_elev = ds_elev.GetProjection()

# Calcular bounding box
x_max = x0 + dx * x_size
y_max = y0 + dy * y_size

# outputBounds = [xmin, ymin, xmax, ymax]
if dy < 0:
    extent = [x0, y_max, x_max, y0]
else:
    extent = [x0, y0, x_max, y_max]

# Resolución (valores absolutos)
x_res = abs(dx)
y_res = abs(dy)
ds_elev = None

# 2) Crear carpeta de salida
out_dir = Path("bio/tiff2/try/crops")
out_dir.mkdir(parents=True, exist_ok=True)

# 3) Recortar cada TIFF en "bio/tiff2/try" (excepto "elevation.tif")
tif_files = glob.glob("bio/tiff2/try/*.tif")
recortados = []

for tif_path in tif_files:
    if Path(tif_path).name == "elevation.tif":
        # Omitimos el propio elevation
        continue

    base_name = Path(tif_path).stem
    out_path = out_dir / f"{base_name}.tif"
    print(f"Recortando: {tif_path} -> {out_path}")

    warp_to_tiff(
        input_tif=tif_path,
        output_tif=out_path,
        extent=extent,
        x_res=x_res,
        y_res=y_res,
        proj=proj_elev
    )
    recortados.append(out_path)

# 4) Fusionar en un multibanda
if recortados:
    output_tif = out_dir / "merged_output.tif"
    print(f"Creando multibanda: {output_tif}")
    merge_bands_to_tiff(recortados, output_tif, dtype=gdal.GDT_Float32)
    print(f"TIFF final multibanda guardado en: {output_tif}")
else:
    print("No se encontraron TIFFs (aparte de 'elevation.tif') para fusionar.")


