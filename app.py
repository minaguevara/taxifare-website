import streamlit as st
import requests as req

from streamlit_folium import st_folium
import folium

st.set_page_config(layout="wide")

map, empty, params = st.columns([3, 0.5, 1])

# Input fields for user to enter parameters
with params:
    st.subheader('Plan your ride')

    date = st.date_input("Date")
    time = st.time_input("Time")
    pickup_latitude = st.number_input("Pickup Latitude", value=None)
    pickup_longitude = st.number_input("Pickup Longitude", value=None)
    dropoff_latitude = st.number_input("Dropoff Latitude", value=None)
    dropoff_longitude = st.number_input("Dropoff Longitude", value=None)
    passenger_count = st.number_input("Number of Passengers", min_value=1, step=1)

    # Button to trigger API call and prediction
    if st.button("Get Fare Prediction", type="primary"):

        # Dictionary containing the parameters for our API...
        params = {
            'pickup_datetime': f"{date} {time}",
            'pickup_longitude': pickup_longitude,
            'pickup_latitude': pickup_latitude,
            'dropoff_longitude': dropoff_longitude,
            'dropoff_latitude': dropoff_latitude,
            'passenger_count': passenger_count
        }

        # Call our API using the `requests` package...
        url = 'https://taxifare.lewagon.ai/predict'
        response = req.get(url, params=params)

        if response.status_code == 200:
            # Retrieve the prediction from the **JSON** returned by the API...
            try:
                prediction = response.json().get('fare', 'Prediction not found')
                st.markdown(f'## Predicted Fare: <span style="color:green">${prediction:.2f}</span>', unsafe_allow_html=True)
            except KeyError:
                st.markdown('### Error: Prediction key not found in API response')
        else:
            st.markdown(f'### Error: Failed to retrieve prediction. Status code: {response.status_code}')


with empty:
    st.empty()


with map:
    # Title and link
    title, link = st.columns([3, 1])
    with title:
        st.title("NY Taxi Fare Prediction")
    with link:
        st.markdown(
            """
            <style>
            .stLinkButton {
                margin-top: 1rem;
                margin-left: 1rem;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.link_button(":gray[Get address coordinates]", "https://gps-coordinates.org/")

    # Folium map centered at an average location or the pickup location if available
    center_lat = pickup_latitude if pickup_latitude else 40.795020
    center_lon = pickup_longitude if pickup_longitude else -73.958588
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # Pickup marker
    if pickup_latitude and pickup_longitude:
        folium.Marker(
            [pickup_latitude, pickup_longitude],
            icon=folium.Icon(color='blue', prefix='fa', icon='person-arrow-up-from-line')
        ).add_to(m)

    # Dropoff marker
    if dropoff_latitude and dropoff_longitude:
        folium.Marker(
            [dropoff_latitude, dropoff_longitude],
            icon=folium.Icon(color='green', prefix='fa', icon='person-arrow-down-to-line')
        ).add_to(m)

    # Display the map in the Streamlit app
    st_data = st_folium(m, width='100%', height=600)
