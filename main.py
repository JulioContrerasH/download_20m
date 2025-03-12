import ee
import pandas as pd
import cubexpress

try:
    ee.Initialize(project="ee-julius013199")
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project="ee-julius013199")


table = pd.read_csv("tables/methane_experiment.csv")
filtered_table = table[table["tile"].str.startswith("S2", na=False)]


filtered_table["tile_date"] = filtered_table["background_image_tile"].astype(str).apply(
    lambda a: a.split("_")[2][:8] if "_" in a else None
)
filtered_table["tile_date"] = pd.to_datetime(filtered_table["tile_date"], format="%Y%m%d")


filtered_table["mgrs_tile"] = filtered_table["background_image_tile"].astype(str).apply(
    lambda s: s.split('_')[5][1:] if "_" in s else None
)

filtered_table["start_date"] = filtered_table["tile_date"].dt.floor("D").dt.strftime('%Y-%m-%d')
filtered_table["end_date"]   = (filtered_table["tile_date"].dt.floor("D") 
                               + pd.Timedelta(days=1)).dt.strftime('%Y-%m-%d')


for i, row in filtered_table.iterrows():

    if row.id_loc_image == "9bc4842b-6f78-4c2e-8db1-204b866fac1d":
        break
    
    start_date = row["start_date"]
    end_date = row["end_date"]

    image = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
                    .filterDate(start_date, end_date) \
                    .filter(ee.Filter.eq("MGRS_TILE", row["mgrs_tile"])) \
                    .first()
    
    image.getInfo()
    metadata = cubexpress.RasterTransform(
        crs=row.crs,
        geotransform={
            'scaleX': float(row["transform_a"]), 
            'shearX': float(row["transform_b"]), 
            'translateX': float(row["transform_c"]),
            'scaleY': float(row["transform_e"]), 
            'shearY': float(row["transform_d"]), 
            'translateY': float(row["transform_f"])
        },
        width=int(row["width"]),
        height=int(row["height"])
    )

    request = cubexpress.Request(
        id=f"{row.id_loc_image}/background_image_tile",
        raster_transform=metadata,
        bands=["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"],
        image=image
    )

    cube_requests = cubexpress.RequestSet(requestset=[request])

    cubexpress.getcube(
        request=cube_requests,
        output_path="/media/contreras/LaCie/cesar_s2_toa",
        nworkers=4,
        max_deep_level=5
    )
    print(i)



