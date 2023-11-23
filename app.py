import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output
from scipy.special import expit  # Logistic function

import base64
import io

# Read the image file
image_path = "logo.png"
with open(image_path, "rb") as img_file:
    encoded_image = base64.b64encode(img_file.read()).decode('ascii')


# Instead of dash.Dash, use JupyterDash
# Instead of JupyterDash, use the standard Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


# Link to your CSS stylesheet
app.css.append_css({"external_url": "style.css"})

import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output
from scipy.special import expit  # Logistic function

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        # Include the Google Fonts link
        html.Link(
            rel='stylesheet',
            href='https://fonts.googleapis.com/css2?family=Quicksand:wght@400;700&display=swap',
        ),
        html.Div(
            [
                dbc.Col(html.Img(src=f"data:image/png;base64,{encoded_image}", className="logo")),
                dbc.Row(dbc.Col(html.H1("CroWalker: Cranial-trait based sex-estimator for Croatian population", className="title"))),
            ],
            className="title-container"
        ),
        html.Div(
            dbc.Row(dbc.Col(html.P("This app was developed on the modern Croatian population MSCT scans on a sample of 200 individuals. It uses four morphological traits: nuchal crest, mastoid process, supraorbital edge, and glabella for evidence-based sex estimation based on logistic regression equations. According to the number of traits entered, the app provides all possible combinations of variables (up to 15 of them) and sorts them by accuracy. Users can obtain the probability of an individual being male or female and the final sex classification.", className="description"))),
            className="description-container"
        ),
        html.Div(
            [
                dbc.Row(
                    dbc.Col(
                        dcc.Markdown(
                            '''
                            **Instruction:** The traits should be scored according to the descriptions available in [MorphoPASSE user manual](https://www.morphopasse.com/uploads/8/4/0/8/8408493/klales_nij_database_manual_v1_03.29.19_on_website.pdf).
                            '''
                        ),
                        className="mb-3"
                    ),
                ),

                dbc.Row(
                    [
                        dbc.Col(html.Div([
                            html.Label("Glabella (1-5):", className="form-label"),
                            dcc.Input(id='input-glabella', type='number', min=1, max=5, step=1, className='form-control input-glabella'),
                        ]), md=3),
                        
                        dbc.Col(html.Div([
                            html.Label("Supraorbital Edge (1-5):", className="form-label"),
                            dcc.Input(id='input-supraorbital', type='number', min=1, max=5, step=1, className='form-control input-supraorbital'),
                        ]), md=3),

                        dbc.Col(html.Div([
                            html.Label("Mastoid Process (1-5):", className="form-label"),
                            dcc.Input(id='input-mastoid', type='number', min=1, max=5, step=1, className='form-control input-mastoid'),
                        ]), md=3),

                        dbc.Col(html.Div([
                            html.Label("Nuchal Crest (1-5):", className="form-label"),
                            dcc.Input(id='input-nuchal', type='number', min=1, max=5, step=1, className='form-control input-nuchal'),
                        ]), md=3),
                    ],
                    className="mb-3"
                ),
                dbc.Row(
                    dbc.Col(html.Button('SUBMIT', id='submit-val', n_clicks=0, className='btn btn-lg btn-primary btn-block custom-submit-btn'), className="d-flex justify-content-center"),
                    className="submit-button-row"
                ),
                dbc.Row(dbc.Col(html.Div(id='container-button-basic'), width=12))
            ],
            className="form-results-container"
        )
    ],
    fluid=True,
    className="main-container"
)


# Function to calculate probability using a logistic regression equation
def calculate_probability(intercept, coefficients, inputs):
    logit_p = intercept + sum(c * i for c, i in zip(coefficients, inputs))
    probability = expit(logit_p)
    return probability

model_accuracy_mapping = {
    "Glabella": "78.75%",
    "Supraorbital Edge": "62.50%",
    "Mastoid Process": "70.00%",
    "Nuchal Crest": "75.00%",
    "Glabella, Supraorbital Edge": "80.00%",
    "Glabella, Mastoid Process": "86.25%",
    "Glabella, Nuchal Crest": "80.00%",
    "Supraorbital Edge, Mastoid Process": "72.50%",
    "Supraorbital Edge, Nuchal Crest": "75.00%",
    "Mastoid Process, Nuchal Crest": "80.00%",
    "Glabella, Supraorbital Edge, Mastoid Process": "86.25%",
    "Glabella, Supraorbital Edge, Nuchal Crest": "81.25%",
    "Glabella, Mastoid Process, Nuchal Crest": "86.25%",
    "Supraorbital Edge, Mastoid Process, Nuchal Crest": "80.00%",
    "Glabella, Supraorbital Edge, Mastoid Process, Nuchal Crest": "85.00%"
}


