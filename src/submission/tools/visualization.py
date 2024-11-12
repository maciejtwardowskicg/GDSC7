from langchain_core.tools import tool

import json
import io
from typing import Literal
import boto3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



@tool
def visualization(chart_type: Literal['scatter','line','bar'], data_json: str, filename: str, x_axis: str, y_axis: str, palette: str = 'dark', rotate_xticks: bool = True, xticks_rotation: int = 45) -> str:
    """
    Visualize results and Generate a Seaborn chart based on input data and save it as an image file, with optional value annotations for bar charts.

    Parameters:
    -----------
    chart_type : Literal['scatter', 'line', 'bar']
        The type of chart to generate. Must be one of 'scatter', 'line', or 'bar'.
    data_json : str
        A JSON string containing the data to be plotted.
    filename : str
        The name of the file (including path if necessary) where the chart image will be saved.
    x_axis : str
        The name of the column in the data to be used for the x-axis.
    y_axis : str
        The name of the column in the data to be used for the y-axis.
    rotate_xticks : bool
        Whether to rotate the x-axis ticks (default is True).
    xticks_rotation : int
        The degree of rotation for the x-axis ticks (default is 45).

    Returns:
    --------
    str
        A message confirming that the chart has been saved, including the filename.
    """
    
    # Convert JSON input to a pandas DataFrame
    data = json.loads(data_json)
    df = pd.DataFrame(data)

    # Create the Seaborn plot
    plt.figure(figsize=(10, 6))
        
    if chart_type == "scatter":
        sns.scatterplot(data=df, x=x_axis, y=y_axis, palette=palette)
    elif chart_type == "line":
        sns.lineplot(data=df, x=x_axis, y=y_axis, palette=palette)
    elif chart_type == "bar":
        ax = sns.barplot(data=df, x=x_axis, y=y_axis, palette=palette)
    
    # Set labels
    plt.title("Visual representation of data")
    
    if rotate_xticks:
        plt.xticks(rotation=xticks_rotation, ha='right')
    
    # Save the plot to a BytesIO object
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', dpi=300, bbox_inches='tight')
    plt.close()

    # Reset the pointer of the BytesIO object
    img_data.seek(0)

    # Upload the image to S3
    session = boto3.Session()
    s3 = session.client('s3')
    bucket_name = 'bucket_name'
    try:
        s3.upload_fileobj(img_data, bucket_name, filename)
        # Build and return the S3 URL
        s3_url = f'https://{bucket_name}.s3.amazonaws.com/{filename}'
        return f"![Chart Preview]({s3_url})"
    except Exception as e:
        return f"An error occurred: {str(e)}"
