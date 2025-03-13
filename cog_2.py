import glob
import os
from pathlib import Path
from osgeo import gdal

def warp_without_unscale(input_tif, tmp_tif, extent, x_res, y_res, proj):
    """
    1) Warp sin 'unscale':
       Recorta 'input_tif' a la extensión 'extent' (xmin, ymin, xmax, ymax),
       usando la misma resolución que 'elevation.tif' (x_res, y_res) y proyección 'proj'.
       Se utiliza 'nearest neighbor' sin aplicar factor de escala ni offset.
    """
    warp_options = gdal.WarpOptions(
        format="GTiff",
        outputBounds=extent,
        xRes=x_res,
        yRes=y_res,
        targetAlignedPixels=True,
        resampleAlg="near",
        dstSRS=proj,
        creationOptions=[
            "COMPRESS=DEFLATE",
            "BIGTIFF=YES"
        ]
        # No usamos 'unscale=True' porque tu GDAL no lo soporta
    )

    gdal.Warp(
        destNameOrDestDS=str(tmp_tif),
        srcDSOrSrcDSTab=str(input_tif),
        options=warp_options
    )

def apply_scale_offset(in_tif, out_tif):
    """
    2) Aplica manualmente la escala/offset (si existen) de la banda 1.
       - Lee 'scale' y 'offset' de la banda 1 del in_tif.
       - Crea un nuevo TIFF con los valores ya desescalados en float32.
    """
    ds = gdal.Open(str(in_tif), gdal.GA_ReadOnly)
    band = ds.GetRasterBand(1)

    # Tomar los metadatos de escala/offset si existen
    scale = band.GetScale()   # Puede ser None si no existe
    offset = band.GetOffset() # Puede ser None si no existe

    # Leemos el array como float para poder hacer la operación
    arr = band.ReadAsArray().astype("float32")

    # Si no hay scale/offset definidos, usar scale=1, offset=0
    if scale is None:
        scale = 1.0
    if offset is None:
        offset = 0.0

    # Aplicamos manualmente: valor_real = valor_bruto * scale + offset
    arr = arr * scale + offset

    # Crear el TIFF de salida con float32
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(
        str(out_tif),
        ds.RasterXSize,
        ds.RasterYSize,
        1,
        gdal.GDT_Float32,
        options=["COMPRESS=DEFLATE","BIGTIFF=YES"]
    )
    # Copiar info espacial
    out_ds.SetGeoTransform(ds.GetGeoTransform())
    out_ds.SetProjection(ds.GetProjection())

    # Escribimos el array con valores ya desescalados
    out_ds.GetRasterBand(1).WriteArray(arr)

    # Cerrar
    out_ds = None
    ds = None

def warp_to_tiff(input_tif, output_tif, extent, x_res, y_res, proj):
    """
    Función principal de recorte:
    - Hace el warp sin unscale (archivo temporal)
    - Aplica la escala manual y crea 'output_tif' final con valores reales
    - Borra el temporal
    """
    tmp_tif = str(output_tif) + ".tmpwarp.tif"

    # 1) Warp sin unscale
    warp_without_unscale(input_tif, tmp_tif, extent, x_res, y_res, proj)

    # 2) Aplica scale/offset manualmente
    apply_scale_offset(tmp_tif, output_tif)

    # 3) Borramos el temporal
    if os.path.exists(tmp_tif):
        os.remove(tmp_tif)

def merge_bands_to_tiff(input_tifs, output_tif):
    """
    Fusiona múltiples TIFFs (ya con valores "reales") en un solo multibanda.
    - No hacemos unscale aquí: asumimos que ya está aplicado en warp_to_tiff.
    - Cada banda se nombra según el nombre del archivo (sin extensión).
    """
    datasets = [gdal.Open(str(tif)) for tif in input_tifs]
    if not datasets:
        raise RuntimeError("No hay datasets de entrada para fusionar.")
    
    # Info espacial del primero
    x_size = datasets[0].RasterXSize
    y_size = datasets[0].RasterYSize
    geotrans = datasets[0].GetGeoTransform()
    proj = datasets[0].GetProjection()

    # Tipo de la primera banda
    first_band = datasets[0].GetRasterBand(1)
    band_type = first_band.DataType

    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(
        str(output_tif),
        x_size,
        y_size,
        len(datasets),
        band_type,
        options=[
            "COMPRESS=DEFLATE",
            "BIGTIFF=YES",
            "TILED=YES",
            "BLOCKXSIZE=1024",
            "BLOCKYSIZE=1024",
            "INTERLEAVE=PIXEL"
        ]
    )
    out_ds.SetGeoTransform(geotrans)
    out_ds.SetProjection(proj)

    # Copiamos cada banda
    for i, ds_in in enumerate(datasets):
        arr = ds_in.GetRasterBand(1).ReadAsArray()
        out_band = out_ds.GetRasterBand(i+1)
        out_band.WriteArray(arr)

        # Nombre de la banda = nombre del archivo de entrada
        band_name = Path(input_tifs[i]).stem
        out_band.SetDescription(band_name)

    # Cerrar
    for ds_in in datasets:
        ds_in = None
    out_ds = None

# ----------------------------------------------------------------------
#                  LÓGICA PRINCIPAL (sin unscale=True)
# ----------------------------------------------------------------------

# 1) Leer bounding box y resolución de 'elevation.tif'
elev_path = "elevation.tif"
ds_elev = gdal.Open(str(elev_path))
if not ds_elev:
    raise RuntimeError(f"No se pudo abrir {elev_path}")

gt = ds_elev.GetGeoTransform()
x0, dx, _, y0, _, dy = gt
x_size = ds_elev.RasterXSize
y_size = ds_elev.RasterYSize
proj_elev = ds_elev.GetProjection()

