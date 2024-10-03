import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import geopandas as gpd
from babel.numbers import format_currency

st.set_page_config(layout="wide", page_title="Sales Dashboard", page_icon=":bar_chart:")
st.title("Sales Dashboard")

# Load the dataset
all_df = pd.read_csv('../data/main_data.csv')

all_df["order_date"] = pd.to_datetime(all_df["order_date"], errors="coerce")
with st.sidebar:
    start_date, end_date = st.date_input(
        label="Select Date Range",
        min_value=all_df["order_date"].min(),
        max_value=all_df["order_date"].max(),
        value=[all_df["order_date"].min(), all_df["order_date"].max()]
    )

def visualize(data, x, y = None, hue = None, title = "", xlabel = "", ylabel = "", kind = "hist", height_annot = 9):
    """Function to perform visualization of the data

    Args:
        data (_type_): _description_
        x (_type_): _description_
        y (_type_, optional): _description_. Defaults to None.
        hue (_type_, optional): _description_. Defaults to None.
        title (str, optional): _description_. Defaults to "".
        xlabel (str, optional): _description_. Defaults to "".
        ylabel (str, optional): _description_. Defaults to "".
        kind (str, optional): _description_. Defaults to "hist".
        x_text (int, optional): _description_. Defaults to 9.
    """
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = sns.color_palette("pastel", n_colors=len(data))
    if kind == "line":
        sns.lineplot(data=data, x=x, y=y, hue=hue)
    elif kind == "bar":
        sns.barplot(data=data, x=x, y=y, hue=hue, color=colors[1])
    elif kind == "count":
        sns.countplot(data=data, x=x, hue=hue, color=colors[1])
    elif kind == "hist":
        sns.histplot(data=data, x=x, bins = 20, kde=True, color=colors[1])
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    # Add numbers on top of each bar
    for p in ax.patches:
        height = p.get_height()
        if height > 0:  
            ax.annotate(f'{int(height)}', 
                        (p.get_x() + p.get_width() / 2., height), 
                        ha='center', va='center', 
                        xytext=(0, height_annot), 
                        textcoords='offset points')
    
    st.pyplot(fig)
    
# perform visualization of the sales per datetime
all_df = all_df[(all_df["order_date"] >= str(start_date)) & 
                (all_df["order_date"] <= str(end_date))]

st.subheader("Total Sales Daily", divider=True)
col1 , col2 = st.columns([1, 1])
with col1:
    total_daily_sales = all_df.groupby(by="order_date").total_price.sum().reset_index()
    total_daily_sales = format_currency(total_daily_sales["total_price"].sum(), 'AUD', locale='es_CO') # Convert to Australian Dollar
    st.metric(label="Total Sales", value=total_daily_sales)
    
with col2:
    total_daily_payment = all_df.groupby(by="order_date").payment.sum().reset_index()
    total_daily_payment = format_currency(total_daily_payment["payment"].sum(), 'AUD', locale='es_CO') # Convert to Australian Dollar
    st.metric(label="Total Payment", value=total_daily_payment)

visualize(data=all_df,
          x="order_date",
          y="total_price",
          hue="order_year",
          title="Total Sales per Month",
          xlabel="Month",
          ylabel="Total Sales",
          kind="line")

st.subheader("Sales per Category", divider=True)
col1, col2 = st.columns([1, 1])

# perform visualization of the most selling product
with col1:
    product_sales = all_df.groupby(by="product_name").agg({
        "quantity_x": "sum",
        "total_price": "sum",
    }).sort_values(by="quantity_x", ascending=False).head(10)
    st.text("Top 10 Best Selling Products")
    visualize(data=product_sales.reset_index(),
            x="product_name",
            y="quantity_x",
            hue=None,
            title="Top 10 Best Selling Products",
            xlabel="Product Name",
            ylabel="Total Sales",
            kind="bar")

#visualization of the least selling product
with col2:
    product_sales = all_df.groupby(by="product_name").agg({
        "quantity_x": "sum",
        "total_price": "sum",
    }).sort_values(by="quantity_x", ascending=False).tail(10)
    st.text("Top 10 Worst Selling Products")
    visualize(data=product_sales.reset_index(),
            x="product_name",
            y="quantity_x",
            hue=None,
            title="Top 10 Worst Selling Products",
            xlabel="Product Name",
            ylabel="Total Sales",
            kind="bar")

st.subheader("Demographic Data", divider=True)

col1, col2 = st.columns([1, 1])

# perform visualization of the sales per age
with col1:
    st.text("Total Sales per Age Group")
    visualize(data=all_df,
                x="age",
                hue=None,
                title="Total Sales per Age Group",
                xlabel="Age Group",
                ylabel="Total Sales",
                kind="hist")


