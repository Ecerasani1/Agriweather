
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import tkinter as tk
from tkinter import ttk
from tkinter import *
from PIL import ImageTk, Image
import numpy as np
from tkinter import messagebox

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
	"current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "weather_code","et0_fao_evapotranspiration" ],
    "hourly": ["wind_speed_10m"],
	"daily": ["precipitation_sum", "precipitation_probability_max","temperature_2m_max", "temperature_2m_min"],
	"timezone": "auto",
	"past_days": 31,
	"forecast_days": 7
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

hourly = response.Hourly()
hourly_wind_speed_10m = hourly.Variables(0).ValuesAsNumpy()
input_list = hourly_wind_speed_10m[-25:]
wind_avg = np.mean(input_list)
rounded_wind_avg = round(wind_avg)

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)

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
daily_et0_fao_evapotranspiration = daily.Variables(0).ValuesAsNumpy()
daily_evapotranspiration = round(daily_et0_fao_evapotranspiration[-1])
weekly_evapotranspiration = round(sum(daily_et0_fao_evapotranspiration[-8:]))





daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}





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
        
        self.evotranspirazione_var = tk.StringVar()
        self.evotranspirazione_var.set(f"Evotranspirazione giornaliera (Et0): {daily_evapotranspiration} mm")
        self.evotranspirazione_label = ttk.Label(self, textvariable=self.evotranspirazione_var)
        self.evotranspirazione_label.grid(column=0, row=7, sticky="w")
        
        self.evotranspirazione_settimanale_var = tk.StringVar()
        self.evotranspirazione_settimanale_var.set(f"Evotranspirazione settimanale (Et0): {weekly_evapotranspiration} mm")
        self.evotranspirazione_settimanale_label = ttk.Label(self, textvariable=self.evotranspirazione_settimanale_var)
        self.evotranspirazione_settimanale_label.grid(column=0, row=8, sticky="w")
    
        self.info_button = ttk.Button(self, text="Info", command=self.evotranspirazione_info)
        self.info_button.grid(column=1, row=8, sticky="e", padx =5)
        
        self.media_velocità_vento_var = tk.StringVar()
        self.media_velocità_vento_var.set(f"Media 24h velocità del vento: {rounded_wind_avg} Km/h")
        self.media_velocità_vento_label = ttk.Label(self, textvariable=self.media_velocità_vento_var)
        self.media_velocità_vento_label.grid(column=0, row=9, sticky="w")
        
        self.modificaColori()
        
        
    
    def evotranspirazione_info(self):
        self.info = tk.Toplevel(self)
        self.info.title("Cos'è l'Evotranspirazione?")
        self.info.geometry("1035x170")
        self.info_window = ttk.Label(self.info, text="""
        Le piante, attraverso le radici, assorbono acqua dal suolo e la trasmettono sotto forma liquida gli apparati fogliari. 
        Dal mesofillo fogliare l’acqua passa dallo stato liquido a quello di vapore, diffondendosi nell’atmosfera attraverso le aperture stomatiche. 
        Questo fenomeno si indica con il termine di traspirazione. sAllo stesso tempo il suolo perde acqua per evaporazione diretta. 
        La somma della quantità d’acqua persa dal suolo per evaporazione e dalle piante per traspirazione costituisce il fenomeno dell’evapotraspirazione. 
        In una coltura, l’evaporazione dipende anche dal grado di copertura della vegetazione presente e dalla quantità d’acqua disponibile. 
        A suolo nudo, o nelle prime fasi di sviluppo della coltura, l’evaporazione sarà più elevata rispetto a quando il terreno è coperto dalle piante.
        Inizialmente, quindi, l’evaporazione sarà la componente principale dell’evapotraspirazione, per poi progressivamente diventarne una frazione modesta.""")
                                     

        self.info_window.grid(column=0, row=0, rowspan=2)
        
    
    def modificaColori(self):
        temperatura = float(self.temperatura_var.get().split(": ")[1][:-2])
        if temperatura >= 35:
            self.temperatura_label.config(background="#fd5959")
            messagebox.showinfo("AVVISO","Attenzione, oggi ci sono temperature sopra i 35°C. Per periodi prolungati temperature così elevate possono causare danni significativi a molte colture sensibili. Questo può portare a disidratazione delle colture, arresto della fotosintesi e appassimento delle foglie. Le alte temperature riducono anche la qualità dei frutti, inducendo ustioni o danni da calore, e limitano lo sviluppo ottimale delle piante.")
        elif temperatura <= 0:
            self.temperatura_label.config(background="#248888")
            messagebox.showinfo("AVVISO", "Attenzione, oggi ci sono temperature sotto i 0°C: fare attenzione specialmente durante il periodo di fioritura e soprattutto durante la notte, possono provocare gelate che danneggiano gravemente le colture. Le gelate interrompono i processi cellulari delle piante, provocando il collasso delle pareti cellulari e, quindi, la morte dei tessuti vegetali.")
        umidità = float(self.umidità_var.get().split(": ")[1][:-2])
        if umidità >= 80:
            self.umidità_label.config(background="#248888")
            messagebox.showinfo("AVVISO","Attenzione, oggi l'umidità è elevata. Se si mantiene se prolungata crea un ambiente favorevole alla proliferazione di funghi e malattie. Le foglie e i frutti rimangono bagnati più a lungo, aumentando il rischio di infezioni fungine come la peronospora, la muffa grigia e l'oidio. Inoltre, l'umidità elevata può ostacolare la traspirazione delle piante, causando stress fisiologico.")
        elif temperatura <= 35:
            self.umidità_label.config(background="#fd5959")
            messagebox.showinfo("AVVISO", "Attenzione, oggi l'umidità è bassa. Il tasso di umidità scarso comporta una maggiore traspirazione delle piante, provocando un eccesso di evaporazione e disidratazione, soprattutto in giornate ventose e calde. Le colture diventano più suscettibili allo stress idrico e possono mostrare segni di appassimento anche con irrigazione adeguata.")
        vento = float(self.velocità_vento_var.get().split()[3])
        if vento >= 30:
            self.velocità_vento_label.config(background="#fd5959")
            messagebox.showinfo("AVVISO","Il vento forte, soprattutto oltre i 30 km/h, può causare danni meccanici alle piante, in particolare a quelle più alte e fragili come i cereali. Può provocare la caduta dei frutti dagli alberi o danneggiare le strutture di supporto (come i tralicci). A velocità ancora maggiori, il vento può strappare foglie e steli e abbattere interi campi di colture.")
        raffica_vento = float(self.raffica_vento_var.get().split()[4])
        if vento >= 60:
            self.raffica_vento_label.config(background="#fd5959")
            
            
        


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

style.theme_use("classic")

root.mainloop()