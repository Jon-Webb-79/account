# Import necessary packages here

from dash import Dash, dcc, html

# ==========================================================================================
# ==========================================================================================

# File:    layout.py
# Date:    April 13, 2024
# Author:  Jonathan A. Webb
# Purpose: Describe the purpose of functions of this file
# ==========================================================================================
# ==========================================================================================
# Insert Code here


def create_layout(app: Dash) -> html.Div:
    """
    This function creates the layout for a Dash application as an html.div

    :param app: A Dash object
    :return: An html.Div containing the layout of the application
    """
    return html.Div(
        [
            # Provides a variable to which the database file name can be assigned
            dcc.Store(id="db-path"),
            html.Div(id="error-message"),
            # ==========================================================================================
            # ==========================================================================================
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
                style={
                    "width": "100%",
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
            ),
            # ==========================================================================================
            # ==========================================================================================
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
        id="app-container",
    )


# ==========================================================================================
# ==========================================================================================
# eof
