import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import geopandas as gpd
from babel.numbers import format_currency

def main():
    st.set_page_config(layout="wide", page_title="E-Commerce Sales Dashboard", page_icon=":bar_chart:")
    st.title("E-Commerce Sales Dashboard")

    # Load the dataset
    all_df = pd.read_csv('../data/all_df.csv')

    all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])
    with st.sidebar:
        start_date, end_date = st.date_input(
            label="Select Date Range",
            min_value=pd.Timestamp('2018-06-01'),
            max_value=pd.Timestamp('2018-12-31'),
            value=[pd.Timestamp('2018-08-01'), pd.Timestamp('2018-08-31')]
        )

    def visualize(data, x, y=None, hue=None, title="", xlabel="", ylabel="", kind="hist", height_annot=9):
        fig, ax = plt.subplots(figsize=(20, 10))
        colors = sns.color_palette("pastel", n_colors=len(data))
        if kind == "line":
            sns.lineplot(data=data, x=x, y=y, hue=hue, color='skyblue')
        elif kind == "bar":
            sns.barplot(data=data, x=x, y=y, hue=hue, color='skyblue')
        elif kind == "count":
            sns.countplot(data=data, x=x, hue=hue, color='skyblue')
        elif kind == "hist":
            sns.histplot(data=data, x=x, kde=True, color='skyblue')
        ax.set_ylabel(ylabel)
        ax.set_xlabel(xlabel)
        ax.set_title(title)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        for p in ax.patches:
            height = p.get_height()
            if height > 0:
                ax.annotate(f'{int(height)}',
                            (p.get_x() + p.get_width() / 2., height),
                            ha='center', va='center',
                            xytext=(0, height_annot),
                            textcoords='offset points')

        st.pyplot(fig)

    all_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                    (all_df["order_purchase_timestamp"] <= str(end_date))]

    st.subheader("Total Order Daily", divider=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        total_daily_order = all_df.groupby(by="order_purchase_timestamp").order_id.count().reset_index()
        st.metric(label="Total Order", value=total_daily_order["order_id"].sum())

    with col2:
        total_daily_payment = all_df.groupby(by="order_purchase_timestamp").payment_value.sum().reset_index()
        total_daily_payment = format_currency(total_daily_payment["payment_value"].sum(), 'BRL', locale='pt_BR')
        st.metric(label="Total Revenue", value=total_daily_payment)

    visualize(data=all_df,
              x="order_purchase_timestamp",
              y="payment_value",
              title="Total Revenue Daily",
              xlabel="Date",
              ylabel="Total Revenue",
              kind="line")

    st.subheader("Sales Performance", divider=True)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.text("Top 10 Best Selling Products")
        group_product = all_df.groupby(by="product_category_name_english").order_id.count().reset_index()
        group_product = group_product.sort_values(by="order_id", ascending=False).head(10)
        visualize(data=group_product,
                  x="product_category_name_english",
                  y="order_id",
                  title="Top 10 Best Selling Products",
                  xlabel="Product Category",
                  ylabel="Total Sales",
                  kind="bar")

    with col2:
        st.text("Top 10 Worst Selling Products")
        group_product = group_product.sort_values(by="order_id", ascending=True).tail(10)
        visualize(data=group_product,
                  x="product_category_name_english",
                  y="order_id",
                  title="Top 10 Worst Selling Products",
                  xlabel="Product Category",
                  ylabel="Total Sales",
                  kind="bar")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.text("Top 10 Best Revenue Products")
        group_product = all_df.groupby(by="product_category_name_english").payment_value.count().reset_index()
        group_product = group_product.sort_values(by="payment_value", ascending=False).head(10)
        visualize(data=group_product,
                  x="product_category_name_english",
                  y="payment_value",
                  title="Top 10 Best Selling Products",
                  xlabel="Product Category",
                  ylabel="Total Revenue",
                  kind="bar")

    with col2:
        st.text("Top 10 Worst Revenue Products")
        group_product = group_product.sort_values(by="payment_value", ascending=True).tail(10)
        visualize(data=group_product,
                  x="product_category_name_english",
                  y="payment_value",
                  title="Top 10 Worst Selling Products",
                  xlabel="Product Category",
                  ylabel="Total Revenue",
                  kind="bar")

    st.subheader("Package and Shipping Performance", divider=True)

    order_df = pd.read_csv("../data/orders_dataset.csv")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.text("Packaging Time Distribution")
        order_df["order_approved_at"] = pd.to_datetime(order_df["order_approved_at"])
        order_df["order_delivered_carrier_date"] = pd.to_datetime(order_df["order_delivered_carrier_date"])
        order_df["packaging_time"] = order_df["order_delivered_carrier_date"] - order_df["order_approved_at"]
        order_df["packaging_time"] = order_df["packaging_time"].abs()
        order_df["packaging_time_hours"] = order_df["packaging_time"].dt.total_seconds() / 3600

        order_df = order_df[order_df['packaging_time_hours'] < 100]

        fig, ax = plt.subplots(figsize=(20, 10))
        sns.histplot(data=order_df, x="packaging_time_hours", kde=True, color="skyblue")
        plt.title("Packaging Time Distribution")
        plt.xlabel("Packaging Time (hours)")
        plt.ylabel("Count")
        st.pyplot(fig)

    with col2:
        st.text("Shipping Time Distribution")
        order_df["order_delivered_customer_date"] = pd.to_datetime(order_df["order_delivered_customer_date"])
        order_df["shipping_time"] = order_df["order_delivered_customer_date"] - order_df["order_delivered_carrier_date"]
        order_df.loc[:, 'shipping_time_hours'] = order_df['shipping_time'].dt.total_seconds() / 3600
        order_df = order_df[order_df['shipping_time_hours'] < 100]
        fig, ax = plt.subplots(figsize=(20, 10))
        sns.histplot(data=all_df, x="shipping_time_hours", kde=True, color="skyblue")
        plt.title("Shipping Time Distribution")
        plt.xlabel("Shipping Time (hours)")
        plt.ylabel("Count")
        st.pyplot(fig)

    all_df["order_purchase_date"] = all_df["order_purchase_timestamp"].dt.date
    all_df["order_purchase_month"] = all_df["order_purchase_timestamp"].dt.to_period("M")
    all_df["order_purchase_year"] = all_df["order_purchase_timestamp"].dt.to_period("Y")

    current_date = all_df["order_purchase_date"].max()
    recency_df = all_df.groupby("customer_unique_id").agg({"order_purchase_date": "max"}).reset_index()
    recency_df["recency"] = current_date - recency_df["order_purchase_date"]
    recency_df["recency"] = recency_df["recency"].apply(lambda x: x.days)

    frequency_df = all_df.groupby("customer_unique_id").agg({"order_id": "count"}).reset_index()
    frequency_df.rename(columns={"order_id": "frequency"}, inplace=True)

    monetary_df = all_df.groupby("customer_unique_id").agg({"payment_value": "sum"}).reset_index()
    monetary_df.rename(columns={"payment_value": "monetary"}, inplace=True)

    st.subheader("RFM Analysis", divider=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.metric(label="Recency", value="{:,.2f} days".format(recency_df["recency"].mean()))
    with col2:
        st.metric(label="Frequency", value="{:,.2f}".format(frequency_df["frequency"].mean()))
    with col3:
        st.metric(label="Monetary", value=format_currency(monetary_df["monetary"].mean(), 'BRL', locale='pt_BR'))

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        visualize(data=recency_df,
                  x="recency",
                  title="Recency Distribution",
                  xlabel="Recency",
                  ylabel="Total Customer",
                  kind="hist")

    with col2:
        visualize(data=frequency_df,
                  x="frequency",
                  title="Frequency Distribution",
                  xlabel="Frequency",
                  ylabel="Total Customer",
                  kind="hist")

    with col3:
        visualize(data=monetary_df,
                  x="monetary",
                  title="Monetary Distribution",
                  xlabel="Monetary",
                  ylabel="Total Customer",
                  kind="hist")

    st.subheader("Geospatial Analysis", divider=True)

    brazil_map = gpd.read_file("../br_shp/br.shp")
    brazil_map['id'] = brazil_map['id'].str.replace('BR', '')
    grouped_df = all_df.groupby("geolocation_state").agg({"order_id": "count"}).reset_index()

    brazil_map = brazil_map.merge(grouped_df, left_on="id", right_on="geolocation_state", how="left")

    fig, ax = plt.subplots(figsize=(20, 10))
    brazil_map.boundary.plot(ax=ax)
    brazil_map.plot(column="order_id", cmap="coolwarm", legend=True, ax=ax)
    plt.title("Total Sales by State")
    st.pyplot(fig)

if __name__ == "__main__":
    main()
