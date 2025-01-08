# Import relevant libraries
import streamlit as st
import os
import pandas as pd
import plotly.express as px
import numpy as np
import subprocess


# Check if the platform is NIDAP
def platform_is_nidap():
    return np.any(['nidap.nih.gov' in x for x in subprocess.run('conda config --show channels', shell=True, capture_output=True).stdout.decode().split('\n')[1:-1]])


# Load the data according to the platform we're on
@st.cache_data
def load_data():
    if platform_is_nidap():
        from foundry.transforms import Dataset
        dataset_handle_name = "dummy_dashboardv2"
        return Dataset.get(dataset_handle_name).read_table(format="pandas")
    else:
        dataset_file_name = 'Dummy_dashboardV2.csv'
        input_dataset = os.path.join(os.getcwd(), dataset_file_name)
        return pd.read_csv(input_dataset)


# Main function definition
def main():

    # Set page configuration
    page_title = 'DCEG HALO Metadata Viewer'
    st.set_page_config(page_title=page_title, page_icon=":bar_chart:", layout="wide")
    st.title(page_title)
    cols = st.columns([1/3, 2/3], border=True)

    # Get the input dataset
    df = load_data()

    # Get numeric columns
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    # Get potential columns on which to perform filtering
    potential_filter_columns = ['Receipt_ID', 'analysisjobs_getRegion']

    # Widgets to choose X and Y columns
    with cols[0]:
        x_column = st.selectbox('x axis:', options=numeric_columns)
        y_column = st.selectbox('y axis:', options=numeric_columns)

        # Choose a filter column
        filter_column = st.selectbox('Filter column:', options=potential_filter_columns)

        # Filter the data based on the filter column
        filter_values = st.multiselect('Filter values:', options=df[filter_column].unique())

    # Perform the filtering
    if filter_values:
        filtered_df = df[df[filter_column].isin(filter_values)]
    else:
        filtered_df = df

    # Scatter plot
    with cols[1]:
        with st.columns(3)[0]:
            marker_size = st.number_input('Marker size:', value=5)
        fig = px.scatter(filtered_df, x=x_column, y=y_column, title=f'{y_column} vs. {x_column}').update_traces(marker=dict(size=marker_size))
        chart_selection = st.plotly_chart(fig, on_select='rerun')

    # Show the selected data points
    point_indices = chart_selection['selection']['point_indices']
    if point_indices:
        st.subheader('Selected points')
        point_indices = point_indices
        st.write(filtered_df.iloc[point_indices])

    # Preview the dataset
    st.subheader('Full dataset')
    st.write(df)


# Run the main function
if __name__ == '__main__':
    main()
