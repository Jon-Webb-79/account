# Import necessary packages here
import base64
import tempfile

from dash import html, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from db import create_funds_df

# ==========================================================================================
# ==========================================================================================

# File:    button_callbacks.py
# Date:    April 13, 2024
# Author:  Jonathan A. Webb
# Purpose: Describe the purpose of functions of this file
# ==========================================================================================
# ==========================================================================================
# Insert Code here


def register_button_callbacks(app):

    @app.callback(
        [Output("db-path", "data"), Output("error-message", "children")],
        Input("upload-file", "contents"),
        State("upload-file", "filename"),
    )
    def get_filename(contents, filename):
        """This function saves the uploaded DB file temporarily and returns its path."""
        if contents is None:
            raise PreventUpdate

        if not filename.endswith(".db"):
            return no_update, "Please upload a file with a .db extension."

        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        # Save the decoded content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            tmp.write(decoded)
            tmp_db_path = tmp.name  # Path to the temporary file

        return tmp_db_path, no_update

    # ------------------------------------------------------------------------------------------

    @app.callback(Output("funds-buttons", "children"), Input("db-path", "data"))
    def generate_fund_buttons(file_path):
        """This function generates buttons for each unique fund in the .db file."""
        if not file_path:
            raise PreventUpdate

        try:
            df = create_funds_df(file_path)
            fund_buttons = [
                html.Button(
                    fund,
                    id={"type": "fund-button", "index": fund},
                    className="dynamic-button",
                )
                for fund in df["Fund"].unique()
            ]
            return fund_buttons
        except Exception as e:
            return html.Div([f"An error occurred processing the .db file: {e}"])


# ==========================================================================================
# ==========================================================================================
# eof
