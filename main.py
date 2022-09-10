#!/usr/bin/env python3

import argparse
import os
import logging
import subprocess
import time
import pandas as pd

from sklearn import datasets
from datetime import date, timedelta

from src.scripts.load_evidently_dashboard import load_drift_data, transform, insert_data


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )


def check_docker_installation():
    logging.info("Check docker version")
    docker_version_result = os.system("docker -v")

    if docker_version_result:
        exit("Docker was not found. Try to install it with https://www.docker.com")


def load_dataframe(dataset):
    logging.info("Load dataframe from dataset")
    return pd.DataFrame(dataset.data, columns=dataset.feature_names)


def run_docker_compose():
    logging.info("Run docker compose")
    run_script(cmd=["docker", "compose", "up", "-d"], wait=True)


def run_script(cmd: list, wait: bool) -> None:
    logging.info("Run %s", ' '.join(cmd))
    script_process = subprocess.Popen(' '.join(cmd), stdout=subprocess.PIPE, shell=True)

    if wait:
        script_process.wait()

        if script_process.returncode != 0:
            exit(script_process.returncode)


def main(force: bool):
    setup_logger()
    check_docker_installation()

    dataset = datasets.load_iris()
    dataframe = load_dataframe(dataset)

    query_data = []

    day = date.today()
    for i in range(1, 149, 1):
        day = day - timedelta(1)
        dashboard_info, additional_graphs = load_drift_data(dataframe[:i], dataframe[i:])
        query_data += transform(day, dashboard_info, additional_graphs)

    run_docker_compose()
    time.sleep(4)
    insert_data(query_data, force)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script for data and config generation for demo Evidently Dashboard integration with Grafana"
    )
    parser.add_argument(
        "-f",
        "--force",
        action='store_true',
        help="Remove and download again test datasets",
    )
    parameters = parser.parse_args()
    main(force=parameters.force)
