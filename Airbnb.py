# Importing Libraries
import pandas as pd
import pymongo
from pymongo import MongoClient
from bson.decimal128 import Decimal128
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
from PIL import Image


# Setting up page configuration
#icon = Image.open("ICN.png")
st.set_page_config(page_title= "Airbnb Data Visualization | By Himani Singh",
                   #page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded",
                   menu_items={'About':  'This dashboard app is created by *Himani Singh*'\
                                        'Data has been imported from mongodb atlas Sample DB for Airbnb'}
                  )

# Creating option menu in the side bar
with st.sidebar:
    selected = option_menu("Menu", ["Home","Overview","Explore"], 
                           icons=["house","graph-up-arrow","bar-chart-line"],
                           menu_icon= "menu-button-wide",
                           default_index=0,
                           styles={"nav-link": {"font-size": "20px", "text-align": "left", "margin": "-2px", "--hover-color": "#FF5A5F"},
                                   "nav-link-selected": {"background-color": "#FF5A5F"}}
                          )

# CREATING CONNECTION WITH MONGODB ATLAS AND RETRIEVING THE Realtime DATA

######## Create CSV Starts here #############

# Connect to MongoDB
client = MongoClient('mongodb+srv://himani:himani@atlascluster.p2wsxy6.mongodb.net/')
db = client['sample_airbnb'] 
collection = db['listingsAndReviews'] 
col = collection
print(collection)
#if False:
# Fetch data from MongoDB
#cursor = collection.find_one()             # Fetch 1 document for testing
cursor = collection.find({})  # Fetch all documents
transformed_data = []
for document in collection.find():
    transformed_doc = {
        "_id": str(document.get("_id")),  
        "Name": document.get("name"),
        "description": document.get("description"),
        "host_id": document.get("host", {}).get("host_id"),
        "Host_name": document.get("host", {}).get("host_name"),
        "host_listing_count": document.get("host", {}).get("host_total_listings_count"),
        "Property_type": document.get("property_type"),
        "Room_type": document.get("room_type"),
        "minimum_nights": document.get("minimum_nights"),
        "maximum_nights": document.get("maximum_nights"),
        "Country": document.get("address").get("country") if document.get("address") is not None else None,
        "neighbourhood": document.get("address").get("suburb") if document.get("address") is not None else None,
       # "location": {
       #     "type": "Point",
       #     "longitude": document.get("address").get("location").get("coordinates")[0],
       #     "latitude": document.get("address").get("location").get("coordinates")[1]
       # },
        "Price": float(document.get("price", Decimal128("0")).to_decimal()),  
        "availability": document.get("availability").get("availability_365") if document.get("availability") is not None else None,
        # {
            # "availability_30": document.get("availability").get("availability_30"),
            # "availability_60": document.get("availability").get("availability_60"),
            # "availability_90": document.get("availability").get("availability_90"),
            # "availability_365": document.get("availability").get("availability_365")
        # },
        "Availability_365": document.get("availability").get("availability_365") if document.get("availability") is not None else None,
        "amenities": document.get("amenities"),
        #"rating": float(document.get("review_scores").get("review_scores_rating", 0)),
        # {
            # "review_scores_accuracy": float(document.get("review_scores").get("review_scores_accuracy", 0)),
            # "review_scores_cleanliness": float(document.get("review_scores").get("review_scores_cleanliness", 0)),
            # "review_scores_checkin": float(document.get("review_scores").get("review_scores_checkin", 0)),
            # "review_scores_communication": float(document.get("review_scores").get("review_scores_communication", 0)),
            # "review_scores_location": float(document.get("review_scores").get("review_scores_location", 0)),
            # "review_scores_value": float(document.get("review_scores").get("review_scores_value", 0)),
            # "review_scores_rating": float(document.get("review_scores").get("review_scores_rating", 0))
        # },
        "last_review_date": str(document.get("last_review")).split('T')[0],
       # "reviews": [
        #    {
        #        "reviewer_id": str(review.get("_id")),  # Convert ObjectId to string
        #        "reviewer_name": review.get("reviewer_name"),
        #        "comment": review.get("comments"),
        #        "rating": float(review.get("rating", 0))  # Convert Decimal128 to float
        #    }
        #    for review in document.get("reviews")
        #],
        "transit": document.get("transit")
    }
    #total_reviews_count = len(document.get("reviews"))
    #transformed_doc["reviews_count"] = total_reviews_count
    transformed_data.append(transformed_doc)

