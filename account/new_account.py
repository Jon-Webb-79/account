# Import necessary packages here

import os

from button_callbacks import register_button_callbacks
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

# Create layout
app.layout = create_layout(app)
register_button_callbacks(app)
# ==========================================================================================
# ==========================================================================================


if __name__ == "__main__":
    app.run_server(debug=True)


# ==========================================================================================
# ==========================================================================================
# eof
