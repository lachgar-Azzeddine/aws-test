import os
import subprocess
from pathlib import Path
import argparse


def sanitize_image_name(image_name):
    """Replace slashes in image names with underscores."""
    return image_name.replace("/", "_")


def tar_images(input_folder_path, output_folder_path, role_name=None, all_roles=False):
    """
    Pulls Docker images and saves them as tar files.

    Can process either a single role or all roles. It checks if an image
    has already been downloaded before pulling it.
    """
    # Ensure the output folder exists
    Path(output_folder_path).mkdir(parents=True, exist_ok=True)

    roles_to_process = []
    if all_roles:
        roles_to_process = [
            d
            for d in os.listdir(input_folder_path)
            if os.path.isdir(os.path.join(input_folder_path, d))
        ]
    elif role_name:
        # Check if the specified role directory exists
        role_path = os.path.join(input_folder_path, role_name)
        if os.path.isdir(role_path):
            roles_to_process = [role_name]
        else:
            print(f"Error: Role directory not found at '{role_path}'")
            return

    # Iterate over each role to be processed
    for role in roles_to_process:
        role_path = os.path.join(input_folder_path, role)
        images_file_path = os.path.join(role_path, "images.txt")

        if os.path.exists(images_file_path):
            with open(images_file_path, "r") as file:
                for image in file.readlines():
                    image = image.strip()
                    if not image:
                        continue

                    # Sanitize the image name and create the tar file path
                    sanitized_image_name = sanitize_image_name(image)
                    tar_file_name = f"{role}_{sanitized_image_name}.tar"
                    tar_file_path = os.path.join(output_folder_path, tar_file_name)

                    # Skip if tar file already exists
                    if os.path.exists(tar_file_path):
                        print(
                            f"Image '{image}' already exists as '{tar_file_path}'. Skipping."
                        )
                        continue

                    try:
                        # Pull the Docker image
                        print(f"Pulling image: {image}")
                        subprocess.run(
                            ["docker", "pull", image],
                            check=True,
                            capture_output=True,
                            text=True,
                        )

                        # Create a tar archive of the pulled image
                        print(f"Saving image '{image}' to '{tar_file_path}'")
                        subprocess.run(
                            ["docker", "save", "-o", tar_file_path, image],
                            check=True,
                            capture_output=True,
                            text=True,
                        )

                        # Remove the Docker image to save space
                        print(f"Removing image '{image}' from local storage")
                        subprocess.run(
                            ["docker", "rmi", image],
                            check=False,  # Don't fail if removal fails
                            capture_output=True,
                            text=True,
                        )
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to pull or save {image}: {e.stderr}")
        else:
            print(f"No 'images-f.txt' file found in '{role}'. Skipping.")


if __name__ == "__main__":
    # Get the absolute path to the project/roles directory
    script_dir = Path(__file__).parent.resolve()
    INPUT_FOLDER_PATH = script_dir / "project" / "roles"

    parser = argparse.ArgumentParser(
        description="Tar Docker images from project roles and save them in an output folder."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--role",
        help="The name of a specific role to download images for (e.g., 'install-gogs').",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Download images for all roles found in the project/roles directory.",
    )
    parser.add_argument(
        "OUTPUT_FOLDER_PATH",
        help="Path to the output folder where tarred images will be saved.",
    )

    args = parser.parse_args()

    tar_images(
        str(INPUT_FOLDER_PATH),
        args.OUTPUT_FOLDER_PATH,
        role_name=args.role,
        all_roles=args.all,
    )
