#!/usr/bin/env python

from requests import Session
from influxdb import InfluxDBClient
import yaml
import os


class Bootstrap(object):
    def __init__(self):
        self._influx = Influx(username=self.secrets.get('influxdb_username'),
                              password=self.secrets.get('influxdb_password'),
                              database=self.secrets.get('influxdb_database'))
        self._grafana = Grafana()

    def bootstrap(self):
        self._influx.bootstrap()
        data_sources = [
            {"name": "prometheus",
             "type": "prometheus",
             "url": "http://localhost:9090",
             "access": "direct"},
            {"name": "influxdb",
             "type": "influxdb",
             "url": "http://localhost:8086",
             "access": "direct",
             "database": self.secrets.get('influxdb_database'),
             "password": self.secrets.get('influxdb_password'),
             "username": self.secrets.get('influxdb_username')}]
        for data_source in data_sources:
            self._grafana.create_data_source(payload=data_source)
        return True

    @property
    def secrets(self):
        base_path = os.path.abspath(os.path.dirname('.'))
        secret_file = '{}/home_assistant/config/secrets.yaml'.format(base_path)
        _secrets = yaml.load(open(secret_file, 'r'))
        return _secrets


class Influx(object):
    def __init__(self, username, password, database):
        self._influx = InfluxDBClient()
        self._username = username
        self._password = password
        self._database = database

    def get_indices(self):
        self._influx.get_list_database()

    def bootstrap(self):
        print("Creating Influx resources")
        self._influx.create_database(dbname=self._database)
        self._influx.create_user(username=self._username,
                                 password=self._password)
        self._influx.grant_privilege(privilege='ALL',
                                     database=self._database,
                                     username=self._username)
        return True


class Grafana(object):
    def __init__(self, username='admin', password='admin'):
        self._session = Session()
        self._site = 'http://localhost:3000/api/datasources'
        self._username = username
        self._password = password

    def create_data_source(self, payload):
        print("Creating Grafana data source for: {}".format(payload.get('name')))
        request = self._session.post(self._site,
                                     auth=(self._username, self._password),
                                     json=payload)
        return request


if __name__ == '__main__':
    boot = Bootstrap()
    boot.bootstrap()
