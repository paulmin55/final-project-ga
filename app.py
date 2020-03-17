from flask import Flask, url_for, render_template, redirect, request
from form import QueryForm, FlightIdQueryForm, MissionNameQueryForm
from data import Launch
from pandas import concat, json_normalize

app = Flask(__name__)
enable_csrf = False
http_methods = ('GET', 'POST')


@app.route('/', methods=http_methods)
def query():
    """ Landing page where you can choose query type. """
    form = QueryForm(meta={'csrf': enable_csrf})
    html_file = 'index.html'
    default_choice = QueryForm.default_choice
    if request.method == 'POST':
        if form.query_type.data == default_choice:
            redirect_page = 'flight'
        else:
            redirect_page = 'mission'
        return redirect(url_for(redirect_page))
    return render_template(html_file, form=form)


@app.route('/flight', methods=http_methods)
def flight():
    """ Route for query by flight number """
    form = FlightIdQueryForm(meta={'csrf': enable_csrf})
    html_file = 'flight.html'
    launch_data = Launch().get_data()
    flight_id = form.flight_numbers.data
    result_df = launch_data[launch_data['flight_number'] == flight_id]

    if form.validate_on_submit():
        data = process_dataframe(result_df)
        links = process_dataframe_links(result_df)
        return render_template(
                                html_file,
                                form=form,
                                data=data.to_html(index=False),
                                mission_patch=links.iloc[0]['mission_patch_small'],
                                article_link=links.iloc[0]['article_link'],
                                wiki=links.iloc[0]['wikipedia'],
                                request_method=request.method)
    return render_template(html_file, form=form)


@app.route('/mission', methods=http_methods)
def mission():
    """ Route for query by Mission Name """
    form = MissionNameQueryForm(meta={'csrf': enable_csrf})
    html_file = 'mission.html'
    launch_data = Launch().get_data()
    mission_name = form.mission_names.data
    result_df = launch_data[launch_data['mission_name'] == mission_name]

    if form.validate_on_submit():
        data = process_dataframe(result_df)
        links = process_dataframe_links(result_df)
        return render_template(
                                html_file,
                                form=form,
                                data=data.to_html(index=False),
                                mission_patch=links.iloc[0]['mission_patch_small'],
                                article_link=links.iloc[0]['article_link'],
                                wiki=links.iloc[0]['wikipedia'],
                                request_method=request.method)
    return render_template(html_file, form=form)


def process_dataframe(result_df):
    """ Logic to create combine dataframe based on
    launch success or failure. """
    if result_df.iloc[0]['launch_success']:
        data = result_df[['mission_name', 'launch_success', 'details']]
    else:
        data_df = result_df[['mission_name', 'launch_success']]
        failure_details_df = json_normalize(result_df.iloc[0]['launch_failure_details'])
        data = concat(
            [data_df, failure_details_df],
            axis=0,
            ignore_index=True).fillna(failure_details_df.head(1)).head(1)
    return data


def process_dataframe_links(result_df):
    """ Extracts links """
    links = json_normalize(result_df.iloc[0]['links'])
    return links
