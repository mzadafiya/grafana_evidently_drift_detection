import psycopg2
from psycopg2.extras import execute_values

from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import (
    DataDriftTab,
)


import numpy
from psycopg2.extensions import register_adapter, AsIs


def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)


def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)


register_adapter(numpy.float64, addapt_numpy_float64)
register_adapter(numpy.int64, addapt_numpy_int64)


def dashboard_data(self):
    tab_widgets = [t.info() for t in self.stages]
    dashboard_info = [item.params for tab in tab_widgets for item in tab if item is not None]
    additional_graphs = {}
    for widget in [item for tab in tab_widgets for item in tab]:
        if widget is None:
            continue
        for graph in widget.get_additional_graphs():
            additional_graphs[graph.id] = graph.params
    return dashboard_info, additional_graphs


def load_drift_data(reference_data, current_data):
    TABS = [DataDriftTab(verbose_level=1)]

    iris_target_drift_dashboard = Dashboard(tabs=TABS)
    iris_target_drift_dashboard.calculate(reference_data, current_data, column_mapping=None)
    return dashboard_data(iris_target_drift_dashboard)


COLUMNS = {
    "f1": "Feature",
    "f6": "Type",
    "f3": "Reference Distribution",
    "f4": "Current Distribution",
    "f2": "Data Drift",
    "stattest_name": "Stat Test",
    "f5": "Drift Score"
}


def transform(date, dashboard_info, additional_graphs):

    drift_table_columns = ['Datetime', "Feature", "Type", "Data Drift", "Stat Test", "Drift Score"]
    distribution_columns = ['Datetime', "Feature", "Type", "Distribution Type", "x", "y"]
    drift_chart_columns = ['Datetime', "Feature", "x", "y1", "y2", "y3"]
    data_distr_columns = ['Datetime', "Feature", "Type", "x"]

    drift_table_query = "INSERT INTO drift_table ({}) VALUES %s".format(','.join(f'"{w}"' for w in drift_table_columns))
    drift_table_data = []

    distribution_query = "INSERT INTO distribution ({}) VALUES %s".format(
        ','.join(f'"{w}"' for w in distribution_columns))
    distribution_data = []

    drift_chart_query = "INSERT INTO drift_chart ({}) VALUES %s".format(','.join(f'"{w}"' for w in drift_chart_columns))
    drift_chart_data = []

    data_distr_query = "INSERT INTO data_distr ({}) VALUES %s".format(','.join(f'"{w}"' for w in data_distr_columns))
    data_distr_data = []

    for widget in dashboard_info:

        for data in widget["data"]:
            feature = data['f1']
            type = data['f6']

            drift_table_data.append([date, feature, type, data['f2'], data['stattest_name'], data['f5']])

            for distribution in ['f3', 'f4']:
                for x, y in zip(data[distribution]['x'], data[distribution]['y']):
                    distribution_data.append([date, feature, type, COLUMNS[distribution], x, y])

    for key, value in additional_graphs.items():
        feature = key[:-6]

        if key.endswith('_distr'):
            for data in value["data"]:
                type = data["name"]
                for x in data['x']:
                    data_distr_data.append([date, feature, type, x])

        elif key.endswith('_drift'):
            data = value['params']['data']
            y2 = data[1]['y'][0]
            y3 = data[1]['y'][1]

            for x, y1 in zip(data[0]['x'], data[0]['y']):
                drift_chart_data.append([date, feature, x, y1, y2, y3])

    return [
        (drift_table_query, drift_table_data),
        (distribution_query, distribution_data),
        (drift_chart_query, drift_chart_data),
        (data_distr_query, data_distr_data)
    ]


def insert_data(query_data, force):
    conn = psycopg2.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port='5432')

    cur = conn.cursor()

    commands = []

    if force:
        commands += [
            "DROP TABLE IF EXISTS drift_table;",
            "DROP TABLE IF EXISTS distribution;",
            "DROP TABLE IF EXISTS drift_chart;",
            "DROP TABLE IF EXISTS data_distr;"
        ]

    commands += [
        """
        CREATE TABLE IF NOT EXISTS drift_table (
            "Datetime" TIMESTAMP NOT NULL,
            "Feature" VARCHAR(255) NOT NULL,
            "Type" VARCHAR(255) NOT NULL,
            "Data Drift" VARCHAR(255) NOT NULL,
            "Stat Test" VARCHAR(255) NOT NULL,
            "Drift Score" NUMERIC NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS distribution (
            "Datetime" TIMESTAMP NOT NULL,
            "Feature" VARCHAR(255) NOT NULL,
            "Type" VARCHAR(255) NOT NULL,
            "Distribution Type" VARCHAR(255) NOT NULL,
            "x" NUMERIC NOT NULL,
            "y" NUMERIC NOT NULL
            )
        """,
        """
        CREATE TABLE IF NOT EXISTS drift_chart (
            "Datetime" TIMESTAMP NOT NULL,
            "Feature" VARCHAR(255) NOT NULL,
            "x" NUMERIC NOT NULL,
            "y1" NUMERIC NOT NULL,
            "y2" NUMERIC NOT NULL,
            "y3" NUMERIC NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS data_distr (
            "Datetime" TIMESTAMP NOT NULL,
            "Feature" VARCHAR(255) NOT NULL,
            "Type" VARCHAR(255) NOT NULL,
            "x" NUMERIC NOT NULL
        )
        """
    ]

    for command in commands:
        cur.execute(command)

    for query, data in query_data:
        execute_values(cur, query, data)

    cur.close()

    # commit changes
    conn.commit()
    # Close the connection
    conn.close()