df = pd.DataFrame(transformed_data)
# Fill null values
df['last_review_date'] = pd.to_datetime(df['last_review_date'], errors='coerce')
df = df.dropna(subset=['last_review_date'])
df['last_review_date'] = df['last_review_date'].dt.date


df['neighbourhood'] = df['neighbourhood'].replace('', None)
df = df.dropna(subset=['neighbourhood'])
#df['longitude'] = df['location'].apply(lambda x: x['longitude'])
#df['latitude'] = df['location'].apply(lambda x: x['latitude'])
#df = df.drop(columns=['location'])

csv_file_path = 'Transformed_Data.csv'
df.to_csv('Transformed_Data.csv', index=False)


print("Data has been successfully exported to", csv_file_path) 

######### Create CSV Ends here ###########


# HOME PAGE
if selected == "Home":
    # Title Image
    #st.image("title.png")
    col1,col2 = st.columns(2,gap= 'medium')
    col1.markdown("## :blue[Domain] : Travel Industry, Property Management and Tourism")
    col1.markdown("## :blue[Technologies used] : Python, Pandas, Plotly, Streamlit, MongoDB")
    col1.markdown("## :blue[Overview] : To analyze Airbnb data using MongoDB Atlas, perform data cleaning and preparation, develop interactive visualizations, and create dynamic plots to gain insights into pricing variations, availability patterns, and location-based trends. ")
    col2.markdown("#   ")
    col2.markdown("#   ")
    #col2.image("home.jpg")
    
# OVERVIEW PAGE
if selected == "Overview":
    tab1,tab2 = st.tabs(["$\huge 📝 RAW DATA $", "$\huge🚀 INSIGHTS $"])
    
    # RAW DATA TAB
    with tab1:
        # RAW DATA
        col1,col2 = st.columns(2)
        if col1.button("Click to view Raw data"):
            col1.write(col.find_one())
        # DATAFRAME FORMAT
        if col2.button("Click to view Dataframe"):
            col1.write(col.find_one())
            col2.write(df)
       
    # INSIGHTS TAB
    with tab2:
        # GETTING USER INPUTS
        country = st.sidebar.multiselect('Select a Country',sorted(df.Country.unique()),sorted(df.Country.unique()))
        prop = st.sidebar.multiselect('Select Property_type',df.Property_type.unique(),df.Property_type.unique())
        room = st.sidebar.multiselect('Select Room_type',df.Room_type.unique(),df.Room_type.unique())
        price = st.slider('Select Price',df.Price.min(),df.Price.max(),(df.Price.min(),df.Price.max()))
        
        # CONVERTING THE USER INPUT INTO QUERY
        query = f'Country in {country} & Room_type in {room} & Property_type in {prop} & Price >= {price[0]} & Price <= {price[1]}'
        
        # CREATING COLUMNS
        col1,col2 = st.columns(2,gap='medium')
        
        with col1:
            
            # TOP 10 PROPERTY TYPES BAR CHART
            df1 = df.query(query).groupby(["Property_type"]).size().reset_index(name="Listings").sort_values(by='Listings',ascending=False)[:10]
            fig = px.bar(df1,
                         title='Top 10 Property Types',
                         x='Listings',
                         y='Property_type',
                         orientation='h',
                         color='Property_type',
                         color_continuous_scale=px.colors.sequential.Agsunset)
            st.plotly_chart(fig,use_container_width=True) 
        
            # TOP 10 HOSTS BAR CHART
            df2 = df.query(query).groupby(["Host_name"]).size().reset_index(name="Listings").sort_values(by='Listings',ascending=False)[:10]
            fig = px.bar(df2,
                         title='Top 10 Hosts with Highest number of Listings',
                         x='Listings',
                         y='Host_name',
                         orientation='h',
                         color='Host_name',
                         color_continuous_scale=px.colors.sequential.Agsunset)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig,use_container_width=True)
        
        with col2:
            
            # TOTAL LISTINGS IN EACH ROOM TYPES PIE CHART
            df1 = df.query(query).groupby(["Room_type"]).size().reset_index(name="counts")
            fig = px.pie(df1,
                         title='Total Listings in each Room_types',
                         names='Room_type',
                         values='counts',
                         color_discrete_sequence=px.colors.sequential.Rainbow
                        )
            fig.update_traces(textposition='outside', textinfo='value+label')
            st.plotly_chart(fig,use_container_width=True)
            
            # TOTAL LISTINGS BY COUNTRY CHOROPLETH MAP
            country_df = df.query(query).groupby(['Country'],as_index=False)['Name'].count().rename(columns={'Name' : 'Total_Listings'})
            fig = px.choropleth(country_df,
                                title='Total Listings in each Country',
                                locations='Country',
                                locationmode='country names',
                                color='Total_Listings',
                                color_continuous_scale=px.colors.sequential.Plasma
                               )
            st.plotly_chart(fig,use_container_width=True)
        