@app.callback(
    Output('container-button-basic', 'children'),
    [Input('submit-val', 'n_clicks')],
    [Input('input-glabella', 'value'),
     Input('input-supraorbital', 'value'),
     Input('input-mastoid', 'value'),
     Input('input-nuchal', 'value')]
)
def update_output(n_clicks, glabella, supraorbital, mastoid, nuchal):
    if n_clicks > 0:
        inputs = [glabella, supraorbital, mastoid, nuchal]
        active_inputs = [i for i in inputs if i is not None]
        num_inputs = len(active_inputs)

        # Helper function to format the result
        def format_result(model_desc, intercept, coefficients, active_inputs):
            probability = calculate_probability(intercept, coefficients, active_inputs)
            male_prob = probability
            female_prob = 1 - male_prob
            classification = "Male" if male_prob >= 0.5 else "Female"
            accuracy = model_accuracy_mapping.get(model_desc, "N/A")
            return f"{model_desc}: Male Probability: {male_prob:.2f}, Female Probability: {female_prob:.2f}, Classified as: {classification}, Accuracy: {accuracy}"

        results = []
        # Logic to handle all possible combinations based on the number of active inputs
        if num_inputs == 4:
            desc = "Glabella, Supraorbital Edge, Mastoid Process, Nuchal Crest"
            results.append(format_result(desc, -7.6727, [1.1666, -0.2110, 0.5406, 0.9516], active_inputs))

        if num_inputs >= 3:
            if glabella is not None and supraorbital is not None and mastoid is not None:
                desc = "Glabella, Supraorbital Edge, Mastoid Process"
                results.append(format_result(desc, -5.9676, [1.3673, -0.0387, 0.6138], active_inputs))
            if glabella is not None and supraorbital is not None and nuchal is not None:
                desc = "Glabella, Supraorbital Edge, Nuchal Crest"
                results.append(format_result(desc, -6.7624, [1.2551, -0.1390, 1.0196], active_inputs))
            if glabella is not None and mastoid is not None and nuchal is not None:
                desc = "Glabella, Mastoid Process, Nuchal Crest"
                results.append(format_result(desc, -8.0062, [1.1358, 0.5101, 0.8901], active_inputs))
            if supraorbital is not None and mastoid is not None and nuchal is not None:
                desc = "Supraorbital Edge, Mastoid Process, Nuchal Crest"
                results.append(format_result(desc, -6.3187, [-0.0154, 0.6735, 1.3026], active_inputs))

        if num_inputs >= 2:
            if glabella is not None and supraorbital is not None:
                desc = "Glabella, Supraorbital Edge"
                results.append(format_result(desc, -4.7607, [1.4994, 0.0573], active_inputs))
            if glabella is not None and mastoid is not None:
                desc = "Glabella, Mastoid Process"
                results.append(format_result(desc, -6.0535, [1.3590, 0.6074], active_inputs))
            if glabella is not None and nuchal is not None:
                desc = "Glabella, Nuchal Crest"
                results.append(format_result(desc, -7.0131, [1.2296, 0.9769], active_inputs))
            if supraorbital is not None and mastoid is not None:
                desc = "Supraorbital Edge, Mastoid Process"
                results.append(format_result(desc, -3.4673, [0.2704, 0.8280], active_inputs))
            if supraorbital is not None and nuchal is not None:
                desc = "Supraorbital Edge, Nuchal Crest"
                results.append(format_result(desc, -5.0749, [0.1148, 1.4276], active_inputs))
            if mastoid is not None and nuchal is not None:
                desc = "Mastoid Process, Nuchal Crest"
                results.append(format_result(desc, -6.3412, [0.6703, 1.2966], active_inputs))

        if num_inputs >= 1:
            if glabella is not None:
                desc = "Glabella"
                results.append(format_result(desc, -4.6169, [1.5150], [glabella]))
            if supraorbital is not None:
                desc = "Supraorbital Edge"
                results.append(format_result(desc, -1.4934, [0.4515], [supraorbital]))
            if mastoid is not None:
                desc = "Mastoid Process"
                results.append(format_result(desc, -2.7615, [0.8905], [mastoid]))
            if nuchal is not None:
                desc = "Nuchal Crest"
                results.append(format_result(desc, -4.8597, [1.4784], [nuchal]))


        # Sorting the results based on accuracy
        sorted_results = sorted(results, key=lambda x: float(model_accuracy_mapping.get(x.split(":")[0], "0%").split('%')[0]), reverse=True)

        # Create a table for the results
        table_header = [html.Thead(html.Tr([html.Th("Feature"), html.Th("Male Probability"), html.Th("Female Probability"), html.Th("Decision"), html.Th("Accuracy")]))]
        table_body_rows = []

        for result in sorted_results:
            model_desc, result_details = result.split(": ", 1)
            male_prob, female_prob, classification, accuracy = [detail.split(": ")[1] for detail in result_details.split(", ")]

            # Process each feature for coloring
            feature_html = process_features_for_coloring(model_desc)

            # Append row to table body
            table_body_rows.append(html.Tr([
                html.Td(feature_html, className="label-cell"),
                html.Td(male_prob),
                html.Td(female_prob),
                html.Td(classification),
                html.Td(accuracy)
            ]))

        table_body = [html.Tbody(table_body_rows)]
        return html.Table(table_header + table_body, className="results-table")

    return None

def process_features_for_coloring(model_desc):
    feature_classes = {
        "Glabella": "label-glabella",
        "Supraorbital Edge": "label-supraorbital-edge",
        "Mastoid Process": "label-mastoid-process",
        "Nuchal Crest": "label-nuchal-crest"
    }
    feature_labels = []
    for feature in model_desc.split(", "):
        class_name = feature_classes.get(feature, "feature-label")
        feature_labels.append(html.Span(feature, className=class_name))
    return feature_labels


if __name__ == '__main__':
    app.run_server(debug=False)