x_max = x0 + dx * x_size
y_max = y0 + dy * y_size

if dy < 0:
    extent = [x0, y_max, x_max, y0]
else:
    extent = [x0, y0, x_max, y_max]

x_res = abs(dx)
y_res = abs(dy)
ds_elev = None

# 2) Crear carpeta de salida
out_dir = Path("bio/tiff2/try/crops")
out_dir.mkdir(parents=True, exist_ok=True)

# 3) Recortar cada TIFF en "bio/tiff2/try", aplicando scale manual, excepto "elevation.tif"
tif_files = glob.glob("bio/*.tif")
recortados = []

for tif_path in tif_files:
    if Path(tif_path).name == "elevation.tif":
        continue  # Omitir elevación si está

    base_name = Path(tif_path).stem
    out_path = out_dir / f"{base_name}.tif"
    print(f"Recortando y desescalando: {tif_path} -> {out_path}")
    warp_to_tiff(
        input_tif=tif_path,
        output_tif=out_path,
        extent=extent,
        x_res=x_res,
        y_res=y_res,
        proj=proj_elev
    )
    recortados.append(out_path)

# 4) Fusionar en un multibanda (ya no hay unscale)
if recortados:
    output_tif = out_dir / "merged_output.tif"
    print(f"Creando multibanda: {output_tif}")
    merge_bands_to_tiff(recortados, output_tif)
    print(f"TIFF final multibanda guardado en: {output_tif}")
else:
    print("No se encontraron TIFFs para fusionar (aparte de 'elevation.tif').")





##########3


import glob
import os
from pathlib import Path
from osgeo import gdal

def partial_merge_bands_to_tiff(input_tifs, output_tif, block_size=1024):
    """
    Fusiona múltiples TIFF (todas del mismo tamaño/proyección) en un solo multibanda,
    leyendo y escribiendo por bloques para no cargar todo en memoria.

    - Usa compresión DEFLATE + PREDICTOR=3 (adecuado para flotantes).
    - TILED=YES, BLOCKXSIZE=1024, BLOCKYSIZE=1024, INTERLEAVE=PIXEL.
    - Emplea argumentos posicionales en ReadAsArray(col, row, cols_to_read, rows_to_read).
    """

    # Abrimos todos los TIFF de entrada en modo lectura
    datasets = [gdal.Open(str(tif), gdal.GA_ReadOnly) for tif in input_tifs]
    if not datasets:
        raise RuntimeError("No hay TIFFs de entrada para fusionar.")

    # Parámetros espaciales (tomados del primero)
    x_size = datasets[0].RasterXSize
    y_size = datasets[0].RasterYSize
    geotrans = datasets[0].GetGeoTransform()
    proj = datasets[0].GetProjection()

    # Tipo de dato de la primera banda
    first_band = datasets[0].GetRasterBand(1)
    band_type = first_band.DataType  # p.e. gdal.GDT_Float32

    # Creamos el archivo de salida con tantas bandas como TIFFs
    driver = gdal.GetDriverByName("GTiff")
    out_ds = driver.Create(
        str(output_tif),
        x_size,
        y_size,
        len(datasets),
        band_type,
        options=[
            "COMPRESS=DEFLATE",
            "PREDICTOR=3",   # 3 para float, 2 si tus datos son enteros
            "TILED=YES",
            "BLOCKXSIZE=1024",
            "BLOCKYSIZE=1024",
            "INTERLEAVE=PIXEL",
            # "ZLEVEL=9",    # Si quieres compresión Deflate máxima, descoméntalo
            "BIGTIFF=YES"
        ],
    )
    out_ds.SetGeoTransform(geotrans)
    out_ds.SetProjection(proj)

    # Para cada TIFF de entrada, copiamos su banda 1 como banda i+1 del multibanda
    for i, ds_in in enumerate(datasets):
        in_band = ds_in.GetRasterBand(1)
        out_band = out_ds.GetRasterBand(i + 1)

        # Nombre de la banda = nombre del archivo sin extensión
        band_name = Path(input_tifs[i]).stem
        out_band.SetDescription(band_name)

        # Leer/escribir en bloques (posicionales en vez de xoff=,yoff=,...)
        for row in range(0, y_size, block_size):
            rows_to_read = min(block_size, y_size - row)
            for col in range(0, x_size, block_size):
                cols_to_read = min(block_size, x_size - col)

                # Leer un bloque del TIFF de entrada (posicional)
                data_block = in_band.ReadAsArray(col, row, cols_to_read, rows_to_read)
                # Escribir el bloque
                out_band.WriteArray(data_block, col, row)

    # Cerrar todo
    out_ds = None
    for ds_in in datasets:
        ds_in = None


# ------------------- LÓGICA PRINCIPAL -------------------
# 1) Carpeta donde ya tienes todos los TIFF recortados:
crops_dir = Path("/home/contreras/Documents/GitHub/download_20m/bio/tiff2/try/crops")

# 2) Buscamos los .tif en esa carpeta
tif_files = sorted(glob.glob(str(crops_dir / "*.tif")))

# 3) Evitar mezclar un TIFF de salida anterior si existe
input_tifs = [t for t in tif_files if not t.endswith("merged_output3.tif")]

# 4) Ejecutar la fusión
if not input_tifs:
    print("No se encontraron TIFFs de entrada para fusionar.")
else:
    output_tif = crops_dir / "merged_output2.tif"
    print(f"Creando multibanda: {output_tif}")
    partial_merge_bands_to_tiff(input_tifs, output_tif, block_size=1024)
    print(f"¡Listo! Multibanda guardado en: {output_tif}")
