
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import tkinter as tk
from tkinter import ttk
from tkinter import *
from PIL import ImageTk, Image

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
	"current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "weather_code" ],
	"daily": ["precipitation_sum", "precipitation_probability_max"],
	"timezone": "auto",
	"past_days": 31,
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
current_wind_gusts_10m = round(current.Variables(0).Value())
current_weather_code = current.Variables(0).Value()


# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_precipitation_probability_max = daily.Variables(1).ValuesAsNumpy()
daily_precipitation_probability = (daily_precipitation_probability_max[-1])
daily_precipitation_sum = daily.Variables(0).ValuesAsNumpy()
weekly_precipitation = round(sum(daily_precipitation_sum[-8:]))
monthly_precipitation = round(sum(daily_precipitation_sum[-32:]))



daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}


daily_data["precipitation_sum"] = daily_precipitation_sum
daily_data["precipitation_probability_max"] = daily_precipitation_probability_max

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
        
        self.info_generali = InfoGenerali(self)
        self.info_generali.grid(column=0, row=0,columnspan=3, sticky="ew")
        
        
        self.horizontal_separator = ttk.Separator(self, orient='horizontal')
        self.horizontal_separator.grid(column=0, row=1, columnspan=3, sticky='ew')

        self.main_frame = ttk.Frame(self, padding=(10, 10))
        self.main_frame.grid(column=0, row=2,columnspan=3, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        
        self.dati_meteo = DatiMeteo(self.main_frame)
        self.dati_meteo.grid(column=0, row=0, sticky="nw")
        
        self.setup_widgets()

    def setup_widgets(self):
        separator = ttk.Separator(self.main_frame, orient='vertical')
        separator.grid(column=1, row=0, sticky='ns', padx=10)

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
        
class InfoGenerali(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.nome = ttk.Label(self, text="Agriweather - Olivicoltura",font=("Arial", 12, "bold"))
        self.nome.grid(column=0, row=0, sticky="n", pady=(0, 10))
        
        self.load_image()
    def load_image(self):
        img = Image.open("./Immaginee-removebg-preview.png")
        img = img.resize((200, 150), Image.Resampling.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(img)

        self.image_label = ttk.Label(self, image=self.img_tk)
        self.image_label.grid(column=0, row=1, pady=(10, 0))
        
class DatiMeteo(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.temperatura_var = tk.StringVar()
        self.temperatura_var.set(f"Temperatura corrente: {current_temperature_2m}°C")  
        self.temperatura_label = ttk.Label(self, textvariable=self.temperatura_var)
        self.temperatura_label.grid(column=0, row=0, sticky="w")

        self.umidità_var = tk.StringVar()
        self.umidità_var.set(f"Umidità relativa: {current_relative_humidity_2m}%")  
        self.umidità_label = ttk.Label(self, textvariable=self.umidità_var)
        self.umidità_label.grid(column=0, row=1, sticky="w")

        self.velocità_vento_var = tk.StringVar()
        self.velocità_vento_var.set(f"Velocità del vento: {current_wind_speed_10m} Km/h")
        self.velocità_vento_label = ttk.Label(self, textvariable=self.velocità_vento_var)
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
        self.direzione_vento_label = ttk.Label(self, textvariable=self.direzione_vento_var)
        self.direzione_vento_label.grid(column=0, row=3, sticky="w")
        
        self.raffica_vento_var = tk.StringVar()
        self.raffica_vento_var.set(f"Raffica del vento max: {current_wind_gusts_10m} Km/h")
        self.raffica_vento_label = ttk.Label(self, textvariable=self.raffica_vento_var)
        self.raffica_vento_label.grid(column=0, row=4, sticky="w")
        
        self.probabilità_precipitazioni_var = tk.StringVar()
        self.probabilità_precipitazioni_var.set(f"Probabilità di pioggia oggi: {daily_precipitation_probability} %")
        self.probabilità_precipitazioni_label = ttk.Label(self, textvariable=self.probabilità_precipitazioni_var)
        self.probabilità_precipitazioni_label.grid(column=0, row=5, sticky="w")
        
        self.precipitazioni_settimanali_var = tk.StringVar()
        self.precipitazioni_settimanali_var.set(f"Pioggia cumulata negli ultimi 7gg: {weekly_precipitation} mm")
        self.precipitazioni_settimanali_label = ttk.Label(self, textvariable=self.precipitazioni_settimanali_var)
        self.precipitazioni_settimanali_label.grid(column=0, row=5, sticky="w")
        
        self.precipitazioni_mensili_var = tk.StringVar()
        self.precipitazioni_mensili_var.set(f"Pioggia cumulata negli ultimi 31gg: {monthly_precipitation} mm")
        self.precipitazioni_mensili_label = ttk.Label(self, textvariable=self.precipitazioni_mensili_var)
        self.precipitazioni_mensili_label.grid(column=0, row=6, sticky="w")
        


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




