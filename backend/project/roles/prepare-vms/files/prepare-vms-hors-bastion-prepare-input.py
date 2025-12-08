import yaml

def main():
    try:
        # Load the YAML file
        with open('../../../global-config.yml', 'r') as f:
            #data = yaml.safe_load(f)
            data = yaml.load(f, Loader=yaml.FullLoader)
        rke = data['infra']['virtual_machine_config']['machine-cluster-rancher']
        # Generate the inventory file
        with open('/home/adamo/inventory/hosts', 'a') as f:
            f.write('\n[prepare_vms]\n')
            for item in range(len(rke)):
                for vm in range(rke[item]['replicas']):
                    f.write('vm-' + str(vm) + ' ansible_host=' + rke[item]['network']['vm_machine_ip'][vm] + ' ansible_sudo_pass=' + data['users_management']['machine_user']['password'] +  ' ansible_password=' + data['users_management']['machine_user']['password'] + ' ansible_user=' + data['users_management']['machine_user']['username'] + " ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n")
    except Exception as e:
        print(f"Error: {str(e)}. Please check the input files and try again.")


if __name__ == "__main__":
    main()
