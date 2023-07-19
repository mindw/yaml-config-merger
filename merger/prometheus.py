import requests
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


def reload_prometheus(url):
    """Do post on Prometheus endpoint to reload it"""
    try:
        requests.post(url=url)
    except Exception as e:
        logger.warning("POST to prometheus url failed with exception `%s`", e)


def save_config(path, config):
    """Save prometheus config to file"""
    try:
        Path(path).write_text(yaml.dump(config), encoding='utf8')
    except Exception as e:
        logger.error(e)
