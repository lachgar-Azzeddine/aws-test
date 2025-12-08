#!/bin/bash

# Folder where the tar files are located, passed as an argument
IMAGE_FOLDER="$1"

# Check if the provided folder exists
if [ ! -d "$IMAGE_FOLDER" ]; then
  echo "Error: Folder '$IMAGE_FOLDER' does not exist."
  exit 1
fi

# Loop through all the tar files in the provided folder
for tarfile in "$IMAGE_FOLDER"/*.tar; do
  # Extract the base name of the file (without path and extension)
  filename=$(basename "$tarfile" .tar)

  # Remove the prefix (subdir_) from the filename
  sanitized_name="${filename#*_}"  # Removes everything up to the first underscore

  # Restore the original image name by replacing '_' back to '/'
  image_name_with_tag=$(echo "$sanitized_name" | tr '_' '/')

  # Output the image name with tag
  echo "$image_name_with_tag"
done
