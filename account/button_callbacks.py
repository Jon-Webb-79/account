# Import necessary packages here
import base64
import json
import tempfile
from typing import Tuple, Union

import pandas as pd
from dash import Dash, callback_context, dash_table, html, no_update
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate
from dateutil import parser
from dateutil.relativedelta import relativedelta
from db import create_funds_df, create_position_df, get_database_tables
from plot import candlestick_plot, time_series_plot

# ==========================================================================================
# ==========================================================================================

# File:    button_callbacks.py
# Date:    April 13, 2024
# Author:  Jonathan A. Webb
# Purpose: This file contains all functions necessary to create actions whena a button
#          is depressed.  For brevity of integration the functions are integrated into
#          a class
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
            return no_update, "Error: Please upload a file with a .db extension."

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
    ) -> tuple[Union[list[html.Button], html.Div], list[str], str]:
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
            # Attempt to load fund names and database table names
            df = create_funds_df(file_path)
            if df.empty:
                return no_update, no_update, no_update

            table_df = get_database_tables(file_path)

            # Cross-reference fund names with database table names
            valid_funds = [
                fund
                for fund in df["Fund"].unique()
                if fund in table_df["Tables"].tolist()
            ]

            # If no valid funds are available, provide an appropriate error message
            if not valid_funds:
                error_msg = "Error: Fund names do not match existing tables!"
                return no_update, no_update, error_msg

            # Generate buttons only for valid funds
            fund_buttons = [
                html.Button(
                    fund,
                    id={"type": "fund-button", "index": fund},
                    className="dynamic-button-active" if index == 0 else "dynamic-button",
                    n_clicks=0,
                )
                for index, fund in enumerate(valid_funds)
            ]
            return fund_buttons, valid_funds, ""  # No error message when successful

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            return [], [], error_msg

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
        self, n_clicks: list[int], durations: list[str]
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
        if not callback_context.triggered:
            # If no button has been clicked yet, maintain initial state
            return [
                "dynamic-button-active" if duration == "Total" else "dynamic-button"
                for duration in durations
            ]

        # Determine which button was clicked
        triggered_id = callback_context.triggered[0]["prop_id"]
        triggered_info = json.loads(triggered_id.split(".")[0])
        triggered_index = triggered_info["index"]

        return [
            "dynamic-button-active" if duration == triggered_index else "dynamic-button"
            for duration in durations
        ]

    # ------------------------------------------------------------------------------------------

    def load_and_store_data(
        self,
        fund_n_clicks: list[int],
        duration_n_clicks: list[int],
        db_filename: str,
        duration_class: list[str],
        duration_id: list[dict[str, str]],
        fund_class: list[str],
        fund_id: list[dict[str, str]],
    ) -> float:
        """
        Fetches data based on the latest clicked fund or duration button,
        filters it, and updates the dashboard.

        This method decides whether to fetch new data based on a fund button
        click or apply a new duration filter based on a duration button click.
        It also identifies which fund or duration button was last activated,
        fetches and processes the corresponding data, then returns a table and
        two plotly graph components for the UI.

        Parameters
        ----------
        :fund_n_clicks (list[int]): List containing the number of clicks for each
                                    fund button.
        :duration_n_clicks (list[int]): List containing the number of clicks for
                                        each duration button.
        :db_filename (str): The filepath to the database file from which data is
                            fetched.
        :duration_class (list[str]): List containing the class names of duration
                                     buttons to identify which is active.
        :duration_id (list[dict[str, str]]): List of dictionaries identifying
                                             each duration button by type and index.
        :fund_class (list[str]): List containing the class names of fund buttons
                                 to identify which is active.
        :fund_id (list[dict[str, str]]): List of dictionaries identifying each
                                         fund button by type and index.

        Returns
        -------
        :tuple[dash_table.DataTable, dcc.Graph, dcc.Graph]: A tuple containing a
                                                            Dash DataTable and two
                                                            Plotly Graph objects
          (one line plot and one candlestick plot) representing the processed
           data for display.

        Raises
        ------
        :PreventUpdate: If no button was clicked, to prevent the callback from
                        executing without user interaction.
        """

        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        triggered_info = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
        triggered_type = triggered_info["type"]
        button_name = triggered_info["index"]

        filter_time = "Total"
        if triggered_type == "fund-button":
            for index, i in enumerate(duration_class):
                if i == "dynamic-button-active":
                    filter_time = duration_id[index]["index"]
                    break

        else:
            filter_time = button_name
            button_name = "none"
            for index, i in enumerate(fund_class):
                if i == "dynamic-button-active":
                    button_name = fund_id[index]["index"]
                    break
            if button_name == "none":
                button_name = fund_id[index][0]

        df = create_position_df(db_filename, button_name).round(2)
        if df.empty:
            return None  # Optionally handle empty data case

        filtered_df = self._filter_dataframe_by_duration(df, filter_time).copy()

        time_plot = time_series_plot(filtered_df, button_name)
        candle_plot = candlestick_plot(filtered_df)
        return self._create_table(filtered_df), time_plot, candle_plot

    # ------------------------------------------------------------------------------------------

    def update_value_display(
        self,
        fund_clicks,
        duration_clicks,
        db_filename,
        duration_class,
        duration_id,
        fund_class,
        fund_id,
    ) -> str:
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        # Determine which button triggered the update
        triggered_info = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
        triggered_type = triggered_info["type"]
        button_name = triggered_info["index"]

        filter_time = "Total"
        if triggered_type == "fund-button":
            for index, i in enumerate(duration_class):
                if i == "dynamic-button-active":
                    filter_time = duration_id[index]["index"]
                    break
        else:
            filter_time = button_name
            button_name = "none"
            for index, i in enumerate(fund_class):
                if i == "dynamic-button-active":
                    button_name = fund_id[index]["index"]
                    break
            if button_name == "none":
                button_name = fund_id[0]["index"]

        # Get the filtered DataFrame for the selected fund and duration
        df = create_position_df(db_filename, button_name).round(2)
        if df.empty:
            return None

        # Filter the DataFrame based on the selected time period
        filtered_df = self._filter_dataframe_by_duration(df, filter_time).copy()

        # Get the start and end dates of the filtered period
        min_date = str(filtered_df["Date"].min())[0:10]
        max_date = str(filtered_df["Date"].max())[0:10]

        # Calculate total contributions up until the start of the filtered period
        filtered_df["Percentage"] = (
            filtered_df["Percentage"] - filtered_df["Percentage"].iloc[0]
        )
        start_value = filtered_df["Close"].iloc[0]
        final_value = filtered_df["Close"].iloc[-1]
        start_contrib = filtered_df["Credit"].iloc[0]
        contributions = filtered_df["Credit"].sum()
        if start_contrib > 0.0:
            contributions -= start_contrib
        earned_value = final_value - start_value - contributions

        # Final account value at the end of the filtered period
        final_value = filtered_df["Close"].iloc[-1]

        earned_percent = filtered_df["Percentage"].iloc[-1]
        # Parse the date strings into datetime objects for duration calculation
        min_date_dt = parser.parse(min_date)
        max_date_dt = parser.parse(max_date)
        difference = relativedelta(max_date_dt, min_date_dt)
        years, months, days = difference.years, difference.months, difference.days

        # Create the UI display
        return html.Div(
            [
                html.H3(f"{min_date} to {max_date}", style={"fontSize": "22px"}),
                html.H3(
                    f"Duration: {years} Years, {months} Months, {days} Days",
                    style={"fontSize": "32px"},
                ),
                html.Ul(
                    [
                        html.Li(
                            [
                                html.Span("Total Value: ", style={"fontWeight": "bold"}),
                                html.Span(
                                    f"${final_value:,.2f}", style={"fontWeight": "bold"}
                                ),
                            ],
                            style={"fontSize": "20px"},
                        ),
                        html.Li(
                            [
                                html.Span("Earned Value: "),
                                html.Span(
                                    f"${earned_value:,.2f}",
                                    style={
                                        "color": "green" if earned_value >= 0 else "red"
                                    },
                                ),
                            ],
                            style={"fontSize": "20px"},
                        ),
                        html.Li(
                            [
                                html.Span("Earned Percent: "),
                                html.Span(
                                    f"{earned_percent:,.2f}%",
                                    style={
                                        "color": "green" if earned_percent >= 0 else "red"
                                    },
                                ),
                            ],
                            style={"fontSize": "20px"},
                        ),
                    ],
                    style={"list-style-type": "none", "padding": "0"},
                ),
            ],
            style={
                "padding": "20px",
                "border": "2px solid #ddd",
                "border-radius": "10px",
                "background-color": "#f9f9f9",
            },
        )

    # ==========================================================================================
    # ==========================================================================================

    def _create_table(self, df: pd.DataFrame) -> pd.DataFrame:
        # Display the specific columns
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        dtable = dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[
                {"name": "Date", "id": "Date"},
                {"name": "Credit ($)", "id": "Credit"},
                {"name": "Close ($)", "id": "Close"},
                {"name": "Percentage (%)", "id": "Percentage"},
            ],
            fixed_rows={"headers": True},
            style_table={"overflowY": "auto", "maxHeight": "1200px"},
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
        return dtable

    # ------------------------------------------------------------------------------------------

    def _filter_dataframe_by_duration(
        self, df: pd.DataFrame, duration: str
    ) -> pd.DataFrame:
        if duration == "Total":
            return df
        latest_date = df["Date"].max()
        if duration == "YTD":
            start_date = pd.Timestamp(year=latest_date.year, month=1, day=1)
        elif duration == "1YR":
            start_date = latest_date - pd.DateOffset(years=1)
        elif duration == "3MO":
            start_date = latest_date - pd.DateOffset(months=3)
        elif duration == "1MO":
            start_date = latest_date - pd.DateOffset(months=1)
        elif duration == "1WK":
            start_date = latest_date - pd.DateOffset(weeks=1)

        filtered_df = df.loc[df["Date"] >= start_date]
        return filtered_df


