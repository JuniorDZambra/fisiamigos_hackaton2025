from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import geopandas as gpd
import plotly.express as px
import json
import sys


try:
    gdf_provincias = gpd.read_file("Provincias.geojson")
except Exception as e:
    print(f"Error leyendo el GeoJSON: {e}", file=sys.stderr)
    gdf_provincias = None

try:
    df_indices = pd.read_csv("NDVI_Estadisticas_Provincias.csv")
except Exception as e:
    print(f"Error leyendo el CSV: {e}", file=sys.stderr)
    df_indices = None


app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])

if gdf_provincias is None or df_indices is None:
  
    app.layout = dbc.Container(
        [
            html.H1("Índices del futuro", className="app-title"),
            html.P("No se pudieron cargar los archivos Provincias.geojson o NDVI_Estadisticas_Provincias.csv. Revisa la consola."),
        ],
        className="p-4",
    )

else:
    
    try:
        mapa_con_datos = gdf_provincias.merge(
            df_indices,
            left_on="provincia",
            right_on="Provincia",
            how="left",
        )
    except Exception as e:
        print(f"Error haciendo merge: {e}", file=sys.stderr)
        mapa_con_datos = gdf_provincias.copy()

    
    try:
        mapa_con_datos = mapa_con_datos.to_crs(epsg=4326)
    except Exception:
        pass

    
    geojson = json.loads(mapa_con_datos.to_json())

   
    numeric_cols = df_indices.select_dtypes(include="number").columns.tolist()
    
    # Si no hay columnas numéricas detectadas, caer en NDVI_Mean si existe
    if not numeric_cols and "NDVI_Mean" in df_indices.columns:
        numeric_cols = ["NDVI_Mean"]

    
    controls = dbc.Card(
        [
            # El dropdown
            html.Div(
                [
                    dbc.Label("Seleccionar índice", html_for="col-dropdown"),
                    dcc.Dropdown(
                        id="col-dropdown",
                        options=[{"label": c, "value": c} for c in numeric_cols],
                        value=numeric_cols[0] if numeric_cols else None,
                        clearable=False,
                    ),
                ],
                className="mb-3",
            ),
            html.Hr(),

           
            dbc.Accordion(
                dbc.AccordionItem(
                    [
                        html.P("El NDVI (Índice de Vegetación de Diferencia Normalizada) es el indicador más usado para medir la salud y la densidad de la vegetación desde el espacio."),
                        html.P("Compara la luz Roja (que las plantas absorben) con la luz Infrarroja Cercana (NIR) (que las plantas reflejan)."),
                        html.H5("Valores del Índice (-1 a +1):"),
                        html.Ul([
                            html.Li([html.Strong("Valores Altos (+1):"), " Vegetación densa y saludable."]),
                            html.Li([html.Strong("Valores Medios (0.2-0.5):"), " Pastizales o matorrales."]),
                            html.Li([html.Strong("Valores Bajos (0):"), " Suelo desnudo o rocas."]),
                            html.Li([html.Strong("Valores Negativos (-1):"), " Agua o nieve."]),
                        ])
                    ],
                    title="🌿 ¿Qué es el NDVI?" # Título del acordeón
                ),
                start_collapsed=True, # Empieza cerrado
            ),
            

            html.Hr(), # Un separador más
            html.P("Interactúa con el mapa: acercar/alejar y pasar el mouse sobre una provincia."),
        ],
        body=True,
    )
    

    app.layout = dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.H1("Índices del futuro", className="app-title"),
                    width=12,
                ),
                className="py-3",
            ),
            dbc.Row(
                [
                    dbc.Col(controls, md=3), # Columna de controles (izquierda)
                    dbc.Col( # Columna del mapa (derecha)
                        dcc.Loading(
                            dcc.Graph(id="map-graph", config={"displayModeBar": True}),
                            type="default",
                        ),
                        md=9,
                    ),
                ],
                className="g-0",
            ),
            dbc.Row(
                dbc.Col(
                    html.Footer("Datos: NDVI por provincia · Visualización con Dash y Plotly", className="footer"),
                    className="py-4",
                )
            ),
        ],
        fluid=True,
        className="app-container",
    )

    @app.callback(
        Output("map-graph", "figure"),
        Input("col-dropdown", "value"),
    )
    def update_map(column):
       
        if column is None or column not in mapa_con_datos.columns:
            fig = px.choropleth_mapbox(
                mapa_con_datos,
                geojson=geojson,
                locations="provincia",
                featureidkey="properties.provincia",
                color=None,
                center={"lat": -40.4, "lon": -63.6},
                zoom=3,
                mapbox_style="carto-positron",
            )
            fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
            return fig

        
        fig = px.choropleth_mapbox(
            mapa_con_datos,
            geojson=geojson,
            locations="provincia",
            featureidkey="properties.provincia",
            color=column,
            hover_name="provincia",
            mapbox_style="carto-positron",
            center={"lat": -40.4, "lon": -63.6},
            zoom=3,
            opacity=0.75,
            color_continuous_scale="Viridis",
            
            
            labels={"provincia": "Provincia", column: "indice promedio"},
         
            title=f"{column} por Provincia"
        )

        fig.update_layout(
            margin={"r":0,"t":40,"l":0,"b":0},
            coloraxis_colorbar={"title": column},
        )
        return fig


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)