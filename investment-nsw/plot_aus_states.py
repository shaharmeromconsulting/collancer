# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 10:02:30 2021

@author: merom
"""

import geopandas as gpd
import matplotlib.pyplot as plt
#%%
display(aus.STE_NAME21.unique())
#%%
aus = gpd.read_file(r'C:\Users\merom\Documents\Collancer\Projects\2 Provider Choice\scripts\GCCSA\GCCSA_2021_AUST_GDA2020.shp')
fig = plt.figure(figsize = (25,25))
ax = fig.add_axes([0,0,1,1])
#plt.xlim(113,154)
#plt.ylim(-44,-10)
ax.axis('off')
aus.loc[aus.STE_NAME21=='Victoria'].plot(color = '#002664',edgecolor = '#002664', ax=ax)
plt.savefig(r'C:\Users\merom\OneDrive - Shahar Merom consulting\16 NSW Government\01 NSW Funding Review\02 Data\Images\Victoria.png',
            transparent=True,bbox_inches="tight",pad_inches = 0)


#%%
aus = gpd.read_file(r'C:\Users\merom\Documents\Collancer\Projects\2 Provider Choice\scripts\GCCSA\GCCSA_2021_AUST_GDA2020.shp')
fig = plt.figure(figsize = (25,25))
ax = fig.add_axes([0,0,1,1])
#plt.xlim(113,154)
#plt.ylim(-44,-10)
ax.axis('off')
aus.loc[aus.STE_NAME21=='Queensland'].plot(color = '#002664',edgecolor = '#002664', ax=ax)
plt.savefig(r'C:\Users\merom\OneDrive - Shahar Merom consulting\16 NSW Government\01 NSW Funding Review\02 Data\Images\Queensland.png',
            transparent=True,bbox_inches="tight",pad_inches = 0)
#%%
aus = gpd.read_file(r'C:\Users\merom\Documents\Collancer\Projects\2 Provider Choice\scripts\GCCSA\GCCSA_2021_AUST_GDA2020.shp')
fig = plt.figure(figsize = (25,25))
ax = fig.add_axes([0,0,1,1])
#plt.xlim(113,154)
#plt.ylim(-44,-10)
ax.axis('off')
aus.loc[aus.STE_NAME21=='New South Wales'].plot(color = '#002664',edgecolor = '#002664', ax=ax)
plt.savefig(r'C:\Users\merom\OneDrive - Shahar Merom consulting\16 NSW Government\01 NSW Funding Review\02 Data\Images\NSW.png',
            transparent=True,bbox_inches="tight",pad_inches = 0)
#%%
aus = gpd.read_file(r'C:\Users\merom\Documents\Collancer\Projects\2 Provider Choice\scripts\GCCSA\GCCSA_2021_AUST_GDA2020.shp')
fig = plt.figure(figsize = (25,25))
ax = fig.add_axes([0,0,1,1])
#plt.xlim(113,154)
#plt.ylim(-44,-10)
ax.axis('off')
aus.loc[aus.STE_NAME21.isin(['Other Territories','Outside Australia'])==False,:].plot(color = '#002664',edgecolor = '#002664', ax=ax)
plt.savefig(r'C:\Users\merom\OneDrive - Shahar Merom consulting\16 NSW Government\01 NSW Funding Review\02 Data\Images\AUS.png',
            transparent=True,bbox_inches="tight",pad_inches = 0)