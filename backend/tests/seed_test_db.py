
import sqlite3
import docker
import argparse

def get_container_ip(container_name):
    """Get the IP address of a running Docker container."""
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        ip_address = container.attrs['NetworkSettings']['Networks']['tests_default']['IPAddress']
        return ip_address
    except docker.errors.NotFound:
        print(f"Error: Container '{container_name}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def seed_database(db_path, gogs_ip):
    """Insert the Gogs container IP into the test database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the VM already exists
        cursor.execute("SELECT id FROM virtual_machines WHERE \"group\" = 'gitops'")
        if cursor.fetchone():
            print("Gogs VM already exists in the database. Updating IP.")
            cursor.execute("UPDATE virtual_machines SET ip = ? WHERE \"group\" = 'gitops'", (gogs_ip,))
        else:
            print("Inserting Gogs VM into the database.")
            # Assuming zone_id=1 exists from the initial db setup.
            # Adjust if necessary.
            cursor.execute(
                "INSERT INTO virtual_machines (hostname, roles, \"group\", ip, nb_cpu, ram, os_disk_size, zone_id, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ('gogs-server', 'gitops', 'gitops', gogs_ip, 2, 4096, 50, 1, 'created')
            )
        
        conn.commit()
        conn.close()
        print(f"Successfully seeded database with Gogs IP: {gogs_ip}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred during database seeding: {e}")

def main():
    parser = argparse.ArgumentParser(description="Seed the test database with dynamic data.")
    parser.add_argument("--db-path", required=True, help="Path to the SQLite database file.")
    parser.add_argument("--gogs-container", default="dev-gogs", help="Name of the Gogs Docker container.")
    args = parser.parse_args()

    gogs_ip = get_container_ip(args.gogs_container)
    if gogs_ip:
        seed_database(args.db_path, gogs_ip)

if __name__ == "__main__":
    main()
