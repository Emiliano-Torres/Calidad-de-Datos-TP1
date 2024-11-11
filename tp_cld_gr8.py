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


#%%Vemos si es correcto borrar las filas sin paises

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
porcentaje_inconsistencias=len(filas_inconsistentes)/len(GSAF)*100

invalid_azul=[x[0] for x in filas_inconsistentes if x[1]=="INVALID" and x[2]==16764057]
porcentaje_invalid_azul=len(invalid_azul)/len(filas_inconsistentes)*100
#Hay un 95,27 de invalid azules
#nos gustaria por simplicidad poner toda la lista como azul y questionable
porcentaje_error_poner_azul_toda_la_lista=((100-95.27)/100 *len(filas_inconsistentes)/len(GSAF))*100 
#Pasariamos del 8 porciento de incosistencia al 0.39% de incosistencia
#lo cual es aceptable para nuestro analisis
#%% Veamos que hacer con los paises dobles y continentes
paises_dobles=sql^"""SELECT Country FROM GSAF WHERE Country LIKE '%/%'"""
continentes=sql^"""SELECT Country FROM GSAF 
                WHERE COUNTRY='AFRICA' OR COUNTRY='ASIA?'"""
#como son 11 registros de 7000 podemos eliminarlos
paises_a_eliminar=[]
for index, _ in paises_dobles.iterrows():
    paises_a_eliminar.append(paises_dobles.iloc[index,0])
for index, _ in continentes.iterrows():
    paises_a_eliminar.append(continentes.iloc[index,0])
    
for index, _ in GSAF.iterrows():
    pais=GSAF.loc[index,"Country"]
    if pais in paises_a_eliminar:
        GSAF=GSAF.drop(index, axis=0)
    
    



#%% hacemos la modificacion
for index, _, _ in filas_inconsistentes:
    GSAF.loc[index,"Type"]="QUESTIONABLE"
    GSAF.loc[index,"ColorFondo"]=16764057
#%% Con un error acumulado de menos del 2% aprox 140 casos hacemos los graficos
cantidad_incidentes_por_tipo=sql^ """SELECT Type, COUNT(Country) AS Cantidad FROM GSAF GROUP BY TYPE ORDER BY Cantidad ASC"""

cantidad_incidentes_por_tipo_por_pais=sql^ """SELECT Country, Type, COUNT(Country) AS Cantidad FROM GSAF GROUP BY  Country, Type HAVING Cantidad>0 ORDER BY Cantidad DESC  """
#Ya que hay menos de un 1% de error con respecto al dataframe total
porcentaje_incosistencia_restante=((1-porcentaje_inconsistencias/100)*len(filas_inconsistentes)/len(GSAF))*100
#%% Hacemos un grafico de el resultado para nuestro primer objetivo
fig, ax = plt.subplots()
#hacemos el grafico de barras
barras=ax.barh([1,2,3,4,5],cantidad_incidentes_por_tipo["Cantidad"],color=["gold","lawngreen","blue","orange","tan"])
etiquetas_y=list(cantidad_incidentes_por_tipo["Type"])
ax.bar_label(barras, padding=0, label_type='edge',rotation=270)
#ponemos ticks y etiquetsa
ax.set_yticks([1,2,3,4,5])
ax.set_yticklabels(etiquetas_y)
ax.set_ylabel("Tipo de ataque")
ax.set_xlabel("Cantidad de ataques")
plt.tight_layout()
#%%procesamiento para graficar


df_paises_incidendes =cantidad_incidentes_por_tipo_por_pais #cambiamos el nombre por practicidad
df_paises_incidendes_pivot = df_paises_incidendes.pivot_table(index='Country', columns='Type', values='Cantidad', aggfunc='sum', fill_value=0)

#sumamos el total de incidentes por país (sumar todas las columnas)
df_paises_incidendes_pivot['total'] = df_paises_incidendes_pivot.sum(axis=1)

#Ordenamos por el total de incidentes (de mayor a menor) y seleccionar los 20 primeros países
df_paises_incidendes_top_10 = df_paises_incidendes_pivot.sort_values(by='total', ascending=False).head(20)

#Creamos el gráfico de barras apiladas para los 20 países más rankeados
ax = df_paises_incidendes_top_10.drop(columns='total').plot(kind='bar', stacked=True, figsize=(10, 6), color=["lawngreen","orange","blue","gold","tan"])

#Añadimos títulos y etiquetas
ax.set_title('Top 20 Países con más Incidentes por Tipo')
ax.set_ylabel('Cantidad de Incidentes')
ax.set_xlabel('Países')

#Mostramos el gráfico
plt.xticks(rotation=45,ha='right')
plt.tight_layout()
plt.show()
#%% Repetimos el proceso eliminando los 3 paises más rankeados

df_paises_incidendes_pivot['total'] = df_paises_incidendes_pivot.sum(axis=1)


df_paises_incidendes_pivot_sorted = df_paises_incidendes_pivot.sort_values(by='total', ascending=False)

#Eliminamos los 3 países más rankeados
df_paises_incidendes_filtered = df_paises_incidendes_pivot_sorted.iloc[3:20]


ax = df_paises_incidendes_filtered.drop(columns='total').plot(kind='bar', stacked=True, figsize=(10, 6), color=["lawngreen","orange","blue","gold","tan"])


ax.set_title('Países con más Incidentes (Excluyendo los 3 más rankeados)')
ax.set_ylabel('Cantidad de Incidentes')
ax.set_xlabel('Países')
ax.bar_label(barras, padding=0, label_type='edge',rotation=270)

plt.xticks(rotation=45,ha="right")
plt.tight_layout()
plt.show()