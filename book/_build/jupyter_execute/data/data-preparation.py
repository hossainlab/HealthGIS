#!/usr/bin/env python
# coding: utf-8

# # Data preparation for tutorial
# 
# This notebook contains the code to convert raw downloaded external data into a cleaned or simplified version for tutorial purposes.
# 
# 
# The raw data is expected to be in the `./raw` sub-directory (not included in the git repo).

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')

import pandas as pd
import geopandas


# ## Countries dataset
# 
# http://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/

# In[2]:


countries = geopandas.read_file("zip://./raw/original_data_ne/ne_110m_admin_0_countries.zip")


# In[3]:


countries.head()


# In[4]:


len(countries)


# In[5]:


countries_subset = countries[['ADM0_A3', 'NAME', 'CONTINENT', 'POP_EST', 'GDP_MD_EST', 'geometry']]


# In[6]:


countries_subset.columns = countries_subset.columns.str.lower()


# In[7]:


countries_subset = countries_subset.rename(columns={'adm0_a3': 'iso_a3'})


# In[8]:


countries_subset.head()


# In[9]:


countries_subset.to_file("ne_110m_admin_0_countries.shp")


# ## Natural Earth - Cities dataset
# 
# http://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-populated-places/ (simple, version 4.0.0, downloaded May 2018)

# In[10]:


cities = geopandas.read_file("zip://./raw/original_data_ne/ne_110m_populated_places_simple.zip")


# In[11]:


cities.head()


# In[12]:


len(cities)


# In[13]:


cities_subset = cities[['name', 'geometry']]


# In[14]:


cities_subset.head()


# In[15]:


cities_subset.to_file("ne_110m_populated_places.shp")


# ## Natural Earth - Rivers dataset
# 
# http://www.naturalearthdata.com/downloads/50m-physical-vectors/50m-rivers-lake-centerlines/ (version 4.0.0, downloaded May 2018)

# In[16]:


rivers = geopandas.read_file("zip://./raw/ne_50m_rivers_lake_centerlines.zip")


# In[17]:


rivers.head()


# Remove rows with missing geometry:

# In[18]:


len(rivers)


# In[19]:


rivers = rivers[~rivers.geometry.isna()].reset_index(drop=True)


# In[20]:


len(rivers)


# Subset of the columns:

# In[21]:


rivers_subset = rivers[['featurecla', 'name_en', 'geometry']].rename(columns={'name_en': 'name'})


# In[22]:


rivers_subset.head()


# In[23]:


rivers_subset.to_file("ne_50m_rivers_lake_centerlines.shp")


# In[ ]:





# ## Paris districts

# Source: https://opendata.paris.fr/explore/dataset/quartier_paris/ (downloaded as GeoJSON file on August 20, 2018)
# 
# Administrative districts, polygon dataset

# In[2]:


districts = geopandas.read_file("./raw/quartier_paris.geojson")


# In[3]:


districts.head()


# In[4]:


districts = districts.rename(columns={'l_qu': 'district_name', 'c_qu': 'id'}).sort_values('id').reset_index(drop=True)


# Add population data (based on pdfs downloaded from ..):
import camelot

import glob
files = glob.glob("../../Downloads/A_*.pdf")


results = []

for fname in files:
    print(fname)
    tables = camelot.read_pdf(fname, pages='17-end', flavor='stream')

    for t in tables:

        df = t.df
        if df.loc[0, 0] == "1.  SUPERFICIES ET DENSITÉS EN 1999":
            district_name = df.loc[2, 0]
            assert df.loc[10, 0] == 'POPULATION TOTALE EN 1999'
            population = df.loc[10, 1]
            print(t.page)
            print(district_name)
            results.append([district_name, population])

df = pd.DataFrame(results, columns=['district_name', 'population'])                                                                                                   
df['population'] = df['population'].str.replace(' ', '').astype('int64')                                                                                              
df.to_csv("datasets/paris-population.csv", index=False)   
# In[5]:


population = pd.read_csv("./raw/paris-population.csv")


# In[6]:


population['temp'] = population.district_name.str.lower()


# In[7]:


population['temp'] = population['temp'].replace({
    'javel': 'javel 15art',
    'saint avoye': 'sainte avoie',
    "saint germain l'auxerrois": "st germain l'auxerrois",
    'plaine monceau': 'plaine de monceaux',
    'la   chapelle': 'la chapelle'})


# In[8]:


districts['temp'] = (districts.district_name.str.lower().str.replace('-', ' ')
                              .str.replace('é', 'e').str.replace('è', 'e').str.replace('ê', 'e').str.replace('ô', 'o'))


# In[9]:


res = pd.merge(districts, population[['population', 'temp']], on='temp', how='outer')


# In[10]:


assert len(res) == len(districts)


# In[11]:


districts = res[['id', 'district_name', 'population', 'geometry']]


# In[12]:


districts.head()


# In[13]:


districts.to_file("processed/paris_districts.geojson", driver='GeoJSON')


# In[14]:


districts = districts.to_crs(epsg=32631)


# In[15]:


districts.to_file("paris_districts_utm.geojson", driver='GeoJSON')


# ## Commerces de Paris

# Source: https://opendata.paris.fr/explore/dataset/commercesparis/ (downloaded as csv file (`commercesparis.csv`) on October 30, 2018)

# In[2]:


df = pd.read_csv("./raw/commercesparis.csv", sep=';')


# In[3]:


df.iloc[0]


# Take subset of the restaurants:

# In[4]:


restaurants = df[df['CODE ACTIVITE'].str.startswith('CH1', na=False)].copy()


# In[5]:


restaurants['LIBELLE ACTIVITE'].value_counts()


# In[6]:


restaurants = restaurants.dropna(subset=['XY']).reset_index(drop=True)


# Translate the restaurants and rename column:

# In[7]:


restaurants['LIBELLE ACTIVITE'] = restaurants['LIBELLE ACTIVITE'].replace({
    'Restaurant traditionnel français': 'Traditional French restaurant',
    'Restaurant asiatique': 'Asian restaurant',
    'Restaurant européen': 'European restuarant',
    'Restaurant indien, pakistanais et Moyen Orient': 'Indian / Middle Eastern restaurant',
    'Restaurant maghrébin': 'Maghrebian restaurant',
    'Restaurant africain': 'African restaurant',
    'Autre restaurant du monde': 'Other world restaurant',
    'Restaurant central et sud américain': 'Central and South American restuarant',
    'Restaurant antillais': 'Caribbean restaurant'
})


# In[8]:


restaurants = restaurants.rename(columns={'LIBELLE ACTIVITE': 'type'})


# Create GeoDataFrame

# In[9]:


from shapely.geometry import Point


# In[10]:


restaurants['geometry'] = restaurants['XY'].str.split(', ').map(lambda x: Point(float(x[1]), float(x[0])))


# In[11]:


restaurants = geopandas.GeoDataFrame(restaurants[['type', 'geometry']], crs={'init': 'epsg:4326'})


# In[12]:


restaurants.head()


# In[13]:


restaurants.to_file("processed/paris_restaurants.gpkg", driver='GPKG')


# In[ ]:




