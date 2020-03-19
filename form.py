from data import Launch
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField


class QueryForm(FlaskForm):
    """Flight ID Query Form"""
    default_choice = 'flight_number_query'
    query_choices = [(default_choice, default_choice),
                     ('mission_name_query', 'mission_name_query'),
                     ('statistics', 'statistics')]
    query_type = SelectField('Select: ', choices=query_choices, default=default_choice)
    submit = SubmitField('Submit')


class FlightIdQueryForm(FlaskForm):
    """Flight ID Query Form"""
    launch_data = Launch().get_data()
    result_series = list(launch_data['flight_number'])
    default_flight_number = 1
    flight_number_choices = list(zip(result_series, result_series))
    flight_numbers = SelectField('Flight Number: ', choices=flight_number_choices, default=default_flight_number, coerce=int)
    submit = SubmitField('Submit')


class MissionNameQueryForm(FlaskForm):
    """Mission Name Query Form"""
    launch_data = Launch().get_data()
    result_series = list(launch_data['mission_name'])
    mission_name_choices = list(zip(result_series, result_series))
    mission_names = SelectField('Mission Name: ', choices=mission_name_choices)
    submit = SubmitField('Submit')
