import argparse


def parse_args():
    """Parse arguments"""
    parser = argparse.ArgumentParser(
        description='Watch for ConfigMaps containing prometheus configuration with specific label and read their contents and merge into final yaml file on disk.')
    parser.add_argument(
        '--label-selector',
        default="prom-rules",
        help='Label selector applied to list ConfigMaps, Default: %(default)s'
    )
    parser.add_argument(
        '--prometheus-config-file-path',
        default="/etc/config/prometheus.yml",
        help='Path where to store Prometheus config. Default: %(default)s'
    )
    parser.add_argument(
        '--logging-level',
        default="INFO",
        help='Logging level'
    )
    parser.add_argument(
        '--reload-url',
        dest='prometheus_reload_url',
        default="http://localhost:9090/-/reload",
        help='URL where to call for Prometheus reload. No call is made if empty, Default: %(default)s'
    )
    parser.add_argument(
        '--namespace',
        default="",
        help='Namespace in which to look for ConfigMaps, default is all'
    )
    args = parser.parse_args()
    return args
