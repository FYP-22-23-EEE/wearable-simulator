import streamlit as st

st.title('Wearable Device Control Panel')

# Define the options for your dropdowns
device_frequency_options = ['10Hz', '20Hz', '50Hz', '100Hz']
activity_options = ['Activity 1', 'Activity 2', 'Activity 3']

# Create the dropdowns in the top header
device_frequency = st.sidebar.selectbox('Select Device Frequency', device_frequency_options)
activity = st.sidebar.selectbox('Select Activity', activity_options)

# Create a 4x4 grid of toggle buttons
st.write('Device Status:')
device_status = []
for i in range(2):
    row = []
    for j in range(2):
        # Each button is tied to a unique key (i, j) and defaults to False
        status = st.button('Device {}{}'.format(i, j), key=(i, j))
        row.append(status)
    device_status.append(row)
