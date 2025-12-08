# file: install.py
"""_summary_
Harmonisation Main installation script
"""

import argparse
import importlib.util
import os
import asyncio
import ansible_runner
from concurrent.futures import ThreadPoolExecutor
from repository import (
    add_ansible_role,
    add_task_logs,
    delete_all_ansible_roles,
    get_monitoring_config,
    get_ansible_role_status,
    # get_products_to_install removed - no longer using product-based system
    get_session,
    update_ansible_role,
)


BACKEND_ROOT = os.path.dirname(os.path.abspath(__file__))

# Determine the root for Ansible project data, which differs between local dev and Docker
# In local dev, the structure is backend/project, backend/inventory, etc.
# In Docker, the structure is backend/data/project, backend/data/inventory, etc.
if os.path.isdir(os.path.join(BACKEND_ROOT, "project")):
    ANSIBLE_ROOT = BACKEND_ROOT
else:
    ANSIBLE_ROOT = os.path.join(BACKEND_ROOT, "data")

print(f"[INFO] Using Ansible root path: {ANSIBLE_ROOT}")


PREPARE_SUFFIX = "-prepare-input"
executor = ThreadPoolExecutor(120)


# ====================================================================
# MINIMAL TEST SETUP - 3 VMs ONLY
# ====================================================================
# VM1 (Infrastructure): Docker Registry + Gogs
# VM2 (RKE2 Master): RKE2 Server (control plane + worker)
# VM3 (RKE2 Worker): RKE2 Agent (worker)
# On RKE2: ArgoCD, Longhorn
# ====================================================================

# MINIMAL ROLE LIST FOR TESTING (6 roles total)
noinf_roles = [
    # Step 1: Prepare all VMs (SSH keys, packages, Docker)
    "prepare-vms",

    # Step 2: Infrastructure VM (Docker Registry + Gogs)
    "install-docker-registry",
    "install-gogs",

    # Step 3: RKE2 Cluster (1 master + 1 worker)
    "install-rke2-apps",

    # Step 4: Kubernetes components (deployed on RKE2)
    "install-longhorn",
    "install-argocd",
]

# Keep original lists commented for reference
# wkube_roles = [
#     "install-argocd",
#     "install-cert-manager",
#     "install-longhorn",
#     "setup-vault-injector",
#     "install-minio-backup",
#     "install-minio",
#     "install-keycloak",
#     "install-kafka",
#     "install-n8n",
#     "install-gravitee-lan",
#     "install-gravitee-dmz",
# ]

# nokube_roles = [
#     "prepare-vms",
#     "install-docker-registry",
#     "install-vault",
#     "install-load-balancer",
#     "install-rke2-apps",
#     "install-rke2-middleware",
#     "install-rke2-dmz",
#     "install-gogs",
#     "install-rancher-server",
# ] + wkube_roles

# ORIGINAL: noinf_roles = [
#     "provisionnement-vms-infra",
#     "provisionnement-vms-apps",
#     "provisionnement-vms-dmz",
# ] + nokube_roles


def load_and_call_get_inputs(role_name, Session):
    absolute_path = os.path.join(
        ANSIBLE_ROOT, "project", "roles", role_name, "prepare_inputs.py"
    )
    if not os.path.exists(absolute_path):
        raise ValueError(
            f"Prepare file for role '{role_name}' does not exist at {absolute_path}"
        )

    spec = importlib.util.spec_from_file_location(
        role_name + "_prepare_inputs", absolute_path
    )
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load module spec for role '{role_name}'")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "get_inputs"):
        raise AttributeError(
            f"Function 'get_inputs' not found in '{absolute_path}' for role '{role_name}'."
        )

    result = module.get_inputs(Session)
    if result is None:
        raise ValueError(
            f"Function 'get_inputs' in '{absolute_path}' for role '{role_name}' returned None."
        )

    return result


def call_post_install(role_name, Session):
    absolute_path = os.path.join(
        ANSIBLE_ROOT, "project", "roles", role_name, "post_install.py"
    )
    if not os.path.exists(absolute_path):
        print(f"Post Install file for role '{role_name}' does not exist, skipping.")
        return

    spec = importlib.util.spec_from_file_location(
        role_name + "_post_install", absolute_path
    )
    if spec is None or spec.loader is None:
        raise ValueError(
            f"Could not load module spec for post_install of role '{role_name}'"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, "post_install"):
        module.post_install(Session)
    else:
        raise AttributeError(
            f"Function 'post_install' not found in '{absolute_path}' for role '{role_name}'."
        )


