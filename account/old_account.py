# Import necessary packages here
import base64
import json
import os
import tempfile

import dash
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash import Dash, Input, Output, State, dash_table, dcc, html
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
from db import create_funds_df, create_position_df

# ==========================================================================================
# ==========================================================================================

# File:    account.py
# Date:    April 09, 2024
# Author:  Jonathan A. Webb
# Purpose: This file integrates the various functions and classes required for the
#          account package
# ==========================================================================================
# ==========================================================================================
# CALLBACK FUNCTIONS

app = Dash(__name__)


pio.templates.default = "seaborn"


@app.callback(
    [
        Output("file-info", "children"),  # Continues to update UI with file info
        Output("db-path", "data"),
    ],  # Now also updates dcc.Store with the DB path
    [Input("upload-file", "contents")],
    [State("upload-file", "filename")],
)
def update_output(contents, filename):
    if contents is None:
        raise PreventUpdate

    if not filename.endswith(".db"):
        return "Please upload a file with a .db extension.", dash.no_update

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    # Save the decoded content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        tmp.write(decoded)
        tmp_db_path = tmp.name  # Path to the temporary file

    try:
        df = create_funds_df(tmp_db_path)
        buttons = [
            html.Button(
                fund,
                id={"type": "fund-button", "index": fund},
                className="dynamic-button",
            )
            for fund in df["Fund"].unique()
        ]
        buttons_container = html.Div(children=buttons, style={"padding-top": "20px"})

        # Return the button container for the UI and the temp DB path for the store
        return buttons_container, {"dbPath": tmp_db_path}
    except Exception as e:
        os.remove(tmp_db_path)
        return (
            html.Div([f"An error occurred processing the .db file: {e}"]),
            dash.no_update,
        )


# ------------------------------------------------------------------------------------------


@app.callback(
    Output("table-container", "children"),
    [Input({"type": "fund-button", "index": ALL}, "n_clicks")],
    [State({"type": "fund-button", "index": ALL}, "id"), State("db-path", "data")],
)
def display_fund_data(n_clicks_list, btn_id_list, db_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    fund_name = json.loads(triggered_id)["index"]

    if db_data is None:
        raise dash.exceptions.PreventUpdate

    db_path = db_data["dbPath"]
    df = create_position_df(db_path, fund_name)

    # Assuming df is your DataFrame for the specific fund
    df["Credit"] = df["Credit"].apply(lambda x: f"${x:,.2f}")
    df["Close"] = df["Close"].apply(lambda x: f"${x:,.2f}")
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    df["Percentage"] = df["Percentage"].apply(lambda x: f"{x:,.2f}%")
    # Display the specific columns
    return dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[
            {"name": "Date", "id": "Date"},
            {"name": "Credit ($)", "id": "Credit"},
            {"name": "Close ($)", "id": "Close"},
            {"name": "Percentage (%)", "id": "Percentage"},
        ],
        fixed_rows={"headers": True},
        style_table={"overflowY": "auto", "maxHeight": "800px"},
        style_header={
            "fontWeight": "bold",  # Makes header text bold
            "textAlign": "center",  # Optional: centers the header text
            "backgroundColor": "rgb(200, 200, 200)",
            "color": "black",  # Text color
            "fontSize": "20px",
            "fontFamily": "Arial",
        },
        style_cell={
            "textAlign": "center",  # Optional:
            "padding": "10px",  # Optional:
        },
        # If you want to specifically style only data cells and not headers:
        style_data={
            "fontSize": "16px",  # Change font size for data cells
            "fontFamily": "Arial",  # Change font type for data cells
        },
    )


# ------------------------------------------------------------------------------------------


@app.callback(
    Output("close-price-plot", "figure"),
    [Input({"type": "fund-button", "index": ALL}, "n_clicks")],
    [State({"type": "fund-button", "index": ALL}, "id"), State("db-path", "data")],
)
def update_graph(n_clicks_list, btn_id_list, db_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # Extract fund name from the button ID that was clicked
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    fund_name = json.loads(
        triggered_id.replace("fund-button-", "")
    )  # Adjust this based on actual ID format

    if db_data is None:
        raise dash.exceptions.PreventUpdate

    db_path = db_data["dbPath"]
    name = fund_name["index"]
    df = create_position_df(db_path, fund_name["index"])

    # Create the plot
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
        autosize=False,
        #    width=800,
        height=800,
    )
    return fig


# ------------------------------------------------------------------------------------------


@app.callback(
    Output("candlestick-plot", "figure"),
    [Input({"type": "fund-button", "index": ALL}, "n_clicks")],
    [State({"type": "fund-button", "index": ALL}, "id"), State("db-path", "data")],
)
def update_candlestick(n_clicks_list, btn_id_list, db_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # Extract fund name from the button ID that was clicked
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    fund_name = json.loads(
        triggered_id.replace("fund-button-", "")
    )  # Adjust this based on actual ID format

    if db_data is None:
        raise dash.exceptions.PreventUpdate

    db_path = db_data["dbPath"]
    df = create_position_df(db_path, fund_name["index"])

    # Preparing data for the plot
    df["Date"] = pd.to_datetime(df["Date"])  # Ensure date is datetime type
    # Assuming df is already prepared and sorted
    df["PrevPercentage"] = df["Percentage"].shift(1).fillna(df["Percentage"][0])
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
        autosize=False,
        #    width=800,
        height=800,
    )
    return fig


# ==========================================================================================
# ==========================================================================================
# TRADITIONAL FUNCTIONS


def process_db_contents(contents, filename):
    """Process .db file and generate buttons based on 'Funds' table."""
    _, content_string = contents.split(",")
    base64.b64decode(content_string)
    try:
        df = create_funds_df(filename)
        buttons = [
            html.Button(fund, id={"type": "fund-button", "index": fund})
            for fund in df["Fund"].unique()
        ]
        return html.Div([html.P(f"File selected: {filename}"), html.Div(buttons)])
    except Exception as e:
        return html.Div([html.P("Failed to process the database file."), html.P(str(e))])


# ==========================================================================================
# ==========================================================================================
# Create a Dash application

# app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Store(id="db-path"),  # Store for holding uploaded DB data
        # Left column for file upload, buttons, and the table
        html.Div(
            [
                # File upload component
                dcc.Upload(
                    id="upload-file",
                    children=html.Button("Upload File", className="upload-button"),
                    multiple=False,
                ),
                # Container for displaying file info and buttons
                html.Div(id="file-info"),
                html.Div(id="funds-buttons"),  # This will hold the fund buttons
                # Container for displaying the table below the buttons
                html.Div(
                    id="table-container",
                    style={"width": "100%", "padding-top": "20px"},
                ),
            ],
            className="left-column",
            style={"width": "100%", "display": "inline-block", "verticalAlign": "top"},
        ),
        # Right column for other content
        html.Div(
            [
                # Add the graph at the top of the right column
                dcc.Graph(
                    id="close-price-plot",
                ),
                dcc.Graph(
                    id="candlestick-plot",
                ),
            ],
            className="right-column",
            style={"width": "70%", "display": "inline-block", "verticalAlign": "top"},
        ),
    ],
    id="container",
)


# ==========================================================================================
# ==========================================================================================


if __name__ == "__main__":
    app.run_server(debug=True)


# ==========================================================================================
# ==========================================================================================
# eof
