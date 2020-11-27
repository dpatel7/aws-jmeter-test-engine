#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
import re
import os
import subprocess
from dotenv import load_dotenv
from create_stack_dash import __determineLoadType
import create_dashboard
from create_stack import Config


def main(json_params):
        # Set Config values gotten from front end
    if json_params['total_users']:
        Config.total_users = json_params['total_users']
        Config.users_per_instance = Config.total_users
    if json_params['ramp_up_time']:
        Config.ramp_up_time = json_params['ramp_up_time']
    if json_params['duration']:
        Config.duration = json_params['duration']
    if json_params['icap_endpoint_url']:
        Config.icap_endpoint_url = json_params['icap_endpoint_url']
    if json_params['prefix']:
        Config.prefix = json_params['prefix']
    if json_params['load_type']:
        __determineLoadType(json_params['load_type'])

    # ensure that preserve stack and create_dashboard are at default values
    Config.preserve_stack = False
    Config.exclude_dashboard = True # update to False

    # set jmeter parameters
    with open("LocalStartExecution.sh") as f:
        script_data = f.read()

        script_data = re.sub("-Jp_vuserCount=[0-9]*", "-Jp_vuserCount=" + str(Config.users_per_instance), script_data)
        script_data = re.sub("-Jp_rampup=[0-9]*", "-Jp_rampup=" + str(Config.ramp_up_time), script_data)
        script_data = re.sub("-Jp_duration=[0-9]*", "-Jp_duration=" + str(Config.duration), script_data)
        script_data = re.sub("-Jp_url=[a-zA-Z0-9\-\.]*", "-Jp_url=" + str(Config.icap_endpoint_url), script_data)
        script_data = re.sub("-Jp_influxHost=[a-zA-Z0-9\.]*", "-Jp_influxHost=" + Config.influx_host, script_data)
        script_data = re.sub("-Jp_prefix=[A-Za-z0-9_\-]*", "-Jp_prefix=" + Config.prefix, script_data)
        script_data = re.sub("-Jp_port=[0-9]*", "-Jp_port=" + str(Config.icap_server_port), script_data)
        script_data = re.sub("-Jp_use_tls=[a-zA-Z]*", "-Jp_use_tls=" + str(Config.enable_tls), script_data)
        script_data = re.sub("-Jp_tls=[a-zA-Z0-9\-\.]*", "-Jp_tls=" + str(Config.tls_verification_method), script_data)
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(dir_path,"RunStartExecution.sh")
    with open(script_path, "w") as f:
        f.write(script_data)
    os.chmod(script_path, 0o771)
    # start execution of tests
    subprocess.Popen([script_path])

    # create dashboard
    Config.grafana_url = "http://localhost:3000/"
    dashboard_url = ""
    if Config.exclude_dashboard:
        print("Dashboard will not be created")
    else:
        print("Creating dashboard...")
        dashboard_url = create_dashboard.main(Config)

    return dashboard_url


if __name__ == "__main__":
    # test this script
    json_params = {"total_users": 4000,
                   "ramp_up_time": 180,
                   "duration": 900,
                   "icap_endpoint_url": "eu.icap.glasswall-icap.com",
                   "prefix": "ga",
                   "load_type": "Direct"}
    main(json_params)
