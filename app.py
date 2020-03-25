from flask import Flask, url_for, render_template, redirect, request
from form import QueryForm, FlightIdQueryForm, MissionNameQueryForm
from data import Launch
from pandas import pandas, concat, json_normalize

import io
import base64
import matplotlib.pyplot as plt


app = Flask(__name__)
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (15, 6)
plt.rcParams['font.size'] = 10
plt.gcf().subplots_adjust(left=0.20)
enable_csrf = False
http_methods = ('GET', 'POST')
launch_data = Launch().get_data().fillna('Not available')


@app.route('/', methods=http_methods)
def query():
    """ Landing page where you can choose query type. """
    form = QueryForm(meta={'csrf': enable_csrf})
    html_file = 'index.html'
    default_choice = QueryForm.default_choice
    if request.method == 'POST':
        if form.query_type.data == default_choice:
            redirect_page = 'flight'
        elif form.query_type.data == 'mission_name_query':
            redirect_page = 'mission'
        elif form.query_type.data == 'statistics':
            redirect_page = 'statistics'
        else:
            redirect_page = 'query'
        return redirect(url_for(redirect_page))
    return render_template(html_file, form=form)


@app.route('/flight', methods=http_methods)
def flight():
    """ Route for query by flight number """
    form = FlightIdQueryForm(meta={'csrf': enable_csrf})
    html_file = 'flight.html'
    flight_id = form.flight_numbers.data
    result_df = launch_data[launch_data['flight_number'] == flight_id]

    if form.validate_on_submit():
        data = process_dataframe(result_df)
        links = json_normalize(result_df.iloc[0]['links'])
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
    mission_name = form.mission_names.data
    result_df = launch_data[launch_data['mission_name'] == mission_name]

    if form.validate_on_submit():
        data = process_dataframe(result_df)
        links = json_normalize(result_df.iloc[0]['links'])
        return render_template(
                                html_file,
                                form=form,
                                data=data.to_html(index=False),
                                mission_patch=links.iloc[0]['mission_patch_small'],
                                article_link=links.iloc[0]['article_link'],
                                wiki=links.iloc[0]['wikipedia'],
                                request_method=request.method)
    return render_template(html_file, form=form)


@app.route('/statistics', methods=http_methods)
def statistics():
    """ Route for launch statistics """
    html_file = 'statistics.html'
    flights_by_rocket_stats = flights_by_rocket()
    launch_site_location_list_stats = site_usage()
    successful_rocket_launch_stats = rocket_launch_stats()
    return render_template(
                            html_file,
                            flights_by_rocket_stats=flights_by_rocket_stats,
                            successful_rocket_launch_stats=successful_rocket_launch_stats,
                            launch_site_location_list_stats=launch_site_location_list_stats)


def rocket_launch_count():
    """ rocket count """
    rocket_info = launch_data[['rocket']].to_dict(orient='index')
    rocket_types = []
    for _, value in rocket_info.items():
        rocket_types.append(value['rocket']['rocket_name'])

    rocket_type_series = pandas.Series(rocket_types)
    rocket_type_counts = rocket_type_series.value_counts()
    return rocket_type_counts


def successful_rocket_launch_count():
    """succesful rocket count """
    successful_launches_df = launch_data[launch_data['launch_success'] == True]
    successful_rocket_info = successful_launches_df[['rocket']].to_dict(orient='index')
    successful_rocket_types = []
    for _, value in successful_rocket_info.items():
        successful_rocket_types.append(value['rocket']['rocket_name'])

    successful_rocket_type_series = pandas.Series(successful_rocket_types)
    successful_rocket_type_counts = successful_rocket_type_series.value_counts()
    return successful_rocket_type_counts


def flights_by_rocket():
    """ return flights by rocket graph """
    rocket_launches = rocket_launch_count()
    rocket_type_count_plot = rocket_launches.plot(kind='barh').get_figure()
    rocket_count_list = list(rocket_launches)
    flights_by_rocket_stats = configure_graph(
                                    series_plot=rocket_type_count_plot,
                                    title='Number of Flights by Rocket Name',
                                    x_label='Flights',
                                    y_label='Name',
                                    count_values=rocket_count_list)
    return flights_by_rocket_stats


def rocket_launch_stats():
    """ average successful launches by rocket type"""
    rocket_launch_averages = {}
    for rocket_name, rocket_count, successful_rocket_count in zip(
        rocket_launch_count().index.to_list(),
        rocket_launch_count(),
        successful_rocket_launch_count()):
        success_average = round((successful_rocket_count/rocket_count * 100), 2)
        rocket_launch_averages[rocket_name] = success_average
        rocket_launch_averages_series = pandas.Series(rocket_launch_averages)
        rocket_launch_averages_plot = rocket_launch_averages_series.plot(kind='barh').get_figure()
    rocket_launch_stats = configure_graph(
                                    series_plot=rocket_launch_averages_plot,
                                    title='Successful Launch Averages by Rocket Name',
                                    x_label='Averages (%)',
                                    y_label='Name',
                                    count_values=list(rocket_launch_averages_series))
    return rocket_launch_stats


def site_usage():
    """ return flights by rocket graph """
    launch_site_info = launch_data[['launch_site']].to_dict(orient='index')
    launch_site_locations = []

    for _, value in launch_site_info.items():
        launch_site_locations.append(value['launch_site']['site_name'])

    launch_site_locations_series = pandas.Series(launch_site_locations)
    launch_site_location_counts = launch_site_locations_series.value_counts()
    launch_site_location_count_plot = launch_site_location_counts.plot(kind='barh').get_figure()
    launch_site_location_count_list = list(launch_site_location_counts)
    launch_site_location_list_stats = configure_graph(
                                    series_plot=launch_site_location_count_plot,
                                    title='Number of times Launch Site were used',
                                    x_label='Times Used',
                                    y_label='Site',
                                    count_values=launch_site_location_count_list)
    return launch_site_location_list_stats


def process_dataframe(result_df):
    """ Logic to create combine dataframe based on
    launch success or failure. """
    fields = ['mission_name', 'launch_success', 'rocket_name', 'rocket_type', 'site_name_long']

    rocket_data_df = json_normalize(result_df.iloc[0]['rocket'])
    result_df = concat(
        [result_df, rocket_data_df],
        axis=0,
        ignore_index=True).fillna(rocket_data_df.head(1)).head(1)

    site_data_df = json_normalize(result_df.iloc[0]['launch_site'])
    result_df = concat(
        [result_df, site_data_df],
        axis=0,
        ignore_index=True).fillna(site_data_df.head(1)).head(1)

    if result_df.iloc[0]['launch_success']:
        fields.append('details')
        data = result_df[fields]
    else:
        data_df = result_df[fields]
        failure_details_df = json_normalize(result_df.iloc[0]['launch_failure_details'])
        failure_details_df = failure_details_df.rename(columns={"reason": "failure_reason", "time":"timer_time_at_failure", "altitude": "failure_altitude" })
        data = concat(
            [data_df, failure_details_df],
            axis=0,
            ignore_index=True).fillna(failure_details_df.head(1)).head(1)
    return data


def configure_graph(series_plot, title, x_label, y_label, count_values):
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(title)

    count_list = list(count_values)
    for key, value in enumerate(count_list):
        plt.text(value, key, str(value))

    buffer_obj = io.BytesIO()
    series_plot.savefig(buffer_obj, format='png')
    buffer_obj.seek(0)
    buffer = b''.join(buffer_obj)
    buffer_encoded = base64.b64encode(buffer)
    buffer_decoded = buffer_encoded.decode('utf-8')
    plt.clf()
    return buffer_decoded
