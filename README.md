# Yaml Config Merger
Sidecar to merge Yaml snippets from multiple ConfigMaps and save it to file.

Exposes metrics on (configurable) port `http://0.0.0.0:9980/`.

Originally conceived as a sidecar for Prometheus, it can be used with anything
consuming a yaml configuration file.

## How does it work
1. Watch the changes to configmaps with specific label.
2. On any change get the contents from all watched ConfigMaps.
3. Merge the content together as yaml.
4. Write the yaml content to file.
5. Hit Prometheus reload API to reload the file.

## How to run
Setup Python environment the standard way:

```bash
poetry install
```

Run the program:

```bash
poetry run python -m merger \
        --prometheus-config-file-path 'my-test-config.yaml' \
        --label-selector='prom-rules.yaml' \
        --namespace 'monitoring' \
        --reload-url 'http://localhost:9090/-/reload'
```

## Integrating with Prometheus Community helm chart
If you want to use this sidecar with [prometheus-community helm chart](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus),
you need to add this container as a sidecar, create common volume and mount it.

Here is example:

```yaml
server:
  sidecarContainers:
    prometheus-config-merger:
      image: mindw/yaml-config-merger:0.2.0
      imagePullPolicy: IfNotPresent
      args:
      - --prometheus-config-file-path=/etc/config-prometheus/prometheus.yml
      - --label-selector='prom-rules' \
      - --namespace 'monitoring' \
      - --reload-url 'http://localhost:9090/-/reload'
      volumeMounts:
      - name: prometheus-merged-config
        mountPath: /etc/config-prometheus/

  extraVolumeMounts:
  - name: prometheus-merged-config
    mountPath: /etc/config-prometheus/

  extraVolumes:
  - name: prometheus-merged-config
    emptyDir: {}

  configPath: /etc/config-prometheus/prometheus.yml
```
