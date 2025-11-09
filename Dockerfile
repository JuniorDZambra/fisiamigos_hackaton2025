# Usa Miniconda para manejar dependencias geoespaciales desde conda-forge
FROM continuumio/miniconda3

WORKDIR /app

# Copia requirements.txt para aprovechar la cache de Docker
COPY requirements.txt /app/requirements.txt

# Configura conda y instala dependencias geoespaciales y librerías básicas desde conda-forge
RUN conda update -n base -c defaults conda -y && \
    conda config --add channels conda-forge && \
    conda config --set channel_priority strict && \
    conda install -y python=3.11 \
        geopandas \
        gdal \
        fiona \
        pyproj \
        shapely \
        rtree \
        pandas \
        dash \
        plotly \
        dash-bootstrap-components && \
    conda clean -afy

# Instala paquetes pip restantes
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia la aplicación
COPY . /app

# Puerto que exponemos
EXPOSE 8050

# Comando por defecto: usar gunicorn apuntando al servidor WSGI de Dash
# Asume que la app está en app.py y la variable principal es app (gunicorn usa app.server)
CMD ["gunicorn", "app:app.server", "--bind", "0.0.0.0:8050", "--workers", "4", "--timeout", "120"]
