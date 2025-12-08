#!/bin/bash
set -e

# Minimal Elasticsearch test - only runs ES, MongoDB, and basic services
# This uses ~4GB RAM instead of ~16GB for the full stack

echo "Starting minimal test environment (ES + MongoDB only)..."

cd /home/mrabbah/Documents/srm-cs/runner-src/backend/tests

# Start only essential services
docker compose up -d postgres mongo registry

# Wait for registry
sleep 5

# Start single-node k3d cluster (not multi-node)
k3d cluster create test-minimal --registry-use test-registry.test.local:8443 \
  --k3s-arg "--disable=traefik" --wait

# Connect to registry network
docker network connect tests_default k3d-test-minimal-server-0 2>/dev/null || true
REGISTRY_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dev-registry)
docker exec k3d-test-minimal-server-0 sh -c "echo '$REGISTRY_IP test-registry.test.local' >> /etc/hosts"

# Render and apply only Elasticsearch
kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: apim
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: elasticsearch-index
  namespace: apim
spec:
  replicas: 1  # Single node for minimal test
  serviceName: elasticsearch-db-index
  template:
    spec:
      containers:
      - name: elasticsearch
        image: test-registry.test.local:8443/elasticsearch:7.16.2
        env:
        - name: node.name
          value: elasticsearch-index-0
        - name: cluster.name
          value: search-engine-cluster
        - name: discovery.seed_hosts
          value: elasticsearch-index-0.elasticsearch-db-index
        - name: cluster.initial_master_nodes
          value: elasticsearch-index-0
        - name: network.host
          value: 0.0.0.0
        - name: ES_JAVA_OPTS
          value: -Xms3072m -Xmx3072m -Des.allow_insecure_settings=true
        - name: http.cors.enabled
          value: "true"
        - name: http.cors.allow-origin
          value: '*'
        - name: transport.host
          value: 0.0.0.0
        resources:
          requests:
            cpu: 100m
            memory: 3072Mi
          limits:
            cpu: 1
            memory: 4096Mi
        ports:
        - containerPort: 9200
          name: http
      initContainers:
      - name: fix-permissions
        image: test-registry.test.local:8443/busybox:latest
        command: [sh, -c, 'chown -R 1000:1000 /usr/share/elasticsearch/data']
        securityContext:
          privileged: true
          runAsUser: 0
        volumeMounts:
        - mountPath: /usr/share/elasticsearch/data
          name: data
      - name: increase-vm-max-map
        image: test-registry.test.local:8443/busybox:latest
        command: [sysctl, -w, vm.max_map_count=262144]
        securityContext:
          privileged: true
          runAsUser: 0
      - name: increase-fd-ulimit
        image: test-registry.test.local:8443/busybox:latest
        command: [sh, -c, 'ulimit -n 65536']
        securityContext:
          privileged: true
          runAsUser: 0
      volumes:
      - name: data
        emptyDir: {}
EOF

# Watch the pod
echo "Watching Elasticsearch pod..."
kubectl -n apim get po -w

# When ready, test it
echo "Testing Elasticsearch..."
kubectl -n apim port-forward svc/elasticsearch-index 9200:9200 &
sleep 5
curl http://localhost:9200/_cluster/health?pretty
