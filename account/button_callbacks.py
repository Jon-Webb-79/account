# Import necessary packages here
import base64
import tempfile
from typing import Tuple, Union

from dash import Dash, callback_context, html, no_update
from dash.dependencies import ALL, Input, Output, State
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


class ButtonCallbackManager:

    def get_filename(
        self, contents: str, filename: str
    ) -> Tuple[str, Union[str, html.Div]]:
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

    def generate_fund_buttons(
        self,
        file_path: str,
    ) -> tuple[Union[list[html.Button], html.Div], list[str]]:
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
                 This function also assigns the list of button names to fund-list

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
                    n_clicks=0,
                )
                for fund in df["Fund"].unique()
            ]
            return fund_buttons, df["Fund"].unique().tolist()
        except Exception as e:
            return html.Div([f"An error occurred processing the .db file: {e}"]), []

    # ------------------------------------------------------------------------------------------

    def update_fund_button_styles(
        self, n_clicks: list[int], funds: list[str]
    ) -> list[str]:
        """
        Updates the className for fund buttons to indicate which one is active.

        :param n_clicks: A list of integers reflecting the number of clicks for
                         each button.
        :param funds: A list of strings that are the names of the funds.
        :return: A list of class names where the active button receives a
                 different class.

        If no funds are available, the update is prevented to avoid errors.
        The function determines which button was clicked last and updates its
        class to active.
        """
        if not funds:
            raise PreventUpdate

        # Determine which button was clicked using Dash's callback context
        triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
        triggered_index = eval(triggered_id)["index"]

        # Update the className for each button based on which one was clicked
        class_names = [
            "dynamic-button-active" if fund == triggered_index else "dynamic-button"
            for fund in funds
        ]
        return class_names

    # ------------------------------------------------------------------------------------------

    def update_duration_button_styles(
        self, n_clicks: list[int], funds: list[str]
    ) -> list[str]:
        """
        Updates the className for duration buttons to indicate which one is active.

        :param n_clicks: A list of integers reflecting the number of clicks for
                         each button.
        :param durations: A list of strings that are the labels for the duration
                          buttons.
        :return: A list of class names where the active button receives a
                 different class.

        This function prevents updates if no durations are provided and uses
        the last clicked button to determine which className to update for
        indicating the active state.
        """
        if not funds:
            raise PreventUpdate

        # Determine which button was clicked using Dash's callback context
        triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
        triggered_index = eval(triggered_id)["index"]

        # Update the className for each button based on which one was clicked
        class_names = [
            "dynamic-button-active" if fund == triggered_index else "dynamic-button"
            for fund in funds
        ]
        return class_names


# ==========================================================================================
# ==========================================================================================


def register_button_callbacks(app: Dash, manager: ButtonCallbackManager):
    app.callback(
        [Output("db-path", "data"), Output("error-message", "children")],
        Input("upload-file", "contents"),
        State("upload-file", "filename"),
    )(manager.get_filename)

    app.callback(
        [Output("funds-buttons", "children"), Output("fund-list", "data")],
        Input("db-path", "data"),
    )(manager.generate_fund_buttons)

    app.callback(
        Output({"type": "fund-button", "index": ALL}, "className"),
        Input({"type": "fund-button", "index": ALL}, "n_clicks"),
        State("fund-list", "data"),
        prevent_initial_call=True,
    )(manager.update_fund_button_styles)

    app.callback(
        Output({"type": "duration-button", "index": ALL}, "className"),
        [Input({"type": "duration-button", "index": ALL}, "n_clicks")],
        [State("duration-list", "data")],
        prevent_initial_call=True,
    )(manager.update_duration_button_styles)


# ==========================================================================================
# ==========================================================================================
# eof
