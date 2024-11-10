import pandas as pd
from openpyxl import load_workbook

# Cargar el archivo de Excel con pandas
archivo = 'GSAF5.xls'
df = pd.read_excel(archivo, sheet_name='Hoja1')  # Cambia por tu hoja

# Cargar el archivo de Excel con openpyxl para obtener el color de la celda
libro = load_workbook(archivo, data_only=True)
hoja = libro['Hoja1']  # Cambia por el nombre de tu hoja

# Función para obtener el color de fondo de una celda específica
def obtener_color_fondo(fila, columna):
    celda = hoja.cell(row=fila + 1, column=columna + 1)  # Las celdas en openpyxl empiezan desde 1
    return celda.fill.start_color.rgb if celda.fill.start_color else None

# Crear una nueva columna en el DataFrame con los colores de cada celda en la primera columna
df['ColorFondo'] = [obtener_color_fondo(i, 0) for i in range(len(df))]

# Mostrar el DataFrame con la nueva columna de colores
print(df)