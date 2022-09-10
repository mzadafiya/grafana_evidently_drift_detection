# Batch ML monitoring with Evidently and Grafana

This example shows how to get real-time Grafana dashboards for monitoring data and model metrics with Evidently. 

## What's inside

We use irish datasets. Then, we configure Evidently `Dashboard` to read the data. Evidently calculates the metrics for Data Drift saves them to Postgres. The metrics are displayed on a pre-built Grafana dashboard.

Here is the one for Data Drift.


![Dashboard example](https://github.com/mzadafiya/grafana_evidently_drift_detection/blob/main/docs/images/evidently_data_drift_grafana_dashboard.png)
![Dashboard example](https://github.com/mzadafiya/grafana_evidently_drift_detection/blob/main/docs/images/evidently_data_drift_grafana_dashboard_advance.png)

You can reproduce the example locally following the instructions below and choose one or more dashboards.

You can also adapt this example to your purposes by replacing the data source and the service settings. 

## How to run an example

In this example, we use:
* `Evidently` - library for the metrics calculations
* `Postgres` - database to store the metrics
* `Grafana` - service to build the dashboards
* `Docker` - service to rule them all

Follow the instructions below to run the example:

1. **Install Docker** if you haven't used it before. 

2. **Create a new Python virtual environment and activate it**.
For example, for Linux/MacOS:
```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate 
```
3. **Get the `evidently` code example**:
```bash
git clone git@github.com:evidentlyai/evidently.git
```

4. **Install dependencies**.

- Go to the example directory:
```bash
cd evidently/examples/integrations/grafana_monitoring_service/
```
- install dependencies for the example run script
```bash
pip install -r requirements.txt
```

5. **Then run the docker image from the example directory**:
```bash
./main.py
```
This will:
- download and prepare the test data - `irish` on the first run.
- run Postgres, Grafana, and Evidently Dashboard service in Docker

The services will be available in your system:
  - **Postgres** at port 5432. To access Postgres web interface
  - **Grafana** at port 3000. To access Grafana web interface, go to your browser and open: http://localhost:3000/

- send the production data from the test datasets to the Evidently monitoring service (row by row)


6. **Explore the dashboard**.
 
Go to the browser and access the Grafana dashboard at http://localhost:3000. At first, you will be asked for login and password. Both are `admin`. 

To see the monitoring dashboard in the Grafana interface, click "General" and navigate to the chosen dashboard (e.g. "Evidently Data Drift").
