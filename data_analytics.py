import pandas as pd
import matplotlib.pyplot as plt
import folium
import json


# top 10 entities with maximum number of total vaccinations per hundred
df = pd.read_csv('csvs\covid-vaccination-doses-per-capita.csv')
df = df.rename(columns={'Day': 'Date'})
df.set_index(df.Date, inplace=True)
df.drop(['Date'], axis=1, inplace=True)
covid_c = df.groupby(['Entity'])['total_vaccinations_per_hundred'].sum()
print(covid_c.nlargest(10))
# visualizing through bar chart
ax = covid_c.nlargest(10).plot.bar(rot=20, color=["powderblue", "cadetblue"])
plt.ylabel('total vaccinations per hundred')
plt.title('Top 10 entities with max total vaccinations')
plt.show()

# maximum values of total number of cases and deaths by country
df = pd.read_csv('csvs\cases_deaths.csv')
# i need only three columns without NaN values
temp = df[['Country', 'Total confirmed deaths due to COVID-19',
           'Total confirmed cases of COVID-19']].dropna()
# or I can fill NaNs with mean value of a particular country
# for key, group in cases_deaths:
#     print(key)
#     group.Cases.fillna(group.Cases.mean(), inplace=True)
#     group.Deaths.fillna(group.Deaths.mean(), inplace=True)
#     print(group.head())
temp.columns = ['Country', 'Cases', 'Deaths']
cases_deaths = pd.DataFrame()
cases_deaths['Cases'] = temp.groupby('Country').Cases.max()
cases_deaths['Deaths'] = temp.groupby('Country').Deaths.max()
cases_deaths = cases_deaths.nlargest(10, ['Cases', 'Deaths'])
# since deaths drastically exceed cases i divide them by a 100.
cases_deaths['Deaths'] = cases_deaths['Deaths'] // 100
print(cases_deaths)
# creating a bar chart with two bars for each country
cases_deaths.plot.bar(rot=10, color=["lightpink", "lightblue"])
plt.ylabel('Cases and Deaths (divided by a 100)')
plt.title('Total number of cases and deaths by country')
plt.show()

# top 10 entities with the largest number of deaths during covid
df = pd.read_csv('csvs\daily-covid-deaths-region.csv')
df = df.rename(columns={'Day': 'Date',
                        'Daily new confirmed deaths due to COVID-19 '
                        '(rolling 7-day average, right-aligned)': 'Deaths'})
df.set_index(df.Date, inplace=True)
df.drop(['Date'], axis=1, inplace=True)
df = df.groupby(['Code'])["Deaths"].sum()
print(df.nlargest(10))
# visualizing through bar chart
ax = df.nlargest(10).plot.bar(rot=0, color=["gold", "khaki"])
plt.ylabel('deaths during covid')
plt.xlabel('entities (their codes)')
plt.title('Top 10 entities with max deaths')
plt.show()

# maximum number of school closures in different countries
df = pd.read_csv('csvs\school-closures-covid.csv')
df['Date'] = pd.to_datetime(df.Day)
df.set_index(df.Date, inplace=True)
df.drop(['Date'], axis=1, inplace=True)
temp = pd.DataFrame()
temp['school_closures'] = df.groupby('Entity')['school_closures'].max()
print(temp)
# folium map
center = [35.762887375145795, 84.08313219586536]
m = folium.Map(location=center, zoom_start=2, max_bounds=True,
               min_zoom=1, min_lat=-84,
               max_lat=84, min_lon=-175, max_lon=187,
               )
geo_path = "csvs/World_Countries_(Generalized).geojson"
json_data = json.load(open(geo_path))
# according to our map, in most countries
# there were 3 school closures at most
folium.Choropleth(geo_data=json_data,
                  data=temp,
                  columns=(temp.index, 'school_closures'),
                  key_on='properties.COUNTRY',
                  fill_color='RdYlGn',
                  fill_opacity=0.7,
                  line_opacity=0.5,
                  ).add_to(m)
folium.LayerControl().add_to(m)
m.save("school_closures.html")

# the latest available data about the current number of patients
# hospitalized in different countries due to covid
df = pd.read_csv('csvs/current-covid-patients-hospital.csv')
df = df.groupby('Entity')
marker_map = folium.Map(location=[35.762887375145795, 84.08313219586536],
                        zoom_start=2, tiles='openstreetmap')
# json with latitude and longitude of all countries
geo_path = "csvs/countries-lat-long.json"
json_data = json.load(open(geo_path))
geo_data = pd.DataFrame(columns=['country', 'latitude', 'longitude'])
for country in df.Entity:
    # find location for each country in the csv
    temp = [[tag['country'], tag['latitude'], tag['longitude']]
            for tag in json_data['ref_country_codes'] if country[0] in tag['country']]
    if len(temp) > 0:
        geo_data.loc[len(geo_data)] = temp[0]
for key, group in df:
    if len(geo_data[geo_data.country == key]) > 0:
        # marking each country with its location on the map
        # as a popup I display country name and its current hospital occupancy
        folium.Marker(location=[geo_data[geo_data.country == key].latitude.values[0],
                                geo_data[geo_data.country == key].longitude.values[0]],
                      popup=f"{key}  hospital occupancy: "
                            f"{group.tail(1)['Daily hospital occupancy'].values[0]}",
                      icon=folium.Icon(Icon='cloud'),
                      ).add_to(marker_map)
marker_map.save("hospital_occupancy.html")
