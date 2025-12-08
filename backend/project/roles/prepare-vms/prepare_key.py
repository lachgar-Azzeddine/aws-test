import os

def prepare_ssh_key(single_line_key):
    # Write the SSH key to a normal file
    BEGIN_KEY = "-----BEGIN OPENSSH PRIVATE KEY-----"
    END_KEY = "-----END OPENSSH PRIVATE KEY-----"
    
    # Find the key data by removing the BEGIN and END markers
    key_data = single_line_key[len(BEGIN_KEY):-len(END_KEY)]
    
    # Break the key data into chunks of 64 characters
    formatted_key_data = "\n".join([key_data[i:i+64] for i in range(0, len(key_data), 64)])
    output_path="files/id_rsa.key"
    # Combine the BEGIN and END markers with the formatted key data
    formatted_key = f"{BEGIN_KEY}\n{formatted_key_data}\n{END_KEY}"
    
    return formatted_key
    with open(output_path, 'w') as f:
        f.write(key_string)

    print(f"SSH key saved to {output_path}")

