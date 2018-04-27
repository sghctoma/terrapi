#!/usr/bin/env python3

import json
import logging
import pkg_resources
import pytz
import sys
import tzlocal
import yaml
from datetime import datetime, timedelta
from os.path import expanduser, isfile

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

from .db import create_sessionmaker, Measurement, Sensor, SensorType


colors = [
    "#1f77b4",
    "#7f7f7f",
    "#17becf",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#bcbd22"
]


app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1('TerraPi dashboard'),
    dcc.Interval(
        id = 'interval-component',
        interval = 5 * 60 * 1000,
        n_intervals = 0
    ),
    html.Div(id='intermediate-value', style={'display': 'none'})
])


def generate_update_func(sensor_type):
    def update_graph_live(measurements_json, relayout_data):
        global sensors

        m = json.loads(measurements_json)
        sensor_ids = [s.id for s in sensors if s.type==sensor_type]
        data = []
        i = 0
        for sensor_id in sensor_ids:
            data.append(go.Scatter(
                x = m[str(sensor_id)]['timestamp'],
                y = m[str(sensor_id)]['value'],
                name = [s.name for s in sensors if s.id==sensor_id][0],
                mode = 'lines',
                line = dict(color=colors[i%len(colors)])
            ))
            i = i + 1

        layout = go.Layout(
            title = sensor_type.name.capitalize(),
            margin = dict(l=60, r=60, b=30, t=30),
            legend = dict(x=0, y=1, xanchor='left'),
            xaxis = dict(
                type = 'date',
                range = [
                    relayout_data['xaxis.range[0]'],
                    relayout_data['xaxis.range[1]']
                ] if 'xaxis.range[0]' in relayout_data else None,
                rangeselector = dict(
                    buttons = list([
                        dict(count=1, label='1 day', step='day', stepmode='backward'),
                        dict(count=7, label='1 week', step='day', stepmode='backward'),
                        dict(count=1, label='1 month', step='month', stepmode='backward'),
                        dict(step='all')
                    ])
                ),

            ),
            yaxis = dict(fixedrange = True)
        )

        return go.Figure(layout=layout, data=data)

    return update_graph_live


@app.callback(
    Output('intermediate-value', 'children'),
    [Input('interval-component', 'n_intervals')])
def update_measurements(n):
    global sensors
    global sessionmaker

    measurements = dict()
    session = sessionmaker()
    one_day = timedelta(hours=30*24)
    local_tz = tzlocal.get_localzone()

    for sensor in sensors:
        measurements[sensor.id] = dict()
        _data = session.query(Measurement).filter(
                Measurement.sensor==sensor).filter(
                Measurement.timestamp>datetime.now()-one_day).order_by(
                Measurement.timestamp).all()
        measurements[sensor.id]['timestamp'] = [
                m.timestamp.replace(tzinfo=pytz.utc).astimezone(local_tz) for m in _data]
        measurements[sensor.id]['value'] = [m.value for m in _data]

    session.close()
    
    return json.dumps(measurements, default=str)


def get_connection_string():
    config_paths = []
    if len(sys.argv) > 1:
        config_paths.append(sys.argv[1])
    config_paths.append(expanduser('~') + '/.terrapi.yaml')
    config_paths.append(expanduser('~') + '/.config/terrapi/config.yaml')
    config_paths.append(pkg_resources.resource_filename('TerraPi',
        'conf/config-sample.yaml'))
    for path in config_paths:
        if isfile(path):
            configfile = path
            break
    if not configfile:
        logging.error("No config file found! Exiting..")
        sys.exit(1)
    with open(configfile, 'r') as stream:
        config = yaml.load(stream)
    if not config:
        logging.error("Empty configuration! Exiting...")
        sys.exit(1)

    connection_string = config.get('connection_string')
    if not connection_string:
        logging.info("Database configuration not found, using SQLite.")
        database = pkg_resources.resource_filename('TerraPi','data/terrapi.db')
        connection_string = 'sqlite:///%s' % database

    return connection_string


def main():
    global sensors
    global sessionmaker

    connection_string = get_connection_string()
    sessionmaker = create_sessionmaker(connection_string)

    session = sessionmaker()
    sensors = session.query(Sensor).all()
    for s in sensors:
        app.layout.children.append(
                html.Div(
                    children = dcc.Graph(id = s.type.name),
                    style = dict(
                        marginBottom = 80,
                        marginTop = 80)
                ))
    session.close()

    for st in set([s.type for s in sensors]):
        app.callback(
            Output(st.name, 'figure'),
            [Input('intermediate-value', 'children')],
            [State(st.name, 'relayoutData')]
        )(generate_update_func(st))

    app.run_server(debug=True)


if __name__ == '__main__':
    main()
