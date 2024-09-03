
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import tkinter as tk
from tkinter import ttk 

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 41.5864,
	"longitude": 12.9707,
	"current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m"],
	"hourly": ["temperature_2m", "dew_point_2m", "evapotranspiration", "wind_speed_10m", "wind_direction_10m"],
	"daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "precipitation_probability_max", "wind_speed_10m_max", "wind_direction_10m_dominant"],
	"timezone": "auto",
	"past_days": 14,
	"forecast_days": 1
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = round(current.Variables(0).Value(), 1)
current_relative_humidity_2m = current.Variables(1).Value()
current_wind_speed_10m = round(current.Variables(2).Value(),1)
current_wind_direction_10m = round(current.Variables(3).Value())


# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_dew_point_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_evapotranspiration = hourly.Variables(2).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()
hourly_wind_direction_10m = hourly.Variables(4).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["dew_point_2m"] = hourly_dew_point_2m
hourly_data["evapotranspiration"] = hourly_evapotranspiration
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["wind_direction_10m"] = hourly_wind_direction_10m

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(2).ValuesAsNumpy()
daily_precipitation_probability_max = daily.Variables(3).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(4).ValuesAsNumpy()
daily_wind_direction_10m_dominant = daily.Variables(5).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}
daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min
daily_data["precipitation_sum"] = daily_precipitation_sum
daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant

daily_dataframe = pd.DataFrame(data = daily_data)
print(daily_dataframe)



try:
     from ctypes import windll
     windll.shcore.SetProcessDpiAwareness(1)
except:
     pass


import tkinter as tk
from tkinter import ttk

class Agriweather(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agriweather")
        self.main_frame = ttk.Frame(self, padding=(10, 10))
        self.main_frame.grid(column=0, row=0)
        
        self.dati_meteo = DatiMeteo(self.main_frame)
        self.setup_widgets()

    def setup_widgets(self):
        separator = ttk.Separator(self.main_frame, orient='vertical')
        separator.grid(column=1, row=0, rowspan=3, sticky='ns', padx=10)

        dati_produzione = ttk.Frame(self.main_frame)
        dati_produzione.grid(column=2, row=0, sticky="nw")

        olive_input = tk.StringVar()
        olio_input = tk.StringVar()
        resa_input = tk.StringVar()

        oliva_label = ttk.Label(dati_produzione, text="Inserire quantità olive raccolte in kg:")
        oliva_input_entry = ttk.Entry(dati_produzione, textvariable=olive_input)
        olio_label = ttk.Label(dati_produzione, text="Inserire quantità olio in kg:")
        olio_input_entry = ttk.Entry(dati_produzione, textvariable=olio_input)
        resa_display = ttk.Label(dati_produzione, textvariable=resa_input)
        resa_button = ttk.Button(dati_produzione, text="Calcola", command=lambda: Calcolo_resa(olive_input, olio_input, resa_input))

        oliva_label.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        oliva_input_entry.grid(column=1, row=0, padx=5, pady=5)
        olio_label.grid(column=0, row=1, padx=5, pady=5, sticky="w")
        olio_input_entry.grid(column=1, row=1, padx=5, pady=5)
        resa_display.grid(column=1, row=2, padx=5, pady=5, sticky="w")
        resa_button.grid(column=0, row=2, padx=5, pady=5, sticky="w")

class DatiMeteo:
    def __init__(self, parent):
        self.dati_meteo = ttk.Frame(parent)
        self.dati_meteo.grid(column=0, row=0, sticky="nw")
        
        self.temperatura_var = tk.StringVar()
        self.temperatura_var.set(f"Temperatura corrente: {current_temperature_2m}°C")  
        self.temperatura_label = ttk.Label(self.dati_meteo, textvariable=self.temperatura_var)
        self.temperatura_label.grid(column=0, row=0, sticky="w")

        self.umidità_var = tk.StringVar()
        self.umidità_var.set(f"Umidità relativa: {current_relative_humidity_2m}%")  
        self.umidità_label = ttk.Label(self.dati_meteo, textvariable=self.umidità_var)
        self.umidità_label.grid(column=0, row=1, sticky="w")

        self.velocità_vento_var = tk.StringVar()
        self.velocità_vento_var.set(f"Velocità del vento: {current_wind_speed_10m} Km/h")
        self.velocità_vento_label = ttk.Label(self.dati_meteo, textvariable=self.velocità_vento_var)
        self.velocità_vento_label.grid(column=0, row=2, sticky="w")
        
        self.direzione_vento_var = tk.StringVar()
        if current_wind_direction_10m == 0 or 360:
         self.direzione_vento_var.set(f"La direzione del vento è: Nord") 
        elif 0 <= current_wind_direction_10m <= 45:
         self.direzione_vento_var.set(f"La direzione del vento è: Nord-Est") 
        elif 45 <= current_wind_direction_10m <= 90:
         self.direzione_vento_var.set(f"La direzione del vento è: Est-Nord")
        elif current_wind_direction_10m == 90:
         self.direzione_vento_var.set(f"La direzione del vento è: Est")
        elif 90 <= current_wind_direction_10m <= 135:
         self.direzione_vento_var.set(f"La direzione del vento è: Est-Sud")
        elif 135 <= current_wind_direction_10m <= 180:
         self.direzione_vento_var.set(f"La direzione del vento è: Sud-Est")
        elif current_wind_direction_10m == 180:
         self.direzione_vento_var.set(f"La direzione del vento è: Sud")
        elif 180 <= current_wind_direction_10m <= 225:
         self.direzione_vento_var.set(f"La direzione del vento è: Sud-Ovest")
        elif 225 <= current_wind_direction_10m <= 270:
         self.direzione_vento_var.set(f"La direzione del vento è: Ovest-Sud")
        elif current_wind_direction_10m == 270:
         self.direzione_vento_var.set(f"La direzione del vento è: Ovest")
        elif 270 <= current_wind_direction_10m <= 315:
         self.direzione_vento_var.set(f"La direzione del vento è: Ovest-Nord")
        elif 315 <= current_wind_direction_10m <= 360:
         self.direzione_vento_var.set(f"La direzione del vento è: Nord-Ovest")
           
        else:
            pass
        self.direzione_vento_label = ttk.Label(self.dati_meteo, textvariable=self.direzione_vento_var)
        self.direzione_vento_label.grid(column=0, row=3, sticky="w")
        
        

def Calcolo_resa(olive_input, olio_input, resa_input):
    try:
        olive = float(olive_input.get())
        olio = float(olio_input.get())
        resa = round(((olio / olive) * 100), 2)
        resa_input.set(f"La resa per quintale è {resa} litri")
    except ValueError:
        resa_input.set("Errore nei dati inseriti")

root = Agriweather()

style = ttk.Style(root)

style.theme_use("alt")

root.mainloop()




