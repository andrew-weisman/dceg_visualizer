# Import relevant libraries
import streamlit as st
import os
import pandas as pd
import plotly.express as px
import numpy as np
import subprocess


# Check if the platform is NIDAP
def platform_is_nidap():
    np.any(['nidap.nih.gov' in x for x in subprocess.run('conda config --show channels', shell=True, capture_output=True).stdout.decode().split('\n')[1:-1]])


# Load the data according to the platform we're on
def load_data():
    if platform_is_nidap():
        from foundry.transforms import Dataset
        return Dataset.get("dummy_dashboardv2").read_table(format="pandas")
    else:
        input_dataset = os.path.join(os.getcwd(), 'Dummy_dashboardV2.csv')
        return pd.read_csv(input_dataset)


# Main function definition
def main():

    # Set page configuration
    page_title = 'Dummy Dashboard'
    st.set_page_config(page_title=page_title, page_icon=":bar_chart:", layout="wide")
    st.title(page_title)
    cols = st.columns(2)

    # Get the input dataset
    df = load_data()

    # Preview the dataset
    with cols[0]:
        st.write(df)

    # Get numeric columns
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    # Get potential columns on which to perform filtering
    potential_filter_columns = ['Receipt_ID', 'analysisjobs_getRegion']

    # Widgets to choose X and Y columns
    with cols[0]:
        x_column = st.selectbox('X axis:', options=numeric_columns)
        y_column = st.selectbox('Y axis:', options=numeric_columns)

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
    fig = px.scatter(filtered_df, x=x_column, y=y_column, title=f'{y_column} vs. {x_column}').update_traces(marker=dict(size=5))
    with cols[1]:
        st.plotly_chart(fig)


# Run the main function
if __name__ == '__main__':
    main()