# ==========================================================================================
# ==========================================================================================


def register_button_callbacks(app: Dash, manager: ButtonCallbackManager):
    app.callback(
        [Output("db-path", "data"), Output("error-message", "children")],
        Input("upload-file", "contents"),
        State("upload-file", "filename"),
    )(manager.get_filename)

    app.callback(
        [
            Output("funds-buttons", "children"),
            Output("fund-list", "data"),
            Output("error-message2", "children"),
        ],
        Input("db-path", "data"),
        allow_duplicate=True,
    )(manager.generate_fund_buttons)

    app.callback(
        Output({"type": "fund-button", "index": ALL}, "className"),
        Input({"type": "fund-button", "index": ALL}, "n_clicks"),
        State("fund-list", "data"),
        prevent_initial_call=True,
    )(manager.update_fund_button_styles)

    app.callback(
        Output({"type": "duration-button", "index": ALL}, "className"),
        Input({"type": "duration-button", "index": ALL}, "n_clicks"),
        State("duration-list", "data"),
        prevent_initial_call=True,
    )(manager.update_duration_button_styles)

    app.callback(
        [
            Output("table-container", "children"),
            Output("close-price-plot", "figure"),
            Output("candlestick-plot", "figure"),
        ],
        [
            Input({"type": "fund-button", "index": ALL}, "n_clicks"),
            Input({"type": "duration-button", "index": ALL}, "n_clicks"),
        ],
        [
            State("db-path", "data"),
            State({"type": "duration-button", "index": ALL}, "className"),
            State({"type": "duration-button", "index": ALL}, "id"),
            State({"type": "fund-button", "index": ALL}, "className"),
            State({"type": "fund-button", "index": ALL}, "id"),
        ],
    )(manager.load_and_store_data)

    app.callback(
        Output("value-display", "children"),
        [
            Input({"type": "fund-button", "index": ALL}, "n_clicks"),
            Input({"type": "duration-button", "index": ALL}, "n_clicks"),
        ],
        [
            State(
                "db-path", "data"
            ),  # Assuming you might need this for actual calculations later
            State({"type": "duration-button", "index": ALL}, "className"),
            State({"type": "duration-button", "index": ALL}, "id"),
            State({"type": "fund-button", "index": ALL}, "className"),
            State({"type": "fund-button", "index": ALL}, "id"),
        ],
        prevent_initial_call=True,
    )(manager.update_value_display)


# ==========================================================================================
# ==========================================================================================
# eof
