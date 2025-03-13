#!/usr/bin/env python3
"""
This script warps each input GeoTIFF so that it matches the exact grid
(extension, size, projection) of a reference TIFF, then combines all
the warped GeoTIFFs into a single multi-band output.

Author: Julio Contreras
Date: 2024-03-13
"""

from pathlib import Path
import os
from osgeo import gdal

def get_raster_info(raster_path: str) -> dict:
    """
    Retrieve basic information from the given raster file:
    
    - width, height: pixel dimensions
    - xres, yres: pixel size (resolution)
    - projection: WKT of the spatial reference
    - bbox: bounding box (xmin, ymin, xmax, ymax)
    
    :param raster_path: Path to the raster file
    :return: Dictionary with the extracted information
    :raises FileNotFoundError: If the raster cannot be opened
    """
    ds = gdal.Open(raster_path)
    if not ds:
        raise FileNotFoundError(f"Could not open {raster_path}")
    
    width = ds.RasterXSize
    height = ds.RasterYSize
    gt = ds.GetGeoTransform()
    proj = ds.GetProjection()

    xres = gt[1]
    yres = gt[5]
    xmin = gt[0]
    ymax = gt[3]
    xmax = xmin + width * xres
    ymin = ymax + height * yres

    ds = None  # Release dataset

    return {
        "width": width,
        "height": height,
        "projection": proj,
        "bbox": (xmin, ymin, xmax, ymax),
        "xres": xres,
        "yres": yres
    }


def warp_exact_grid(input_tif: str, output_tif: str, ref_info: dict) -> None:
    """
    Warp 'input_tif' so that:
      - It has the same spatial extent as the reference TIFF
      - It has the same number of rows and columns as the reference
      - It uses the same projection
      - It uses DEFLATE compression and tiling (BlockSize=1024)
      - It keeps the same data type as the source band
    
    :param input_tif: Path to the input TIFF file
    :param output_tif: Path to the output (warped) TIFF file
    :param ref_info: A dictionary containing reference raster info
    """
    (xmin, ymin, xmax, ymax) = ref_info["bbox"]
    ref_width = ref_info["width"]
    ref_height = ref_info["height"]
    ref_proj = ref_info["projection"]

    dataset = gdal.Open(input_tif)
    if not dataset:
        raise FileNotFoundError(f"Could not open {input_tif}")

    # Obtain the data type from the first band
    band = dataset.GetRasterBand(1)
    data_type = band.DataType

    # Define warp options
    warp_opts = gdal.WarpOptions(
        format="GTiff",
        outputBounds=[xmin, ymin, xmax, ymax],
        width=ref_width,
        height=ref_height,
        dstSRS=ref_proj,
        resampleAlg="near",
        outputType=data_type,
        creationOptions=[
            "COMPRESS=DEFLATE",
            "TILED=YES",
            "BLOCKXSIZE=1024",
            "BLOCKYSIZE=1024",
            "BIGTIFF=YES"
        ]
    )

    # Perform the warp operation
    ds = gdal.Warp(
        destNameOrDestDS=output_tif,
        srcDSOrSrcDSTab=input_tif,
        options=warp_opts
    )
    ds = None  # Release dataset
    print(f"[warp_exact_grid] {input_tif} -> {output_tif}")


def create_multiband(final_multiband_tif: str, list_of_tifs: list[str]) -> None:
    """
    Combine multiple single-band GeoTIFF files (already matching in size
    and projection) into a single multi-band GeoTIFF. Each file will become
    a separate band in the output file. The band name is set to the file's
    base name (excluding .tif).
    
    - Uses a temporary VRT to aggregate sources in separate bands
    - Then translates the VRT to a single GeoTIFF with DEFLATE compression
    
    :param final_multiband_tif: Path to the final multi-band TIFF
    :param list_of_tifs: List of paths to single-band TIFF files
    """
    vrt_temp = "temp_mosaic.vrt"

    # Build a VRT with each input as a separate band
    vrt_ds = gdal.BuildVRT(
        destName=vrt_temp,
        srcDSOrSrcDSTab=list_of_tifs,
        separate=True
    )
    
    if vrt_ds:
        # Rename each band using the file name without extension
        for i, tif_path in enumerate(list_of_tifs):
            band_i = vrt_ds.GetRasterBand(i + 1)
            base_name = os.path.splitext(os.path.basename(tif_path))[0]
            band_i.SetDescription(base_name)
        vrt_ds.FlushCache()
        vrt_ds = None

    # Translate the VRT into a single compressed GeoTIFF
    translate_opts = gdal.TranslateOptions(
        format="GTiff",
        outputType=gdal.GDT_Float32,
        creationOptions=[
            "TILED=YES",
            "BLOCKXSIZE=1024",
            "BLOCKYSIZE=1024",
            "INTERLEAVE=PIXEL",
            "COMPRESS=DEFLATE",
            "BIGTIFF=YES"
        ]
    )
    out_ds = gdal.Translate(
        destName=final_multiband_tif,
        srcDS=vrt_temp,
        options=translate_opts
    )
    out_ds = None

    # Clean up the temporary VRT
    if os.path.exists(vrt_temp):
        os.remove(vrt_temp)

    print(f"[create_multiband] Created multiband: {final_multiband_tif}")


if __name__ == "__main__":
    """
    Main entry point. Adjust paths as needed.
    """
    ref_tif = "/home/contreras/Documents/GitHub/download_20m/elevation.tif"
    ref_info = get_raster_info(ref_tif)

    dir_images = Path("/home/contreras/Documents/GitHub/download_20m/bio")
    path_images = sorted(list(dir_images.glob("*.tif")))

    dir_crop = Path("/home/contreras/Documents/GitHub/download_20m/crop2")
    dir_crop.mkdir(exist_ok=True)

    final_tifs = []

    # Warp each input TIF to match the reference grid
    for path_img in path_images:
        out_name = dir_crop / path_img.name
        warp_exact_grid(str(path_img), str(out_name), ref_info)
        final_tifs.append(str(out_name))

    # Create a multi-band output
    final_multiband = dir_crop / "CHELSA_multibanda_NOcompress.tif"
    create_multiband(str(final_multiband), final_tifs)

    print("Process completed!")
