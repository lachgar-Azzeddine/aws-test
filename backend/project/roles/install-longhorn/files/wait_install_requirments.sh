#!/bin/bash

namespace="longhorn-system"

while true; do
  pods=$(kubectl get pods -n $namespace | awk '{if(NR>1) print $1}')
  if [ -z "$pods" ]; then
    echo "No pods found in namespace $namespace. Sleeping for 10 seconds..."
    sleep 10
    continue
  fi
  all_running=true
  for pod in $pods; do
    status=$(kubectl get pod $pod -n $namespace | awk '{if(NR>1) print $3}')
    if [ "$status" != "Running" ]; then
      echo "Pod $pod is not running!"
      all_running=false
    fi
  done
  if $all_running; then
    echo "All pods in namespace $namespace are running!"
    exit 0
  fi
  sleep 10
done