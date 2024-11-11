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
porcentaje_inconsistencias=len(filas_inconsistentes)/len(GSAF)*100

invalid_azul=[x[0] for x in filas_inconsistentes if x[1]=="INVALID" and x[2]==16764057]
porcentaje_invalid_azul=len(invalid_azul)/len(filas_inconsistentes)*100
#Hay un 99,27 de invalid azules, decidimos poner como cuestionable toda la lista
#Ya que hay menos de un 1% de error
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

#%% Hacemos un grafico de el resultado para nuestro primer objetivo
fig, ax = plt.subplots()
barras=ax.barh([1,2,3,4,5],cantidad_incidentes_por_tipo["Cantidad"],color=["gold","lawngreen","blue","orange","tan"])
etiquetas_y=list(cantidad_incidentes_por_tipo["Type"])
ax.bar_label(barras, padding=0, label_type='edge',rotation=270)
ax.set_yticks([1,2,3,4,5])
ax.set_yticklabels(etiquetas_y)
ax.set_ylabel("Tipo de ataque")
ax.set_xlabel("Cantidad de ataques")
plt.tight_layout()
#%%procesamiento para graficar
#le asignamos un id a cada pais ara ubicarlo en el grafico
paises_distintos=sql^"""SELECT DISTINCT Country FROM cantidad_incidentes_por_tipo_por_pais ORDER BY Cantidad asc"""

id_paises={}
paises_id={}
for id in range(1,len(paises_distintos)+1):
    pais=paises_distintos.iloc[id-1,0]
    id_paises[id]=pais
    paises_id[pais]=id

dict_provoked={}
dict_unprovoked={}
dict_att_on_boat={}
dict_sea_disaster={}
dict_Questionable={}

Provoked_paises=sql^"""SELECT DISTINCT Country, Cantidad FROM cantidad_incidentes_por_tipo_por_pais WHERE Type='PROVOKED'""" 
Unprovoked_paises=sql^"""SELECT DISTINCT Country, Cantidad  FROM cantidad_incidentes_por_tipo_por_pais WHERE Type='UNPROVOKED'"""
Sea_disaster_paises=sql^"""SELECT DISTINCT Country, Cantidad  FROM cantidad_incidentes_por_tipo_por_pais WHERE Type='SEA DISASTER'"""
Att_on_boat_paises=sql^"""SELECT DISTINCT Country, Cantidad  FROM cantidad_incidentes_por_tipo_por_pais WHERE Type='ATTACKS ON BOAT'"""
Questianble_paises=sql^"""SELECT DISTINCT Country, Cantidad  FROM cantidad_incidentes_por_tipo_por_pais WHERE Type='QUESTIONABLE'"""

for i in range(len(Provoked_paises)):
    fila=Provoked_paises.iloc[i]
    pais=fila[0]
    valor=fila[1]
    dict_provoked[paises_id[pais]]=valor

for i in range(len(Unprovoked_paises)):
    fila=Unprovoked_paises.iloc[i]
    pais=fila[0]
    valor=fila[1]
    dict_unprovoked[paises_id[pais]]=valor

for i in range(len(Att_on_boat_paises)):
    fila=Att_on_boat_paises.iloc[i]
    pais=fila[0]
    valor=fila[1]
    dict_att_on_boat[paises_id[pais]]=valor
    
for i in range(len(Sea_disaster_paises)):
    fila=Sea_disaster_paises.iloc[i]
    pais=fila[0]
    valor=fila[1]
    dict_sea_disaster[paises_id[pais]]=valor
    
for i in range(len(Questianble_paises)):
    fila=Questianble_paises.iloc[i]
    pais=fila[0]
    valor=fila[1]
    dict_Questionable[paises_id[pais]]=valor

fig , ax=plt.subplots()
