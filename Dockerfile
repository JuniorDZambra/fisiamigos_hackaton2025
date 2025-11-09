
FROM continuumio/miniconda3

WORKDIR /app


COPY requirements.txt /app/requirements.txt

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


RUN pip install --no-cache-dir -r /app/requirements.txt


COPY . /app


EXPOSE 8050


CMD ["gunicorn", "app:app.server", "--bind", "0.0.0.0:8050", "--workers", "4", "--timeout", "120"]
