import yahoo_fin.stock_info as si

nasdaq_tickers = si.tickers_nasdaq()

from tqdm import tqdm
import yfinance as yf
import pandas as pd

# Inicializamos una lista vacía para guardar los datos
datos_acciones = []

# Iteramos sobre la lista de símbolos
# Usamos tqdm para mostrar la barra de progreso
for simbolo in tqdm(nasdaq_tickers, desc="Obteniendo cotizaciones"):
    accion = yf.Ticker(simbolo)
    try:
        cotizacion = accion.history(period='1d')['Close'].iloc[0]  # Usamos iloc en lugar de [0] directamente
    except IndexError:
        cotizacion = None  # En caso de que no se encuentre cotización, asignamos None

    # Añadimos el símbolo y la cotización al listado
    datos_acciones.append({'Accion': simbolo, 'Cotizacion': cotizacion})

# Convertimos la lista de datos en un DataFrame para una mejor visualización y manejo
df_acciones = pd.DataFrame(datos_acciones)

# Mostramos el DataFrame
print(df_acciones)

df_acciones.sort_values(by='Cotizacion', ascending=True).head(1000).to_csv('nasdaq_tickers.csv', index=False)

