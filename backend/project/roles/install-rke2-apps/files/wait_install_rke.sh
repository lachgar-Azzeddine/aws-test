#!/bin/bash

while true; do
  nodes=$(kubectl get nodes | awk '{if(NR>1) print $1}')
  if [ -z "$nodes" ]; then
    echo "No nodes available. Sleeping for 10 seconds..."
    sleep 10
    continue
  fi
  all_running=true
  for node in $nodes; do
    status=$(kubectl get nodes $node | awk '{if(NR>1) print $2}')
    if [ "$status" != "Ready" ]; then
      echo "Node $node is not available yet!"
      all_running=false
    fi
  done
  if $all_running; then
    echo "All nodes are up and running!"
    exit 0
  fi
  sleep 10
done

