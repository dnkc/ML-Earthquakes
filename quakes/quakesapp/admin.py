from django.contrib import admin
from datetime import datetime
import pandas as pd
from quakesapp.models import Quake, Quake_Predictions
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV

# Register your models here.
admin.site.register(Quake)
admin.site.register(Quake_Predictions)

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

if Quake_Predictions.objects.all().count() == 0:
    # Add the 2017 test data and the 1965-2016 training data
    df_test = pd.read_csv(r'D:\Program\Machine Learning-GIS\Earthquakes\quakes\earthquakeTest.csv')
    df_train = pd.read_csv(r'D:\Program\Machine Learning-GIS\Earthquakes\quakes\database.csv')

    df_train_load = df_train.drop(['Depth Error', 'Time', 'Depth Seismic Stations', 'Magnitude Error', 
    'Magnitude Seismic Stations', 'Azimuthal Gap', 'Horizontal Distance', 'Horizontal Error', 
    'Root Mean Square', 'Source', 'Location Source', 'Magnitude Source', 'Status'], axis=1)

    df_test_load = df_test[['time', 'latitude', 'longitude', 'mag', 'depth']]

    df_train_load = df_train_load.rename(columns={'Magnitude Type': 'Magnitude_Type'})

    df_test_load = df_test_load.rename(columns={'time':'Date', 
                                                'latitude':'Latitude',
                                                'longitude':'Longitude', 
                                                'mag':'Magnitude', 
                                                'depth':'Depth'})
    
    # Create training and test data frames
    df_testing = df_test_load[['Latitude', 'Longitude', 'Magnitude', 'Depth']]
    df_training = df_train_load[['Latitude', 'Longitude', 'Magnitude', 'Depth']]

    # Drop null fields from data to prevent future problems
    df_training.dropna()
    df_testing.dropna()

    X = df_training[['Latitude', 'Longitude']]
    y = df_training[['Magnitude', 'Depth']]

    X_new = df_testing[['Latitude', 'Longitude']]
    y_new = df_testing[['Magnitude', 'Depth']]


    # Use train_test_split on training data features
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=42)
    
    # Build the model
    model_reg = RandomForestRegressor(random_state=50)
    # Fit it on our training data
    model_reg.fit(X_train, y_train)

    # Use train model to predict y_test using X_test
    model_reg.predict(X_test)

    # Improve model accuracy by automating hyperparameter tuning
    parameters = {'n_estimators': [10, 20, 50, 100, 200, 500]}
    # Create grid search CV model
    grid_obj = GridSearchCV(model_reg, parameters)
    # train the model using the training data
    grid_fit = grid_obj.fit(X_train, y_train)
    # select the best fit model
    best_fit = grid_fit.best_estimator_
    # use the best fit model to make the prediction on our training test data
    results = best_fit.predict(X_test)

    #score = best_fit.score(X_test, y_test)*100
    #print(score)
    # Make prediction on out of sample data (Earthquakes for next year - 2017)
    final_results = best_fit.predict(X_new)
    final_score = best_fit.score(X_new, y_new) * 100

    lst_Magnitudes = []
    lst_Depth = []
    i = 0
    for r in final_results.tolist():
        lst_Magnitudes.append(final_results[i][0])
        lst_Depth.append(final_results[i][1])
        i += 1
    df_results = X_new[['Latitude', 'Longitude']]
    df_results['Magnitude'] = lst_Magnitudes
    df_results['Depth'] = lst_Depth
    df_results['Score'] = final_score

    # Store the predicted results in the postgres database
    for index, row in df_results.iterrows():
        Latitude = row['Latitude']
        Longitude = row['Longitude']
        Magnitude = row['Magnitude']
        Depth = row['Depth']
        Score = row['Score']

        Quake_Predictions(Latitude=Latitude, Longitude=Longitude, Magnitude=Magnitude, Depth=Depth, Score=Score).save()