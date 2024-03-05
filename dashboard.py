#menyiapkan library
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

#load data
day_df = pd.read_csv("day.csv")
hour_df = pd.read_csv("hour.csv")

#memperbaiki tipe data
day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

#memperbaiki nama kolom
def rename_columns(dataframe, column_mapping):
    for old_col, new_col in column_mapping.items():
        dataframe.rename(columns={old_col: new_col}, inplace=True)

column_day = {'dteday': 'date', 'yr': 'year', 'mnth': 'month', 'temp': 'temperature', 'hum': 'humidity', 'cnt': 'total'}
column_hour = {'dteday': 'date', 'yr': 'year', 'mnth': 'month', 'hr': 'hour', 'temp': 'temperature', 'hum': 'humidity', 'cnt': 'total'}

rename_columns(day_df, column_day)
rename_columns(hour_df, column_hour)

#memperbaiki nama kategori season
season_mapping = {1: 'spring', 2: 'summer', 3: 'fall', 4: 'winter'}
day_df['season'] = day_df['season'].replace(season_mapping)
hour_df['season'] = hour_df['season'].replace(season_mapping)

#memperbaiki nama kategori month
day_df['month'] = day_df['month'].apply(lambda x: calendar.month_name[x])
hour_df['month'] = hour_df['month'].apply(lambda x: calendar.month_name[x])

#memperbaiki nama kategori year
year_mapping = {0: '2011', 1: '2012'}
day_df['year'] = day_df['year'].replace(year_mapping)
hour_df['year'] = hour_df['year'].replace(year_mapping)

#memperbaiki nama kategori weekday
weekday_mapping = {0: 'sunday', 1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday', 5: 'friday', 6: 'saturday'}
day_df['weekday'] = day_df['weekday'].replace(weekday_mapping)
hour_df['weekday'] = hour_df['weekday'].replace(weekday_mapping)

# Filter data
min_date = day_df["date"].min()
max_date = day_df["date"].max()

with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main1_df = day_df[(day_df["date"] >= str(start_date)) & 
                (day_df["date"] <= str(end_date))]
main2_df = hour_df[(hour_df["date"] >= str(start_date)) & 
                (hour_df["date"] <= str(end_date))]

st.header('Bike Rent')

#deskripsi jumlah penyewaan sepeda
col1, col2, col3 = st.columns(3)

with col1:
    total_casual = main1_df.casual.sum()
    st.metric("Casual", value="{:,}".format(total_casual))

with col2:
    total_registered = main1_df.registered.sum()
    st.metric("Registered", value="{:,}".format(total_registered))

with col3:
    total_total = main1_df.total.sum()
    st.metric("Total", value="{:,}".format(total_total))

#visualisasi musim
st.subheader('Seasonal Usage')

plot_season = main1_df.groupby('season')[['registered', 'casual']].sum().reset_index()

fig, ax = plt.subplots(figsize=(10, 6)) 

bar_width = 0.35
bar_positions1 = range(len(plot_season['season']))
bar_positions2 = [pos + bar_width for pos in bar_positions1]

plt.bar(bar_positions1, plot_season['registered'], width=bar_width, label='Registered', color='tab:blue')
plt.bar(bar_positions2, plot_season['casual'], width=bar_width, label='Casual', color='tab:orange')

plt.xlabel('Season')
plt.ylabel('Total Rent')
plt.title('Jumlah Penyewaan Sepeda Berdasarkan Musim', fontsize = 17)
plt.xticks([pos + bar_width/2 for pos in bar_positions1], plot_season['season'])
plt.legend()

st.pyplot(fig)

#visualisasi bulan dan tahun
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
main1_df['month'] = pd.Categorical(main1_df['month'], categories=month_order, ordered=True)

st.subheader('Monthly Usage')
fig, ax = plt.subplots(figsize=(10, 6)) 

plot_monthly = main1_df.groupby(by=["month", "year"], observed=False).agg({
    "total": "sum"
}).reset_index()

sns.lineplot(
    data=plot_monthly,
    x="month",
    y="total",
    hue="year",
    style="year",  
    markers=True,
    markersize=8,  
    dashes=False,  
)

plt.grid(False)
plt.title("Jumlah Penyewaan Sepeda Berdasarkan Bulan dan Tahun", fontsize=17)
plt.xlabel(None)
plt.ylabel(None)
plt.legend(title="Tahun", loc="upper right")
plt.tight_layout()

st.pyplot(fig)

#visualisasi tanggal
st.subheader('Daily Usage')

fig, ax = plt.subplots(figsize=(10, 6)) 

plot_ym = main1_df.groupby(by=["date"], observed=False).agg({
    "total": "sum"
}).reset_index()

sns.lineplot(
    data=plot_ym,
    x="date",
    y="total",  
    markers=True,
    markersize=8,  
    dashes=False,  
)

plt.grid(False)
plt.title("Jumlah Penyewaan Sepeda Berdasarkan Tanggal", fontsize = 17)
plt.xlabel(None)
plt.ylabel(None)
plt.tight_layout()

st.pyplot(fig)

#visualisasi pola hari
st.set_option('deprecation.showPyplotGlobalUse', False)

st.subheader('Weekday Usage Pattern')

mask1 = ((main2_df['workingday'] == 0) | (main2_df['holiday'] == 1))
df1 = main2_df[mask1]
mask2 = ((main2_df['workingday'] == 1) & (main2_df['holiday'] == 0))
df2 = main2_df[mask2]

plot_weekday = sns.FacetGrid(hour_df, col='weekday', hue='workingday', col_wrap=2, height=5, sharex=False)
plot_weekday.map(sns.lineplot, "hour", "total")
plot_weekday.fig.suptitle('Pola Penyewaan Sepeda Berdasarkan Hari', y=1.02, fontsize=20)
plot_weekday.set_axis_labels('Hour', 'Total')
plot_weekday.add_legend()

for ax in plot_weekday.axes.flat:
    ax.set(xlabel="Hour")
plot_weekday.set_titles(size=10)

plt.subplots_adjust(wspace=0.3, hspace=0.3)

st.pyplot()

st.caption('Fikry Zaky N')




