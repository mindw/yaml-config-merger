from argparse import Namespace
from logging import Logger

import yaml
import sys
import signal

from kubernetes import client, config, watch
from mergedeep import Strategy, merge
from prometheus_client import start_http_server

from .log import setup_logger
from .args import parse_args
from .metrics import CONFIGMAPS_LISTING, LIST_FAILURES, CONFIGMAPS_PROCESSED, MERGED_KEYS, SKIPPED_KEYS, CONFIGURATION_SAVE_FAILURES, CONFIGURATION_ASSEMBLY, RELOAD_NOTIFICATION_FAILURES, VERSION
from . import prometheus
from . version import version


class Merger:
    prometheus_config: dict
    args: Namespace
    logger: Logger
    w_configmaps: watch.Watch
    stop: bool

    def __init__(self, ):
        self.prometheus_config = {}
        self.args = parse_args()
        self.logger = setup_logger(self.args.logging_level)
        self.w_configmaps = watch.Watch()
        self.stop = False
        # ensure we have a label is there a no errors
        VERSION.info(dict(version=version, namespace=self.args.namespace))
        CONFIGURATION_SAVE_FAILURES.labels(path=self.args.prometheus_config_file_path)
        RELOAD_NOTIFICATION_FAILURES.labels(reload_url=self.args.prometheus_reload_url)

    def cleanup(self, sig, frame):
        self.logger.info("Cleaning up watcher streams")
        self.w_configmaps.stop()
        self.stop = True
        raise Exception('Cleanup Finished')

    def start(self, ):
        self.load_kube_config()
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)

        start_http_server(8000)

        # The watcher stream tends to break a lot
        # because of that we need to recreate the task in loop
        while True:
            self.logger.info("Watching config maps")

            try:
                self.watch_config_maps()
                self.logger.info("Watching done")
            except Exception as e:
                self.logger.warning("Exception: `%s`", e)

            if self.stop:
                break

    def load_kube_config(self):
        try:
            config.load_config()
        except config.ConfigException as e:
            self.logger.critical("Cannot load kubeconfig %s", e)
            sys.exit(1)

    def load_and_merge_config(self):
        """Runs over all ConfigMaps to produce final Prometheus config and saves it"""
        v1 = client.CoreV1Api()
        try:
            with CONFIGMAPS_LISTING.time():
                config_maps: client.V1ConfigMapList
                if self.args.namespace:
                    config_maps = v1.list_namespaced_config_map(
                        namespace=self.args.namespace,
                        label_selector=self.args.label_selector
                    )
                else:
                    config_maps = v1.list_config_map_for_all_namespaces(
                        label_selector=self.args.label_selector
                    )
        except client.OpenApiException as e:
            LIST_FAILURES.inc()
            self.logger.error(e)
            return

        config_map: client.V1ConfigMap
        with CONFIGURATION_ASSEMBLY.time():
            for config_map in config_maps.items:
                # Merge data inside the ConfigMap into the final configuration
                # dictionary
                for key in config_map.data:
                    data = config_map.data[key]
                    data_yaml = yaml.safe_load(data)
                    if isinstance(data_yaml, dict):
                        self.logger.info(
                            "Key `%s` in ConfigMap `%s` is a dictionary - merging",
                            key,
                            config_map.metadata.name
                        )
                        merge(
                            self.prometheus_config,
                            data_yaml,
                            strategy=Strategy.ADDITIVE
                        )
                        MERGED_KEYS.inc()
                    else:
                        self.logger.info(
                            "Key `%s` in ConfigMap `%s` is not a dictionary - skipping merge",
                            key,
                            config_map.metadata.name
                        )
                        SKIPPED_KEYS.inc()
                CONFIGMAPS_PROCESSED.inc()

        prometheus.save_config(
            self.args.prometheus_config_file_path,
            self.prometheus_config
        )
        if self.args.prometheus_reload_url:
            prometheus.reload_prometheus(self.args.prometheus_reload_url)
        self.prometheus_config = {}

    def watch_config_maps(self):
        """Watch events on ConfigMaps with specific label and reload prometheus configuration on event"""
        v1 = client.CoreV1Api()
        event: client.CoreV1Event

        args = {
            "func": v1.list_config_map_for_all_namespaces,
            "label_selector": self.args.label_selector
        }
        if self.args.namespace:
            args = {
                "func": v1.list_namespaced_config_map,
                "namespace": self.args.namespace,
            } | args
        try:
            for event in self.w_configmaps.stream(**args):
                self.logger.info(
                    'Registered ConfigMap event `%s` on resource `%s` in namespace `%s`',
                    event['type'],
                    event['object'].metadata.name,
                    event['object'].metadata.namespace)
                self.load_and_merge_config()
        except Exception as e:
            self.logger.warning("Config map watcher exception: %s", e)