# EXPLORE PAGE
if selected == "Explore":
    st.markdown("## Explore more about the Airbnb data")
    
    # GETTING USER INPUTS
    country = st.sidebar.multiselect('Select a Country',sorted(df.Country.unique()),sorted(df.Country.unique()))
    prop = st.sidebar.multiselect('Select Property_type',sorted(df.Property_type.unique()),sorted(df.Property_type.unique()))
    room = st.sidebar.multiselect('Select Room_type',sorted(df.Room_type.unique()),sorted(df.Room_type.unique()))
    price = st.slider('Select Price',df.Price.min(),df.Price.max(),(df.Price.min(),df.Price.max()))
    
    # CONVERTING THE USER INPUT INTO QUERY
    query = f'Country in {country} & Room_type in {room} & Property_type in {prop} & Price >= {price[0]} & Price <= {price[1]}'
    
    # HEADING 1
    st.markdown("## Price Analysis")
    
    # CREATING COLUMNS
    col1,col2 = st.columns(2,gap='medium')
    
    with col1:
        
        # AVG PRICE BY ROOM TYPE BARCHART
        pr_df = df.query(query).groupby('Room_type',as_index=False)['Price'].mean().sort_values(by='Price')
        fig = px.bar(data_frame=pr_df,
                     x='Room_type',
                     y='Price',
                     color='Price',
                     title='Avg Price in each Room type'
                    )
        st.plotly_chart(fig,use_container_width=True)
        
        # HEADING 2
        st.markdown("## Availability Analysis")
        
        # AVAILABILITY BY ROOM TYPE BOX PLOT
        fig = px.box(data_frame=df.query(query),
                     x='Room_type',
                     y='Availability_365',
                     color='Room_type',
                     title='Availability by Room_type'
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    with col2:
        
        # AVG PRICE IN COUNTRIES SCATTERGEO
        country_df = df.query(query).groupby('Country',as_index=False)['Price'].mean()
        fig = px.scatter_geo(data_frame=country_df,
                                       locations='Country',
                                       color= 'Price', 
                                       hover_data=['Price'],
                                       locationmode='country names',
                                       size='Price',
                                       title= 'Avg Price in each Country',
                                       color_continuous_scale='agsunset'
                            )
        col2.plotly_chart(fig,use_container_width=True)
        
        # BLANK SPACE
        st.markdown("#   ")
        st.markdown("#   ")
        
        # AVG AVAILABILITY IN COUNTRIES SCATTERGEO
        country_df = df.query(query).groupby('Country',as_index=False)['Availability_365'].mean()
        country_df.Availability_365 = country_df.Availability_365.astype(int)
        fig = px.scatter_geo(data_frame=country_df,
                                       locations='Country',
                                       color= 'Availability_365', 
                                       hover_data=['Availability_365'],
                                       locationmode='country names',
                                       size='Availability_365',
                                       title= 'Avg Availability in each Country',
                                       color_continuous_scale='agsunset'
                            )
        st.plotly_chart(fig,use_container_width=True)