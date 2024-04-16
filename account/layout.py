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
    button_labels = ["Total", "YTD", "1YR", "3MO", "1MO", "1WK"]

    return html.Div(
        [
            # Provides a variable to which the database file name can be assigned
            dcc.Store(id="db-path"),
            # Store the fund list data as a list
            dcc.Store(id="fund-list"),
            # Store the initial JSON data for data
            dcc.Store(id="fund-data"),
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
                    html.Div(
                        id="error-message",
                        style={
                            "color": "red",
                            "fontWeight": "bold",
                            "fontSize": "22px",
                            "fontStyle": "Helvetica Neue",
                            "margin-top": "10px",
                        },
                    ),
                    # Container for displaying file info and buttons
                    html.Div(id="file-info"),
                    html.Div(
                        id="funds-buttons", style={"padding": "10px"}
                    ),  # This will hold the fund buttons
                    html.Div(
                        id="error-message2",
                        style={
                            "color": "red",
                            "fontWeight": "bold",
                            "fontSize": "22px",
                            "fontStyle": "Helvetica Neue",
                            "margin-top": "10px",
                        },
                    ),
                    # dcc.Markdown(id='value-display'),
                    html.Div(id="value-display", style={"margin": "20px 0"}),
                    # Container for displaying the table below the buttons
                    html.Div(
                        id="table-container",
                        style={"width": "100%", "padding-top": "20px"},
                    ),
                ],
                className="left-column",
                style={
                    "flex": "1 1 auto",  # Flex-grow, flex-shrink, flex-basis
                    "min-width": "30%",  # Minimum width to prevent shrinking too small
                    "max-width": "70%",  # Maximum width
                    "verticalAlign": "top",
                    "padding": "20px",
                },
            ),
            # ==========================================================================================
            # ==========================================================================================
            # Right column for other content
            html.Div(
                [
                    # Graphs at the top of the right column
                    dcc.Graph(id="close-price-plot"),
                    dcc.Graph(id="candlestick-plot"),
                    # Div for the buttons below the candlestick-plot
                    html.Div(
                        [
                            # Create buttons with indexed ids
                            html.Button(
                                label,
                                id={"type": "duration-button", "index": label},
                                className=(
                                    "dynamic-button"
                                    if label != "Total"
                                    else "dynamic-button-active"
                                ),
                            )
                            for label in button_labels
                        ]
                        + [
                            dcc.Store(id="duration-list", data=button_labels)
                        ],  # Store for button labels
                        style={
                            "display": "flex",  # Align buttons horizontally
                            "justify-content": "center",  # Center buttons in the div
                            "padding-top": "10px",
                            "gap": "10px",  # Space between the buttons
                        },
                        id="duration-buttons",
                    ),
                ],
                className="right-column",
                style={
                    "flex": "3 1 auto",  # Larger flex-grow to take more space
                    "min-width": "70%",  # Minimum width to prevent shrinking too small
                    "max-width": "100%",  # Maximum width to control expansion
                    "display": "inline-block",
                    "verticalAlign": "top",
                },
            ),
        ],
        id="app-container",
    )


# ==========================================================================================
# ==========================================================================================
# eof
