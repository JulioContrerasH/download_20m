import glob
import math
from pathlib import Path
from osgeo import gdal

def world2pixel(gt, x, y):
    """Convierte coordenada (x, y) en píxeles según el GeoTransform gt."""
    x0, dx, rx, y0, ry, dy = gt
    col = (x - x0) / dx
    row = (y - y0) / dy
    return col, row

def warp_to_tiff(input_tif, output_tif, extent):
    """
    Recorta 'input_tif' a la extensión 'extent' y lo guarda como TIFF con bloques 1024x1024 y interleave PIXEL en 'output_tif'.
    No se aplica re-muestreo (interpolación), solo un corte exacto y alineado.
    """
    # Abrir el dataset de entrada
    ds = gdal.Open(input_tif)
    if not ds:
        raise RuntimeError(f"No se pudo abrir {input_tif}")
    gt = ds.GetGeoTransform()
    x_size = ds.RasterXSize
    y_size = ds.RasterYSize
    
    # Convertir la extensión de coordenadas geográficas a píxeles (sin redondeo excesivo)
    px_tl, py_tl = world2pixel(gt, extent[0], extent[3])  # top-left
    px_br, py_br = world2pixel(gt, extent[2], extent[1])  # bottom-right
    
    # Asegurarse de que el corte esté bien alineado con los píxeles del raster
    xoff = int(round(px_tl))
    yoff = int(round(py_tl))
    xend = int(round(px_br))
    yend = int(round(py_br))
    xsize = xend - xoff
    ysize = yend - yoff
    
    # Ajuste por si se sale de los límites del raster
    if xoff < 0:
        xsize += xoff
        xoff = 0
    if yoff < 0:
        ysize += yoff
        yoff = 0
    if xoff + xsize > x_size:
        xsize = x_size - xoff
    if yoff + ysize > y_size:
        ysize = y_size - yoff
    if xsize <= 0 or ysize <= 0:
        raise RuntimeError("La ventana de corte (srcWin) es inválida o está fuera de rango.")
    
    # Usar gdal.Translate para recortar el raster y guardar como TIFF con bloques 1024x1024 y interleave PIXEL
    translate_opts = gdal.TranslateOptions(
        srcWin=[xoff, yoff, xsize, ysize],  # Especifica la ventana de subraste
        format="GTiff",  # Formato TIFF estándar (no COG)
        creationOptions=[
            "COMPRESS=DEFLATE",  # Compresión
            "BIGTIFF=YES",       # Si el archivo es grande
            "TILED=YES",         # Crear en formato tiled
            "BLOCKXSIZE=1024",   # Tamaño del bloque en X (1024 píxeles)
            "BLOCKYSIZE=1024",   # Tamaño del bloque en Y (1024 píxeles)
            "INTERLEAVE=PIXEL",  # Interleave en formato PIXEL
        ],
    )
    
    # Especifica el sistema de referencia espacial al llamar a gdal.Translate
    gdal.Translate(str(output_tif), input_tif, options=translate_opts, dstSRS="EPSG:4326")


# 1) Leer el bounding box de 'elevation.tif'
elev_path = "elevation.tif"
ds_elev = gdal.Open(elev_path)
if not ds_elev:
    raise RuntimeError(f"No se pudo abrir {elev_path}")

# Obtener geotransform [x0, dx, 0, y0, 0, dy]
gt = ds_elev.GetGeoTransform()
x0, dx, _, y0, _, dy = gt

x_size = ds_elev.RasterXSize
y_size = ds_elev.RasterYSize

# Calcular x_max, y_max
x_max = x0 + dx * x_size
y_max = y0 + dy * y_size

# Para outputBounds en GDAL: [xmin, ymin, xmax, ymax]
if dy < 0:
    # y0 es top, y_max es bottom
    extent = [x0, y_max, x_max, y0]
else:
    # y0 es bottom, y_max es top
    extent = [x0, y0, x_max, y_max]

ds_elev = None  # Cerrar el dataset de elevation

# 2) Crear carpeta de salida
out_dir = Path("bio/tiff")
out_dir.mkdir(parents=True, exist_ok=True)

# 3) Iterar sobre cada TIFF en "bio/images"
for tif_path in glob.glob("bio/*.tif"):
    if tif_path.endswith("elevation.tif"):
        # Saltamos el propio elevation.tif
        continue
    
    base_name = Path(tif_path).stem  # nombre sin extensión
    out_path = out_dir / f"{base_name}.tif"
    
    print(f"Procesando: {tif_path} -> {out_path}")
    warp_to_tiff(tif_path, out_path, extent)

print("¡Listo! Se generaron los TIFF con bloques 1024x1024 y interleave PIXEL en la carpeta bio/tiff/.")
