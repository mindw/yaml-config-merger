from prometheus_client import Counter, Histogram, Info

PREFIX = "prometheus_config_merger"

VERSION = Info(
    "version",
    documentation="Prometheus Config Merger version",
    namespace=PREFIX
)

CONFIGMAPS_LISTING = Histogram(
    "configmap_listing",
    documentation="Distribution of the time spent in listing selected configmaps",
    unit="seconds",
    namespace=PREFIX
)

CONFIGURATION_ASSEMBLY = Histogram(
    "configuration_assembly",
    documentation="Distribution of the time spent in assembling configuration from the configmaps",
    unit="seconds",
    namespace=PREFIX
)

WATCH_FAILURES = Counter(
    "watch_failures",
    documentation="Number of times Kuberntes watch generated an exception",
    namespace=PREFIX
)

LIST_FAILURES = Counter(
    "list_failures",
    documentation="Number of failures to list configmaps",
    namespace=PREFIX
)

MERGED_KEYS = Counter(
    "merged_configmap_keys",
    "Total number of configmap keys merged into the configuration",
    namespace=PREFIX,
)

SKIPPED_KEYS = Counter(
    "skipped_configmap_keys",
    "Total number of configmap keys skipped and were not merged into the configuration",
    namespace=PREFIX,
)

CONFIGMAPS_PROCESSED = Counter(
    "configmaps_processed",
    "Total number of configmaps processed",
    namespace=PREFIX
)

CONFIGURATION_SAVE_FAILURES = Counter(
    "configuration_save_failures",
    "Total number of configuration save failures",
    namespace=PREFIX,
    labelnames=['path']
)

RELOAD_NOTIFICATION_FAILURES = Counter(
    "reload_notification_failures",
    "Total number of times notification calls failures",
    namespace=PREFIX,
    labelnames=['reload_url']
)
