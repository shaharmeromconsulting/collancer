import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
world = gpd.read_file('C:/Users/merom/Documents/GitHub/collancer/investment-nsw/input/world-administrative-boundaries.shp')
world = world[['name','geometry']]
world = world.loc[(world.name=='New Zealand'),:]

states = gpd.read_file('C:/Users/merom/Documents/GitHub/collancer/investment-nsw/input/STE_2021_AUST_GDA2020.shp')
states = states[['STE_NAME21','geometry']]

plot_data = pd.concat([world.to_crs(crs=4326),states.to_crs(crs=4326)],axis=0)
#========================================================================
# # Australia NZ plot
#========================================================================
fig, ax = plt.subplots(figsize=(30,18))
plot_data.plot(edgecolor='white',facecolor='#002664',linewidth=4, ax=ax)

# Remove axes
ax.axis('off')

# Set x/y limits and aspect ratio
ax.set_xlim(100, 185)  
ax.set_ylim(-85, 0)  
ax.set_aspect('equal')   

# Save the plot as JPG with transparent background
fig.savefig('C:/Users/merom/Documents/GitHub/collancer/investment-nsw/output/australia-nz.png',
dpi=300, transparent=True)
