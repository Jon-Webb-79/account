# Import necessary packages here
import base64
import tempfile
from typing import Tuple, Union

from dash import Dash, html, no_update
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


def register_button_callbacks(app: Dash) -> None:
    """
    Contains all button callback functions to support a Dash object

    :param app: A Dash object
    """

    @app.callback(
        [Output("db-path", "data"), Output("error-message", "children")],
        Input("upload-file", "contents"),
        State("upload-file", "filename"),
    )
    def get_filename(contents: str, filename: str) -> Tuple[str, Union[str, html.Div]]:
        """
        Processes the uploaded file and returns the path to a temporarily saved
        database file.

        This callback is triggered by a file upload event. It decodes the
        content of the uploaded file, saves it temporarily, and checks the file
        extension to ensure it's a .db file.

        :param contents: The content of the uploaded file, encoded in base64.
        :param filename: The name of the uploaded file, used to validate the file
                         type.

        :return: A tuple containing the path to the temporary database file and
                 an error message. If the file extension is not .db, it returns
                 a message prompting the user to upload a .db file.

        If no file is uploaded, this callback prevents further updates to
        prevent errors.
        """
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
    def generate_fund_buttons(file_path: str) -> Union[list[html.Button], html.Div]:
        """
        Generates HTML button elements for each unique fund found in the database
        file specified by the file path.

        This callback is triggered when the 'db-path' data is updated with a valid
        file path. It reads the database file, extracts unique fund names, and
        generates a button for each fund. These buttons are returned as a list
        of Dash HTML components and can be dynamically displayed in the UI.

        :param file_path: The file path to the database file from which fund
                          data is to be read.

        :return: A list of HTML button components, each representing a unique
                 fund from the database. If an error occurs during the file
                 processing, it returns an HTML Div containing an error message.

        If the file path is not provided, this callback prevents further updates
        to avoid processing errors.
        """
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
