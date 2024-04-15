# Import necessary packages here

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc

# ==========================================================================================
# ==========================================================================================

# File:    plot.py
# Date:    April 14, 2024
# Author:  Jonathan A. Webb
# Purpose: This file contains plotting algorithms
# ==========================================================================================
# ==========================================================================================
# Insert Code here


def time_series_plot(df: pd.DataFrame, name: str) -> dcc.Graph:
    """
    Creates a time-series plot for closeout price over time in a DataFrame.

    Parameters
    ----------
    :param df: Dataframe containing the data with 'Date' and 'Close' columns.

    Returns
    -------
    :return: Plotly Graph object visualizing the value of close out price versus time.

    """
    fig = px.line(
        df,
        x="Date",
        y="Close",
        title=f"{name} Close Price Time History",
        template="seaborn",
        hover_data={
            "Date": "|%B %d, %Y",  # Custom date format
            "Close": ":.2f",  # Custom number format
        },
    )
    fig.update_traces(hovertemplate="<b>Date:</b> %{x}<br><b>Close:</b> $%{y:.2f}")

    fig.update_layout(
        title={
            "text": "<b>Close Price Time History</b>",
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"family": "Arial", "size": 24, "color": "black"},
        },
        xaxis_title="Date",
        yaxis_title="Close ($)",
        font=dict(family="Courier New, monospace", size=30, color="black"),
        xaxis=dict(
            title_font=dict(size=22, family="Courier New, monospace"),
            tickfont=dict(size=18, family="Courier New, monospace"),
        ),
        yaxis=dict(
            title_font=dict(size=22, family="Courier New, monospace"),
            tickfont=dict(size=18, family="Courier New, monospace"),
        ),
        autosize=True,
        height=650,
    )
    return fig


# ------------------------------------------------------------------------------------------


def candlestick_plot(df: pd.DataFrame) -> dcc.Graph:
    """
    Creates a candlestick-like plot for percentage changes over time in a DataFrame.

    Parameters
    ----------
    :param df: Dataframe containing the data with 'Date' and 'Percentage' columns.

    Returns
    -------
    :return: Plotly Graph object visualizing the changes in percentage.

    The function calculates the day-to-day percentage change and visualizes this
    using a bar chart where the color of the bars indicates an increase or
    decrease from the previous day.
    """
    if df.empty:
        # Return an empty graph if the DataFrame is empty
        return dcc.Graph()
    # Preparing data for the plot
    df["Date"] = pd.to_datetime(df["Date"])  # Ensure date is datetime type
    # Assuming df is already prepared and sorted
    df["PrevPercentage"] = df["Percentage"].shift(1).fillna(df["Percentage"].iloc[0])
    df["PercentChange"] = df["Percentage"] - df["PrevPercentage"]
    df["color"] = np.where(df["PercentChange"] >= 0, "green", "red")

    # Prepare customdata as a 2D numpy array, each row containing data for one bar
    customdata = np.column_stack((df["Percentage"], df["PercentChange"]))

    # Create the candlestick-like plot
    fig = go.Figure(
        data=[
            go.Bar(
                x=df["Date"],
                y=df["PercentChange"],
                base=df["PrevPercentage"],
                marker_color=df["color"],
                customdata=customdata,
                hovertemplate=(
                    "Date: %{x}<br>"
                    + "Cumulative Change: %{customdata[0]:.2f}%<br>"
                    + "Day Change: %{customdata[1]:.2f}%"
                ),
            )
        ]
    )

    fig.update_layout(
        title={
            "text": "<b>Account Change in %</b>",
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"family": "Arial", "size": 24, "color": "black"},
        },
        xaxis_title="Date",
        yaxis_title="Delta (%)",
        font=dict(family="Courier New, monospace", size=30, color="black"),
        xaxis=dict(
            title_font=dict(size=22, family="Courier New, monospace"),
            tickfont=dict(size=18, family="Courier New, monospace"),
        ),
        yaxis=dict(
            title_font=dict(size=22, family="Courier New, monospace"),
            tickfont=dict(size=18, family="Courier New, monospace"),
        ),
        autosize=True,
        height=650,
    )
    return fig


# ==========================================================================================
# ==========================================================================================
# eof
