#!/usr/bin/env python
# coding: utf-8

# # Introduction to GeoPandas 

# In[1]:


import geopandas as gpd 
import matplotlib.pyplot as plt 
import warnings
warnings.simplefilter("ignore")


# ## Read Shape Files into GeoPandas 

# In[2]:


# read file 
data = gpd.read_file(r'../shapefiles/districts.shp')


# In[3]:


# show data 
data   


# In[4]:


# type of dataframe 
type(data)


# In[5]:


# plot the map 
data.plot() 


# In[6]:


# color 
data.plot(color = "red")


# In[7]:


# edge color 
data.plot(color = "red", edgecolor='black')


# In[13]:


# cmap: https://matplotlib.org/2.0.2/users/colormaps.html
data.plot(color = "red", edgecolor='black', cmap='jet')


# In[9]:


# color by column 
data.plot(color = "red", edgecolor = 'black', cmap= 'jet', column = 'districts')


# In[15]:


# read area of interest 
area_of_interest = gpd.read_file(r'../shapefiles/area_of_interest.shp')


# In[16]:


area_of_interest.plot() 


# In[17]:


# Plot the figure side by side 
fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(10,8)) 
data.plot(ax = ax1, color = "red", edgecolor = 'black', cmap= 'jet', column = 'districts')
area_of_interest.plot(ax = ax2, color='green')


# In[21]:


# Plot the figure side by side 
fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(10,8)) 
data.plot(ax = ax1, color = "red", edgecolor = 'black', cmap= 'jet', column = 'districts')
area_of_interest.plot(ax = ax2, color='green')
plt.axis('off')
plt.show() 


# In[35]:


# Plotting multiple layers: area of interest 
fig, ax = plt.subplots(figsize=(10,6)) 
data.plot(ax = ax, color = "red", edgecolor = 'black', cmap= 'jet', column = 'districts')
area_of_interest.plot(ax = ax, color='green')


# In[36]:


# Plotting multiple layers: area of interest 
fig, ax = plt.subplots(figsize=(10,6)) 
data.plot(ax = ax, color = "red", edgecolor = 'black', cmap= 'jet', column = 'districts')
area_of_interest.plot(ax = ax, color='none', edgecolor = 'black')


# In[37]:


atms = gpd.read_file(r"../shapefiles/atms.shp")


# In[42]:


# Plotting multiple layers: area of interest 
fig, ax = plt.subplots(figsize=(10,6)) 
data.plot(ax = ax, color = "red", edgecolor = 'black', cmap= 'jet', column = 'districts')
area_of_interest.plot(ax = ax, color='none', edgecolor = 'black')
atms.plot(ax = ax, color = "black", markersize = 16)


# In[43]:


data.crs


# In[44]:


area_of_interest.crs


# In[45]:


atms.crs 


# In[53]:


# Reprojecting: coordinate reference system 
districs = data.to_crs(epsg = 32629)
area_of_interest = area_of_interest.to_crs(epsg = 32629)


# In[47]:


districs.crs   


# In[49]:


districs.plot(figsize = (10,6)) 


# In[54]:


# overlays 
df = gpd.overlay(districs, area_of_interest, how="intersection")


# In[58]:


df.plot(edgecolor = "red", figsize = (10,8)) 