async def async_call_role(role_name, Session):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, call_role, role_name, Session)


def call_role(role_name, Session):
    """_summary_
    _description_
    Call the ansible role with the given name
    Args:
        role_name (string): role name
        status_handler (function): status handler
        event_handler (function): event handler
    """
    print("call_role: " + role_name)
    extra_vars, inventory = load_and_call_get_inputs(role_name, Session)
    private_data_dir = ANSIBLE_ROOT

    status_handler = create_status_handler(role_name, Session)
    event_handler = create_event_handler(role_name, Session)
    ansible_runner.run(
        private_data_dir=private_data_dir,
        role=role_name,
        status_handler=status_handler,
        event_handler=event_handler,
        extravars=extra_vars,
        inventory=inventory,
        # cmdline="-vvv",
    )
    call_post_install(role_name, Session)


def check_monitoring_role_existence(Session):
    monitoring = get_monitoring_config(Session)
    if monitoring is not None:
        return monitoring.deploy_embeded_monitoring_stack
    return False


# set_products_to_install function removed - no longer using product-based system


async def install_all_roles(Session):
    """_summary_
    _description_
    Install all roles
    Args:
        status_handler (function): status handler
        event_handler (function): event handler
    """
    order = 1
    # noinf_roles = ["testrole"]  # , "testrolefailed", "testrole"]

    # Product-based role selection removed

    if check_monitoring_role_existence(Session):
        if "install-monitoring" not in noinf_roles:
            noinf_roles.append("install-monitoring")
        if "install-neuvector" not in noinf_roles:
            noinf_roles.append("install-neuvector")

    for role in noinf_roles:
        add_ansible_role(role, order, Session)
        order += 1
    for role in noinf_roles:
        await async_call_role(role, Session)
        status = get_ansible_role_status(role, Session)
        if status != "successful":
            break
        # call_role(role, Session)


def create_status_handler(role_name, Session):
    def my_status_handler(data, runner_config):
        # print(
        #     "role_name: "
        #     + role_name
        #     + " runner_ident: "
        #     + data["runner_ident"]
        #     + " status: "
        #     + data["status"]
        #     + "\n"
        # )
        # print("\n")
        update_ansible_role(role_name, data["runner_ident"], data["status"], Session)

    return my_status_handler


def create_event_handler(role_name, Session):
    def my_event_handler(data):
        # Check if event_data exists and is a dictionary before accessing its keys
        if "event_data" in data and isinstance(data["event_data"], dict):
            # Check if event exists and print it
            if (
                "event" in data
                and "stdout" in data
                and data["event"] != "verbose"
                and data["event"] != "playbook_on_start"
                and data["event"] != "runner_on_start"
                and "task" in data["event_data"]
            ):
                print("event: " + data["event"] + "\n")
                print("runner_ident: " + data["runner_ident"] + "\n")
                # if "role" in data["event_data"]:
                #     print("role: " + data["event_data"]["role"] + "\n")
                print("task: " + data["event_data"]["task"] + "\n")
                print("stdout: " + data["stdout"] + "\n")
                add_task_logs(
                    data["event"],
                    data["event_data"]["task"],
                    data["stdout"],
                    data["runner_ident"],
                    Session,
                )
        # Check for play recap event
        if data.get("event") == "playbook_on_stats":
            # print("Role Name: " + role_name + "\n")
            # print("PLAY RECAP:\n")
            # print("runner_ident: " + data["runner_ident"] + "\n")
            # print("event: " + data["event"] + "\n")
            # print(data["stdout"] + "\n")
            add_task_logs(
                data["event"],
                "PLAY RECAP",
                data["stdout"],
                data["runner_ident"],
                Session,
            )

    return my_event_handler


async def main():
    parser = argparse.ArgumentParser(description="Install APPS")
    parser.add_argument(
        "--role",
        type=str,
        required=True,
        nargs="?",
        help="Role to install",
    )
    args = parser.parse_args()
    role = args.role
    DATABASE_URL = os.getenv("DATABASE_URL", "/home/devops/db/harmonisation_runner.db")
    _, Session = get_session(DATABASE_URL)

    delete_all_ansible_roles(Session)
    if role == "all":
        await install_all_roles(Session)
    else:
        add_ansible_role(role, 1, Session)
        call_role(role, Session)


if __name__ == "__main__":
    asyncio.run(main())
