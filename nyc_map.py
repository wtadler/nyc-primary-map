import pandas as pd
import geopandas as gpd
import folium
import matplotlib.cm as cm

cuomo = 'ANDREW M. CUOMO'
nixon = 'CYNTHIA E. NIXON'
frac = 'cuomo_over_cuomo_plus_nixon'

def rgb_to_hex(rgb):
    f = lambda x: int(x*255)
    return '#%02X%02X%02X' % (f(rgb[0]), f(rgb[1]), f(rgb[2]))

colormap = lambda x: rgb_to_hex(cm.BrBG(x))

df = pd.read_csv('20180913__ny__primary__nyc__precinct.csv')

gdf = gpd.read_file('shapefile/nyed.shp')

df['ElectDist'] = df['assembly district'].astype(str) + df['election district'].apply(lambda x: str(x).zfill(3))

gov = df.pivot_table(index='ElectDist', columns='candidate', values='votes', aggfunc=sum)[[cuomo, nixon]].astype(int)
gov[frac] = gov[cuomo] / (gov[cuomo] + gov[nixon])

gdf['ElectDist'] = gdf['ElectDist'].astype(str)
gdf = gdf.merge(gov, on='ElectDist')

gdf['readable_dist'] = gdf['ElectDist'].apply(lambda x: x[:2] + '/' + x[2:])

bounds = [[40.477, -74.259], [40.918, -73.7]]
m = folium.Map(control_scale=True, min_lat=bounds[0][0], max_lat=bounds[1][0], min_lon=bounds[0][1], max_lon=bounds[1][1], max_bounds=True)


def style_function(x):
    default_color = '#fff'
    if frac not in x['properties']:
        color = default_color
    else:
        if x['properties'][frac] is None:
            color = default_color
        else:
            color = colormap(x['properties'][frac])

    return {'fillColor': color,
            'fillOpacity': 0.8,
            'weight': .5,
            'color': '#888'}

tooltip = folium.features.GeoJsonTooltip(['readable_dist', cuomo, nixon],
                                         aliases=['Assembly/Election district', 'Cuomo votes', 'Nixon votes'])

folium.features.GeoJson(gdf,
                        style_function=style_function,
                        tooltip=tooltip).add_to(m)
folium.map.FitBounds(bounds).add_to(m)

info_box = f'''

<div style="position: fixed; top: 10px; left: 60px; border: 0px; z-index: 9999; font-size: 13px; border-radius: 5px; background-color: #fff; padding: 8px; box-shadow: 0px 2px 4px #888; opacity: 0.85; overflow: auto; white-space: nowrap;">
     <style>
/* basic positioning */

.legend {{
  list-style: none;
  padding-left: 0;
}}

.legend li {{
  float: left;
  margin-right: 2px;
}}

.legend span {{
  border: 1px solid #ccc;
  float: left;
  width: 12px;
  height: 12px;
  margin: 2px;
}}

/* your colors */

.legend .choro1 {{
  background-color: {colormap(0)};
}}

.legend .choro2 {{
  background-color: {colormap(.25)};
}}

.legend .choro3 {{
  background-color: {colormap(0.5)};
}}

.legend .choro4 {{
  background-color: {colormap(0.75)};
}}

.legend .choro5 {{
  background-color: {colormap(1)};
}}

</style>

<ul class="legend">
  <li><span class="choro1"></span>0% Cuomo, 100% Nixon</li><br>
  <li><span class="choro2"></span>25% Cuomo, 75% Nixon</li><br>
  <li><span class="choro3"></span>50% Cuomo, 50% Nixon</li><br>
  <li><span class="choro4"></span>75% Cuomo, 75% Nixon</li><br>
  <li><span class="choro5"></span>100% Cuomo, 0% Nixon</li><br>
</ul>
</div>
'''


info_box2 = '''

<div style="position: fixed; top: 10px; left: 260px; max-width: 40em; border: 0px; z-index: 9999; font-size: 13px; border-radius: 5px; background-color: #fff; padding: 8px; box-shadow: 0px 2px 4px #888; opacity: 0.85; overflow: auto; margin-right: 20px">

<p>Unofficial Democratic primary results for the NY State Governor race held on 9/13/2018, NYC results only. Details, data, and code <a href="https://github.com/wtadler/nyc-primary-map">here</a>.</p>

<p><a href="http://wtadler.com">Will Adler</a> 2018</p>

</div>
'''


m.get_root().html.add_child(folium.Element(info_box))
m.get_root().html.add_child(folium.Element(info_box2))


m.save('gov_map.html')




