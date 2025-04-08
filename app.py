import pyodbc
import pandas as pd
import streamlit as st
import os

# Intenta importar configuración local, pero no falla si no existe
try:
    import config
    DB_SERVER = config.DB_SERVER
    DB_NAME = config.DB_NAME
    DB_USER = config.DB_USER
    DB_PASSWORD = config.DB_PASSWORD
except ImportError:
    # Si no hay config.py, busca variables de entorno
    DB_SERVER = os.environ.get("DB_SERVER")
    DB_NAME = os.environ.get("DB_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")

def obtener_datos_sql():
    try:
        # Configuración de la conexión con variables de entorno o config
        conexion = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_NAME};"
            f"UID={DB_USER};"
            f"PWD={DB_PASSWORD};"
        )
        # Establecer un tiempo de espera para la conexión
        conexion.timeout = 300
        
        # Definir el procedimiento almacenado y su parámetro
        procedimiento = "SELECT * FROM SEGUIMIENTO_VENTAS_ABRIL"

        # Ejecutar el procedimiento almacenado y cargar los resultados en un DataFrame
        df = pd.read_sql(procedimiento, conexion)

        # Cerrar la conexión
        conexion.close()
        
        return df

    except Exception as e:
        st.error(f"Error al conectar o ejecutar el procedimiento almacenado: {e}")
        return None

def main():
    # Configurar el título de la página de Streamlit
    st.title('Seguimiento de VentasPRB')
    
    # Verificar si tenemos las credenciales necesarias
    if not all([DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD]):
        st.error("Faltan credenciales para la conexión a la base de datos.")
        return
    
    # Obtener los datos
    df = obtener_datos_sql()
    
    # Mostrar los datos si se obtuvieron correctamente
    if df is not None:
        # Mostrar información básica del DataFrame
        st.write(f"Total de registros: {len(df)}")
        st.write(f"Columnas: {', '.join(df.columns)}")
        
        # Mostrar la tabla con Streamlit
        st.dataframe(df)
        
        # Opcional: Agregar filtro de búsqueda
        search_term = st.text_input('Buscar en la tabla')
        if search_term:
            # Filtrar el DataFrame basado en el término de búsqueda
            filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
            st.dataframe(filtered_df)

if __name__ == "__main__":
    main()