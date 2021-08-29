#!/usr/bin/env python
# coding: utf-8

# # Coordinate reference systems

# In[3]:


get_ipython().run_line_magic('matplotlib', 'inline')
import pandas as pd
import geopandas


# In[4]:


countries = geopandas.read_file("zip://./data/ne_110m_admin_0_countries.zip")
cities = geopandas.read_file("zip://./data/ne_110m_populated_places.zip")
rivers = geopandas.read_file("zip://./data/ne_50m_rivers_lake_centerlines.zip")


# ## Coordinate reference systems
# 
# Up to now, we have used the geometry data with certain coordinates without further wondering what those coordinates mean or how they are expressed.
# 
# > The **Coordinate Reference System (CRS)** relates the coordinates to a specific location on earth.
# 
# For a nice in-depth explanation, see https://docs.qgis.org/2.8/en/docs/gentle_gis_introduction/coordinate_reference_systems.html

# ### Geographic coordinates
# 
# > Degrees of latitude and longitude.
# >
# > E.g. 48°51′N, 2°17′E
# 
# The most known type of coordinates are geographic coordinates: we define a position on the globe in degrees of latitude and longitude, relative to the equator and the prime meridian. 
# With this system, we can easily specify any location on earth. It is used widely, for example in GPS. If you inspect the coordinates of a location in Google Maps, you will also see latitude and longitude.
# 
# **Attention!**
# 
# in Python we use (lon, lat) and not (lat, lon)
# 
# - Longitude: [-180, 180]{{1}}
# - Latitude: [-90, 90]{{1}}

# ### Projected coordinates
# 
# > `(x, y)` coordinates are usually in meters or feet
# 
# Although the earth is a globe, in practice we usually represent it on a flat surface: think about a physical map, or the figures we have made with Python on our computer screen.
# Going from the globe to a flat map is what we call a *projection*.
# 
# ![](img/projection.png)
# 
# We project the surface of the earth onto a 2D plane so we can express locations in cartesian x and y coordinates, on a flat surface. In this plane, we then typically work with a length unit such as meters instead of degrees, which makes the analysis more convenient and effective.
# 
# However, there is an important remark: the 3 dimensional earth can never be represented perfectly on a 2 dimensional map, so projections inevitably introduce distortions. To minimise such errors, there are different approaches to project, each with specific advantages and disadvantages.
# 
# Some projection systems will try to preserve the area size of geometries, such as the Albers Equal Area projection. Other projection systems try to preserve angles, such as the Mercator projection, but will see big distortions in the area. Every projection system will always have some distortion of area, angle or distance.
# 
# <table><tr>
# <td> <img src="img/projections-AlbersEqualArea.png"/> </td>
# <td> <img src="img/projections-Mercator.png"/> </td>
# </tr>
# <tr>
# <td> <img src="img/projections-Robinson.png"/> </td>
# </tr></table>

# **Projected size vs actual size (Mercator projection)**:
# 
# ![](img/mercator_projection_area.gif)

# ## Coordinate Reference Systems in Python / GeoPandas

# A GeoDataFrame or GeoSeries has a `.crs` attribute which holds (optionally) a description of the coordinate reference system of the geometries:

# In[ ]:


countries.crs


# For the `countries` dataframe, it indicates that it uses the EPSG 4326 / WGS84 lon/lat reference system, which is one of the most used for geographic coordinates.
# 
# 
# It uses coordinates as latitude and longitude in degrees, as can you be seen from the x/y labels on the plot:

# In[ ]:


countries.plot()


# The `.crs` attribute is given as a dictionary. In this case, it only indicates the EPSG code, but it can also contain the full "proj4" string (in dictionary form).
# 
# Possible CRS representation:
# 
# - **`proj4` string**  
#   
#   Example: `+proj=longlat +datum=WGS84 +no_defs`
# 
#   Or its dict representation: `{'proj': 'longlat', 'datum': 'WGS84', 'no_defs': True}`
# 
# - **EPSG code**
#   
#   Example: `EPSG:4326` = WGS84 geographic CRS (longitude, latitude)
#   
# - Well-Know-Text (WKT) representation (better support coming with PROJ6 in the next GeoPandas version)
# 
# See eg https://epsg.io/4326
# 
# Under the hood, GeoPandas uses the `pyproj` / `PROJ` libraries to deal with the re-projections.
# 
# For more information, see also http://geopandas.readthedocs.io/en/latest/projections.html.

# ### Transforming to another CRS
# 
# We can convert a GeoDataFrame to another reference system using the `to_crs` function. 
# 
# For example, let's convert the countries to the World Mercator projection (http://epsg.io/3395):

# In[ ]:


# remove Antartica, as the Mercator projection cannot deal with the poles
countries = countries[(countries['name'] != "Antarctica")]


# In[ ]:


countries_mercator = countries.to_crs(epsg=3395)  # or .to_crs({'init': 'epsg:3395'})


