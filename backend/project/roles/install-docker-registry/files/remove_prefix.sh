#!/bin/bash

PREFIX="harbor.example.com/"

# Get all image:tag combinations
docker images --format "{{.Repository}}:{{.Tag}}" | while read -r image; do
    # Check if image starts with the prefix
    if [[ "$image" == $PREFIX* ]]; then
        # Remove the prefix
        new_image="${image#$PREFIX}"
        echo "Tagging $image as $new_image"
        docker tag "$image" "$new_image"
    fi
done
