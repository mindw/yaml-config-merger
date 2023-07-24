import logging
from pathlib import Path

import urllib3
import yaml

from .metrics import CONFIGURATION_SAVE_FAILURES, RELOAD_NOTIFICATION_FAILURES

logger = logging.getLogger(__name__)


def multi_line_str_presenter(dumper, data):
    style = '|' if '\n' in data else None
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)


yaml.add_representer(str, multi_line_str_presenter, yaml.CDumper)


def reload_prometheus(url):
    """Do post on Prometheus endpoint to reload it"""
    try:
        urllib3.request(method="POST", url=url, retries=False)
    except Exception as e:
        RELOAD_NOTIFICATION_FAILURES.labels(reload_url=url).inc()
        logger.warning("POST to prometheus url failed with exception `%s`", e)


def save_config(path, config):
    """Save prometheus config to file"""
    try:
        Path(path).write_text(yaml.dump(config, Dumper=yaml.CDumper), encoding='utf8')
    except Exception as e:
        CONFIGURATION_SAVE_FAILURES.labels(path=path).inc()
        logger.error("Failed writing prometheus file `%s`, %s", path, e)
