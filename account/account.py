# Import necessary packages here

import dash
from dash import Input, Output, dcc, html

# ==========================================================================================
# ==========================================================================================

# File:    account.py
# Date:    April 09, 2024
# Author:  Jonathan A. Webb
# Purpose: This file integrates the various functions and classes required for the
#          account package
# ==========================================================================================
# ==========================================================================================
# Create a Dash application

# Create a Dash application
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        # Left column
        html.Div(
            [
                # File upload component with CSS class
                dcc.Upload(
                    id="upload-file",
                    children=html.Button("Upload File", className="upload-button"),
                    # Allow multiple files to be uploaded
                    multiple=False,
                ),
                # Container to display the file name or path
                html.Div(id="file-info"),
            ],
            className="left-column",
        ),  # Use CSS class for styling
        # Right column
        html.Div(
            [
                # Content for the right column
                html.P("This is the right column content.")
            ],
            className="right-column",
        ),  # Use CSS class for styling
    ],
    id="container",
)


@app.callback(Output("file-info", "children"), [Input("upload-file", "filename")])
def update_output(uploaded_filename):
    if uploaded_filename is not None:
        # Handle the file as needed
        return html.Div(
            [
                html.P(f"File selected: {uploaded_filename}"),
            ]
        )
    else:
        return "No file selected."


if __name__ == "__main__":
    app.run(debug=True)

# ==========================================================================================
# ==========================================================================================
# eof