# perform visualization of the sales per state
with col2:
    st.text("Total Sales per State")
    visualize(data = all_df,
            x="state",
            y="total_price",
            hue=None,
            title="Total Sales per State",
            xlabel="State",
            ylabel="Total Sales",
            kind="bar",
            height_annot=30)

col1, col2 = st.columns([1, 1])

# perform visualization of the sales per city
with col1:
    col1.text("Top 10 Cities with Highest Sales")
    city_sales = all_df.groupby(by="city").agg({
        "quantity_x": "sum",
        "total_price": "sum",
    }).sort_values(by="total_price", ascending=False).head(10)

    visualize(data=city_sales.reset_index(),
                x="city",
                y="total_price",
                hue=None,
                title="Total Sales per City",
                xlabel="City",
                ylabel="Total Sales",
                kind="bar")

# perform visualization of the sales per gender
with col2:
    st.text("Total Sales per Gender")
    visualize(data=all_df,
                x="gender",
                y="total_price",
                hue=None,
                title="Total Sales per Gender",
                xlabel="Gender",
                ylabel="Total Sales",
                kind="bar",
                height_annot=30)

# perform RFM Analysis
# Recency
recency = all_df.groupby(by="customer_id").order_date.max().reset_index()
recency.columns = ["customer_id", "last_purchase_date"]
recency["recency"] = (all_df["order_date"].max() - recency["last_purchase_date"]).dt.days
recency.drop(columns="last_purchase_date", inplace=True)

# Frequency
frequency = all_df.groupby(by="customer_id").order_id.nunique().reset_index()
frequency.columns = ["customer_id", "frequency"]

# Monetary
monetary = all_df.groupby(by="customer_id").total_price.sum().reset_index()
monetary.columns = ["customer_id", "monetary"]

# Merge the data
rfm = pd.merge(
    left=recency,
    right=frequency,
    how='left',
    left_on="customer_id",
    right_on="customer_id"
)

rfm = pd.merge(
    left=rfm,
    right=monetary,
    how='left',
    left_on="customer_id",
    right_on="customer_id"
)

# perform the visualization of RFM Analysis

st.subheader("RFM Analysis", divider=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col1: 
    avg_recency = round(rfm["recency"].mean(), 2)
    st.metric("Average Recency", value=avg_recency)
    
with col2:
    avg_frequency = round(rfm["frequency"].mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)


with col3:
    avg_monetary = format_currency(rfm["monetary"].mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_monetary)

col1, col2, col3 = st.columns([1, 1, 1]) 

with col1:
    visualize(data=rfm, # Recency
            x="recency",
            hue=None,
            title="Recency Distribution",
            xlabel="Recency",
            ylabel="Total Sales",
            kind="hist")

with col2:
    visualize(data=rfm, # Frequency
            x="frequency",
            hue=None,
            title="Frequency Distribution",
            xlabel="Frequency",
            ylabel="Total Sales",
            kind="hist")

with col3:
    visualize(data=rfm, # Monetary
            x="monetary",
            hue=None,
            title="Monetary Distribution",
            xlabel="Monetary",
            ylabel="Total Sales",
            kind="hist")

# perform geospatial analysis
st.subheader("Geospatial Analysis", divider=True)
australia = gpd.read_file("../STE_2021_AUST_SHP_GDA2020/STE_2021_AUST_GDA2020.shp") # Load the map of Australia

sales_per_state = all_df.groupby(by="state").total_price.sum().reset_index()
sales_per_state.columns = ["iso_a2", "total_sales"]
world = pd.merge(
    left=australia,
    right=sales_per_state,
    how='left',
    left_on="STE_NAME21",
    right_on="iso_a2"
)

fig, ax = plt.subplots(figsize=(20, 10))
world.boundary.plot(ax=ax)
world.plot(column='total_sales', ax=ax, legend=True, legend_kwds={'label': "Total Sales"}, cmap='coolwarm')
plt.title("Total Sales per State")
st.pyplot(fig)

# perform clustering with Manual Grouping
def rfm_cluster(row):
    if row['recency'] <= 30 and row['frequency'] >= 5 and row['monetary'] >= 1000:
        return 'Best Customers'
    elif row['recency'] <= 90 and row['frequency'] >= 3 and row['monetary'] >= 500:
        return 'Loyal Customers'
    elif row['recency'] <= 180 and row['frequency'] >= 1 and row['monetary'] >= 100:
        return 'Potential Loyalists'
    elif row['recency'] > 180 and row['frequency'] >= 1 and row['monetary'] >= 100:
        return 'At Risk'
    else:
        return 'Others'

rfm['cluster'] = rfm.apply(rfm_cluster, axis=1)
st.subheader("Customer Segmentation", divider=True)
visualize(data=rfm, 
          x="cluster",
          hue=None,
          title="Customer Segmentation Manual Grouping",
          xlabel="Cluster",
          ylabel="Total Sales",
          kind="count")
