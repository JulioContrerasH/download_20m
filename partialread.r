install.packages("systemfonts")
install.packages("textshaping")
install.packages("ragg")
install.packages("pkgdown")
install.packages("devtools")
install.packages("terra")
devtools::install_github("rspatial/terra")


install.packages("raster")
install.packages("ggplot2")
install.packages("viridis")

# Cargar las librerías necesarias
library(raster)
library(ggplot2)
library(viridis)


# Leer el archivo raster
r <- raster("bio/tiff/CHELSA_ai_1981-2010_V.2.1.tif")

# Función para leer y mostrar subventanas del raster
plot_multiple_subwindows <- function(raster, nrows, ncols, window_size) {
  # Lista para almacenar los gráficos
  plots <- list()

  # Dimensiones del raster
  raster_rows <- nrow(raster)
  raster_cols <- ncol(raster)

  # Crear subventanas y graficarlas
  for (row_start in seq(1, raster_rows, by = window_size)) {
    for (col_start in seq(1, raster_cols, by = window_size)) {
      
      # Leer una subventana del raster
      partial_raster <- readRaster(raster, row = row_start, nrows = window_size, col = col_start, ncols = window_size)
      
      # Convertir la subventana en un data frame
      raster_df <- as.data.frame(partial_raster, xy = TRUE)
      
      # Crear el gráfico
      p <- ggplot(raster_df, aes(x = x, y = y, fill = layer)) +
        geom_raster() +
        scale_fill_viridis(option = "C") +  # Usando la paleta viridis
        theme_minimal() +                   # Minimal style for the plot
        labs(title = paste("Subventana: Rows", row_start, "-", row_start + window_size - 1, 
                           "Cols", col_start, "-", col_start + window_size - 1), 
             x = "Longitud", y = "Latitud") +
        theme(legend.position = "bottom")
      
      # Almacenar el gráfico en la lista
      plots[[length(plots) + 1]] <- p
    }
  }
  
  # Mostrar todos los gráficos
  return(plots)
}

# Llamar a la función para mostrar subventanas
plots <- plot_multiple_subwindows(r, nrows = 1024, ncols = 1024, window_size = 1024)

# Mostrar todos los gráficos generados
for (p in plots) {
  print(p)
}
