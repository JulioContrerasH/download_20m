import os
import requests

years = range(1981, 2019)

base_url = "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/annual/swb/CHELSA_swb_{}_V.2.1.tif"

def download_file(url, filename):
    # Verificar si el archivo ya existe
    if os.path.exists(filename):
        print(f"{filename} ya existe. Se omite la descarga.")
        return

    # Descargar el archivo si no existe
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"{filename} descargado con éxito.")
    else:
        print(f"Error al descargar {filename}.")

# Crear directorio si no existe
# os.makedirs("images", exist_ok=True)

# # Descargar los archivos
# for year in years:
#     url = base_url.format(year)
#     filename = f"images/CHELSA_swb_{year}_V.2.1.tif"
#     download_file(url, filename)

images = [
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_ai_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_clt_max_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_clt_mean_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_clt_min_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_clt_range_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_cmi_max_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_cmi_mean_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_cmi_min_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_cmi_range_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_fcf_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_fgd_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_gdd0_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_gdd10_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_gdd5_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_gddlgd0_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_gddlgd10_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_gddlgd5_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_gdgfgd0_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_gdgfgd10_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_gdgfgd5_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_gsl_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_gsp_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_gst_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_hurs_max_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_hurs_mean_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_hurs_min_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_hurs_range_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_kg0_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_kg1_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_kg2_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_kg3_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_kg4_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_kg5_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_lgd_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_ngd0_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_ngd10_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_ngd5_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_npp_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_pet_penman_max_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_pet_penman_mean_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_pet_penman_min_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_pet_penman_range_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_rsds_1981-2010_max_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_rsds_1981-2010_mean_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_rsds_1981-2010_min_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_rsds_1981-2010_range_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_scd_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_sfcWind_max_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_sfcWind_mean_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_sfcWind_min_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_sfcWind_range_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_swb_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_swe_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_vpd_max_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_vpd_mean_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_vpd_min_1981-2010_V.2.1.tif",
    "https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_vpd_range_1981-2010_V.2.1.tif"

]
for x in [1,2,3,4,5,6,7,10,11,12,13,14,15,16,17]:
    var = f"https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_bio{x}_1981-2010_V.2.1.tif"
    images.append(var)


# Descargar los archivos
for image in images:
    filename = "bio/" + image.split("bio/")[-1]
    download_file(image, filename)
    print(filename)