# In[ ]:


countries_mercator.plot()


# Note the different scale of x and y.

# ### Why using a different CRS?
# 
# There are sometimes good reasons you want to change the coordinate references system of your dataset, for example:
# 
# - Different sources with different CRS -> need to convert to the same crs
# 
#     ```python
#     df1 = geopandas.read_file(...)
#     df2 = geopandas.read_file(...)
# 
#     df2 = df2.to_crs(df1.crs)
#     ```
# 
# - Mapping (distortion of shape and distances)
# 
# - Distance / area based calculations -> ensure you use an appropriate projected coordinate system expressed in a meaningful unit such as metres or feet (not degrees).
# 
# <div class="alert alert-info" style="font-size:120%">
# 
# **ATTENTION:**
# 
# All the calculations that happen in geopandas and shapely assume that your data is in a 2D cartesian plane, and thus the result of those calculations will only be correct if your data is properly projected.
# 
# </div>

# ## Let's practice!
# 
# Again, we will go back to the Paris datasets. Up to now, we provided the datasets in an appropriate projected CRS for the exercises. But the original data actually were geographic coordinates. In the following exercises, we will start from there.
# 
# ---

# Going back to the Paris districts dataset, this is now provided as a GeoJSON file (`"data/paris_districts.geojson"`) in geographic coordinates.
# 
# For converting to projected coordinates, we will use the standard projected CRS for France is the RGF93 / Lambert-93 reference system, referenced by the `EPSG:2154` number (in Belgium this would be Lambert 72, EPSG:31370).
# 
# <div class="alert alert-success">
# 
# **EXERCISE: Projecting a GeoDataFrame**
# 
# * Read the districts datasets (`"data/paris_districts.geojson"`) into a GeoDataFrame called `districts`.
# * Look at the CRS attribute of the GeoDataFrame. Do you recognize the EPSG number?
# * Make a simple plot of the `districts` dataset.
# * Calculate the area of all districts.
# * Convert the `districts` to a projected CRS (using the `EPSG:2154` for France). Call the new dataset `districts_RGF93`.
# * Make a similar plot of `districts_RGF93`.
# * Calculate the area of all districts again with `districts_RGF93` (the result will now be expressed in m²).
#     
#     
# <details><summary>Hints</summary>
# 
# * The CRS information is stored in the `crs` attribute of a GeoDataFrame.
# * Making a simple plot of a GeoDataFrame can be done with the `.plot()` method.
# * Converting to a different CRS can be done with the `to_crs()` method, and the CRS can be specified as an EPSG number using the `epsg` keyword.
# 
# </details>
# 
# </div>

# In[ ]:


# %load _solved/solutions/02-coordinate-reference-systems1.py


# In[ ]:


# %load _solved/solutions/02-coordinate-reference-systems2.py


# In[ ]:


# %load _solved/solutions/02-coordinate-reference-systems3.py


# In[ ]:


# %load _solved/solutions/02-coordinate-reference-systems4.py


# In[ ]:


# %load _solved/solutions/02-coordinate-reference-systems5.py


# In[ ]:


# %load _solved/solutions/02-coordinate-reference-systems6.py


# In[ ]:


# %load _solved/solutions/02-coordinate-reference-systems7.py


# In[ ]:


# %load _solved/solutions/02-coordinate-reference-systems8.py


# <div class="alert alert-success">
# 
# **EXERCISE:**
# 
# In the first notebook, we did an exercise on plotting the bike stations locations in Paris and adding a background map to it using the `contextily` package.
# 
# Currently, `contextily` assumes that your data is in the Web Mercator projection, the system used by most web tile services. And in that first exercise, we provided the data in the appropriate CRS so you didn't need to care about this aspect.
# 
# However, typically, your data will not come in Web Mercator (`EPSG:3857`) and you will have to align them with web tiles on your own.
#     
# * Read the bike stations datasets (`"data/paris_bike_stations.geojson"`) into a GeoDataFrame called `stations`.
# * Convert the `stations` dataset to the Web Mercator projection (`EPSG:3857`). Call the result `stations_webmercator`, and inspect the result.
# * Make a plot of this projected dataset (specify the marker size to be 5) and add a background map using `contextily`.
# 
#     
# <details><summary>Hints</summary>
# 
# * Making a simple plot of a GeoDataFrame can be done with the `.plot()` method. This returns a matplotlib axes object.
# * The marker size can be specified with the `markersize` keyword if the `plot()` method.
# * To add a background map, use the `contextily.add_basemap()` function. It takes the matplotlib `ax` to which to add a map as the first argument.
# 
# </details>
# 
# </div>

# In[ ]:


# %load _solved/solutions/02-coordinate-reference-systems9.py


# In[ ]:


# %load _solved/solutions/02-coordinate-reference-systems10.py


# In[ ]:


# %load _solved/solutions/02-coordinate-reference-systems11.py

