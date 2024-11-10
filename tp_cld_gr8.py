import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from inline_sql import sql,sql_val
from pandas import isna

#%% Fuimos al open refine, y seguimos el analisis

GSAF=pd.read_excel(".\\GSAF5-MOD.xlsx")

#%%
GSAF=GSAF.rename(columns={"Column 6":"ColorFondo"})
GSAF=GSAF[['Type','Country','ColorFondo']]


#%%

longitud_antes_de_borrar=len(GSAF)
#borramos los que no tienen paises por ser menos del 1%
GSAF = GSAF.dropna(subset="Country")
longitud_luego_de_borrar=len(GSAF)
porcentaje_pedida=(1-longitud_luego_de_borrar/longitud_antes_de_borrar)*100

#%% Recuperamos los tipos sin datos
color_por_tipo={"11918061":"UNPROVOKED","13430479":"ATTACKS ON BOAT","10079487":"PROVOKED","12976127":"SEA DISASTER","16764057":"QUESTIONABLE"}


for index, _ in GSAF.iterrows():
    if pd.isna(GSAF.loc[index,"Type"]):
        GSAF.loc[index,"Type"]=color_por_tipo[str(GSAF.loc[index,"ColorFondo"])]

#%%
for index, _ in GSAF.iterrows():
    if GSAF.loc[index,"Type"]=="WATERCRAFT" or GSAF.loc[index,"Type"]=="BOAT":
        GSAF.loc[index,"Type"]="ATTACKS ON BOAT"
#%% Miramos inconsistencias
filas_inconsistentes=[]
for index, _ in GSAF.iterrows():
    if color_por_tipo[str(GSAF.loc[index,"ColorFondo"])]!=GSAF.loc[index,"Type"]:
        filas_inconsistentes.append((index,GSAF.loc[index,"Type"],GSAF.loc[index,"ColorFondo"]))
#%%
#Vemos como 500 de invalids azules represante cerca del 10% de los datos
#Decidimos ver que proporcion Hay de azueles y si hay mucho le asignamos QUESTIONABLE

invalid_azul=[x[0] for x in filas_inconsistentes if x[1]=="INVALID" and x[2]==16764057]
porcentaje_invalid_azul=len(invalid_azul)/len(filas_inconsistentes)*100
#Hay un 99,27 de invalid azules, decidimos poner como cuestionable toda la lista
#Ya que hay menos de un 1% de error
#%% hacemos la modificacion
for index, _, _ in filas_inconsistentes:
    GSAF.loc[index,"Type"]="QUESTIONABLE"
    GSAF.loc[index,"ColorFondo"]=16764057

#%% Con un error acumulado de menos del 2% aprox 140 casos hacemos los graficos
cantidad_incidentes_por_tipo=sql^ """SELECT Type, COUNT(Country) AS Cantidad FROM GSAF GROUP BY TYPE ORDER BY Cantidad ASC  """

cantidad_incidentes_por_tipo_por_pais=sql^ """SELECT Country, Type, COUNT(Country) AS Cantidad FROM GSAF GROUP BY  Country, Type HAVING Cantidad>2 ORDER BY Cantidad DESC  """

#%% Hacemos unos graficos de los resultados
fig, ax = plt.subplots()
barras=ax.barh([1,2,3,4,5],cantidad_incidentes_por_tipo["Cantidad"],color=["gold","lawngreen","blue","orange","tan"])
etiquetas_y=list(cantidad_incidentes_por_tipo["Type"])
ax.bar_label(barras, padding=0, label_type='edge',rotation=270)
ax.set_yticks([1,2,3,4,5])
ax.set_yticklabels(etiquetas_y)
plt.tight_layout()
#%%
fig, ax = plt.subplots()


