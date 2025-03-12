from osgeo import gdal
import math
from pathlib import Path

# ========== 1) ABRIR elevation.tif Y LEER EXTENSIÓN ==========
elev_path = "elevation.tif"
elev_ds = gdal.Open(elev_path)
if not elev_ds:
    raise RuntimeError(f"No se pudo abrir {elev_path}")

elev_gt = elev_ds.GetGeoTransform()
elev_nx = elev_ds.RasterXSize
elev_ny = elev_ds.RasterYSize

# Calcular la extensión en coordenadas (xmin, xmax, ymin, ymax)
# teniendo en cuenta si dy es negativo
ex0 = elev_gt[0]                    # x de la esquina sup. izq.
ex1 = ex0 + elev_gt[1] * elev_nx    # x de la esquina sup. der.
ey0 = elev_gt[3]                    # y de la esquina sup. izq.
ey1 = ey0 + elev_gt[5] * elev_ny    # y de la esquina inf. izq. (si dy<0)

elev_xmin = min(ex0, ex1)
elev_xmax = max(ex0, ex1)
elev_ymin = min(ey0, ey1)
elev_ymax = max(ey0, ey1)

elev_ds = None  # cerrar elevation

# ========== 2) ABRIR CHELSA Y LEER SU EXTENSIÓN ==========
chelsa_path = "bio/CHELSA_ai_1981-2010_V.2.1.tif"
chelsa_ds = gdal.Open(chelsa_path)
if not chelsa_ds:
    raise RuntimeError(f"No se pudo abrir {chelsa_path}")

chelsa_gt = chelsa_ds.GetGeoTransform()
chelsa_nx = chelsa_ds.RasterXSize
chelsa_ny = chelsa_ds.RasterYSize

cx0 = chelsa_gt[0]
cx1 = cx0 + chelsa_gt[1] * chelsa_nx
cy0 = chelsa_gt[3]
cy1 = cy0 + chelsa_gt[5] * chelsa_ny

chelsa_xmin = min(cx0, cx1)
chelsa_xmax = max(cx0, cx1)
chelsa_ymin = min(cy0, cy1)
chelsa_ymax = max(cy0, cy1)

# ========== 3) CALCULAR INTERSECCIÓN ENTRE AMBAS EXTENSIONES ==========
ixmin = max(chelsa_xmin, elev_xmin)
ixmax = min(chelsa_xmax, elev_xmax)
iymin = max(chelsa_ymin, elev_ymin)
iymax = min(chelsa_ymax, elev_ymax)

if ixmin >= ixmax or iymin >= iymax:
    raise RuntimeError(
        "No hay superposición entre la extensión de elevation y CHELSA."
    )

# ========== 4) CONVERTIR ESA INTERSECCIÓN A OFFSETS (SUBWIN) EN CHELSA ==========
# Fórmula para pasar de coord. geográfica a píxeles:
#    col = (X - x0)/dx
#    row = (Y - y0)/dy
# Ojo si dy es negativo (típico en north-up), esto se maneja igual con la misma fórmula.

def world2pixel(gt, x, y):
    """Convierte coordenada (x, y) en píxeles según el GeoTransform `gt`."""
    x0, dx, rx, y0, ry, dy = gt
    col = (x - x0) / dx
    row = (y - y0) / dy
    return col, row

# Para la subventana, definimos la esquina sup. izq. en píxeles y la inf. der. en píxeles
px_tl, py_tl = world2pixel(chelsa_gt, ixmin, iymax)  # top-left
px_br, py_br = world2pixel(chelsa_gt, ixmax, iymin)  # bottom-right

# Redondeamos para crear la subventana integral
xoff = int(math.floor(px_tl))
yoff = int(math.floor(py_tl))
xend = int(math.ceil(px_br))
yend = int(math.ceil(py_br))

xsize = xend - xoff
ysize = yend - yoff

# Ajuste por si se sale de los límites del raster
if xoff < 0:
    xsize += xoff
    xoff = 0
if yoff < 0:
    ysize += yoff
    yoff = 0
if xoff + xsize > chelsa_nx:
    xsize = chelsa_nx - xoff
if yoff + ysize > chelsa_ny:
    ysize = chelsa_ny - yoff

if xsize <= 0 or ysize <= 0:
    raise RuntimeError("La ventana de corte (srcWin) es inválida o está fuera de rango.")

# ========== 5) USAR gdal.Translate PARA EXTRAER ESA SUBVENTANA SIN SHIFT ==========
out_path = "bio/cropped/CHELSA_ai_1981-2010_V.2.1_cropped.tif"
out_dir = Path("bio/cropped")
out_dir.mkdir(parents=True, exist_ok=True)

print(f"Recortando CHELSA en la intersección con elevation:\n  {chelsa_path}\n  -> {out_path}")

translate_opts = gdal.TranslateOptions(
    srcWin=[xoff, yoff, xsize, ysize],
    creationOptions=["TILED=NO"]  # sin formato tiled
)

gdal.Translate(
    destName=out_path,
    srcDS=chelsa_ds,
    options=translate_opts
)

# Cerramos
chelsa_ds = None

print("¡Listo! Se generó el recorte en la carpeta bio/cropped/.")
