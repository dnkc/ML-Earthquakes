from django.contrib import admin
from datetime import datetime
import pandas as pd
from quakesapp.models import Quake


# Register your models here.
admin.site.register(Quake)


if Quake.objects.all().count() == 0:
    print("READING & LOADING DATA INTO POSTGRES...")
    # Add the 1965 - 2016 earthquakes dataset
    df = pd.read_csv(r'D:\Program\Machine Learning-GIS\Earthquakes\quakes\database.csv')

    # preview df
    #print(df.head())

    df_load = df.drop(['Depth Error', 'Time', 'Depth Seismic Stations', 'Magnitude Error', 
    'Magnitude Seismic Stations', 'Azimuthal Gap', 'Horizontal Distance', 'Horizontal Error', 
    'Root Mean Square', 'Source', 'Location Source', 'Magnitude Source', 'Status'], axis=1)

    # preview df_load
    #print(df_load.head())

    df_load = df_load.rename(columns={"Magnitude Type": "Magnitude_Type"})

    # Preview df_load
    #print(df_load.head())
    
    # Insert the records into the quake model/table
    for index, row in df_load.iterrows():
        Date = row['Date']
        Latitude = row['Latitude']
        Longitude = row['Longitude']
        Type = row['Type']
        Depth = row['Depth']
        Magnitude = row['Magnitude']
        Magnitude_Type = row['Magnitude_Type']
        ID = row['ID']

        Quake(Date=Date, Latitude=Latitude, Longitude=Longitude, Type=Type, Depth=Depth, Magnitude=Magnitude, Magnitude_Type=Magnitude_Type, ID=ID).save()
        print("LOADING COMPLETE...")