#!/usr/bin/env python
# UFO Sighting Report Data Cleanup + Visualization

# Importing Relavant Libraries

get_ipython().system(' pip install numpy pandas seaborn plotly.express wordcloud matplotlib')
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

# Setting environment to ignore future warnings
import warnings
warnings.simplefilter('ignore')

from matplotlib.pylab import rcParams
rcParams["figure.figsize"] = (16,7)


# Reading Dataset
df = pd.read_csv(r"nuforc_reports.csv")
df.head(3) #returns top 3 rows of data --> ensures file is read correctly

#returns # of records in dataset
df.shape
#output: 88125 rows and 12 col

#returns further insight about the null data
df.info()


# ------------ Data Cleaning ------------
# Checking for missing values in data per column (# missing, % missing)
def missing_zero_values_table(df):
    mis_val = df.isnull().sum()
    mis_val_percent = 100 * df.isnull().sum() / len(df)
    mz_table = pd.concat([mis_val, mis_val_percent], axis=1)
    mz_table = mz_table.rename(
        columns={0: 'Missing Values', 1: '% of Total Values'})
    mz_table['Data Type'] = df.dtypes
    mz_table = mz_table[
        mz_table.iloc[:, 1] != 0].sort_values(
        '% of Total Values', ascending=False).round(1)
    print("The " +  " dataframe has " + str(df.shape[1]) + " columns and " + str(df.shape[0]) + " rows.\n"
          "There are " + str(mz_table.shape[0]) + " columns that have missing values.")
    return mz_table #table generated
#call
missing_zero_values_table(df)



#since highest % is missing from lat & long:
df[df.city_latitude.isnull()].head(2)
# Dropping rows containing missing latitude & logitude col simultaneously
index = df[df.city_latitude.isnull()].index
df.drop(index, inplace=True)

# Filling Duration, Shape column's Null values with the most frequent value
df.duration.fillna(value=dict(df.duration.mode())[0], inplace=True)
df["shape"].fillna(value="light", inplace=True)
#call
missing_zero_values_table(df) # 5 columns have missing values


##since highest % is missing from date time
df[df.date_time.isnull()].head(2)
# date time missing means posted column value is also missing.
# Dropping missing values from date_time and posted columns
index = df[df.date_time.isnull()].index
df.drop(index, inplace=True)


# Dropping all other NAN values
df.dropna(inplace=True)

missing_zero_values_table(df) # no columns with missing values


# Extract date info from the stats column, save this in new column called date
df[['drop', 'date']] = df['stats'].str.extract(r'^(?P<drop>Occurred : )(?P<date>[0-9]{1,2}[/][0-9]{1,2}[/][0-9]{4})')

#Drop all access columns that dont have useful info for further analysis
df.drop(columns=['date_time', 'stats', 'report_link', 'text', 'posted', 'drop'], inplace=True)

# Set the correct data type for the columns
df['date'] = pd.to_datetime(df['date'], errors = 'coerce')
df['summary'] = df['summary'].astype(str)

df.shape
# lost 9% percent data in the whole cleaning process

#------------Data Visualization------------
# Creates an image displaying most frequently used works the sighters said about UFO
text = " ".join(df['summary'])
wordcloud = WordCloud(background_color="black", width=1600, height=800
).generate(text)

plt.figure(figsize=(16, 8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.margins(x=0, y=0)
plt.show()

#shows the % on bar
def per_on_bar(plot,feature):
    total = len(feature)
    for p in plot.patches:
        percentage = '{:.1f}%'.format(100 * p.get_height()/total)
        x = p.get_x() + p.get_width() / 2 - 0.08
        y = p.get_y() + p.get_height()
        ax.annotate(percentage, (x, y), size = 8)
    plt.show()

#Graph displays # of sightings by city
names = []
values = []
for i, j in dict(df.city.value_counts()[0:50]).items():
    names.append(i)
    values.append(j)
plt.xticks(rotation=60)
ax = sns.barplot(x=names, y=values)
per_on_bar(ax, df.city)
plt.title(
    'UFO Sightings by City',
    fontdict={
        'fontsize': 16
    }
)


#Graph displays # of sightings by shape
plt.xticks(rotation=60)
ax = sns.countplot(df["shape"])
per_on_bar(ax, df["shape"])
plt.title(
    'UFO Sightings by Shape',
    fontdict={
        'fontsize': 16
    }
)


#Graph displays # of sightings by state
plt.figure(figsize=(15, 15))
sns.countplot(
    data=df,
    y='state',
    order=df['state'].value_counts().index
)
plt.title(
    'UFO Sightings by State',
    fontdict={
        'fontsize': 16
    }
)


#Graph Displays UFO sightings over the years
sns.set_theme(style='darkgrid')
fig = sns.kdeplot(
    data=df,
    x='date',
    fill=True
)
plt.title(
    'UFO sightings Over the Years',
    fontdict={
        'fontsize': 16
    }
)


# Create a temporary dataframe with no missing values
df_temp = df.copy()
df_temp = df_temp.dropna(subset=['date'])
df_temp['year'] = pd.DatetimeIndex(df_temp['date']).year


#Animated USA map of sightings per year in each state
fig = px.choropleth(
    df_temp.groupby(['state', 'year'])['year'].count().reset_index(name='Sightings').sort_values(by=['year'], ascending=True),
    locations="state",
    color='Sightings',
    color_continuous_scale='aggrnyl',
    locationmode='USA-states',
    scope="usa",
    animation_frame="year",
    animation_group='state',
    height=700
)

fig.update_layout(
    title_text='UFO sightings over the years',

)

fig.show()

#static
fig = px.choropleth(
    df_temp.groupby(['state'])['state'].count().reset_index(name='Sightings'),
    locations='state',
    color='Sightings',
    color_continuous_scale='aggrnyl',
    locationmode = 'USA-states',
    height=700
)

fig.update_layout(
    title_text = 'Total UFO sightings by state',
    geo_scope='usa', # limite map scope to USA
)

fig.show()
