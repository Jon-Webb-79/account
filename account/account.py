# Import necessary packages here

import os

from dash import Dash
from layout import create_layout

# ==========================================================================================
# ==========================================================================================

# File:    account.py
# Date:    April 12, 2024
# Author:  Jonathan A. Webb
# Purpose: Describe the purpose of functions of this file
# ==========================================================================================
# ==========================================================================================
# Insert Code here


# Set the path to the assets folder and instantiate Dash object
assets_folder = os.path.join(os.getcwd(), "../data", "assets")
app = Dash(__name__, assets_folder=assets_folder, title="Brokerage Data")
app.layout = create_layout(app)
# app = Dash(__name__)


# app.layout = html.Div(
#     [
#         # Provides a variable to which the database file name can be assigned
#         dcc.Store(id="db-path"),
#         # Left column for file upload, buttons, and the table
#         html.Div(
#             [
#                 # File upload component
#                 dcc.Upload(
#                     id="upload-file",
#                     children=html.Button("Upload File", className="upload-button"),
#                     multiple=False,
#                 ),
#                 # Container for displaying file info and buttons
#                 html.Div(id="file-info"),
#                 html.Div(id="funds-buttons"),  # This will hold the fund buttons
#                 # Container for displaying the table below the buttons
#                 html.Div(
#                     id="table-container",
#                     style={"width": "100%", "padding-top": "20px"},
#                 ),
#             ],
#             className="left-column",
#             style={"width": "100%", "display": "inline-block", "verticalAlign": "top"},
#         ),
#         # Right column for other content
#         html.Div(
#             [
#                 # Add the graph at the top of the right column
#                 dcc.Graph(
#                     id="close-price-plot",
#                 ),
#                 dcc.Graph(
#                     id="candlestick-plot",
#                 ),
#             ],
#             className="right-column",
#             style={"width": "70%", "display": "inline-block", "verticalAlign": "top"},
#         ),
#     ],
#     id="app-container",
# )
# ==========================================================================================
# ==========================================================================================


if __name__ == "__main__":
    app.run_server(debug=True)


# ==========================================================================================
# ==========================================================================================
# eof
