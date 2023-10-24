# FTPDrop - Automated FTP Server Vulnerability Checker

FTPDrop is a Python script designed to automate the process of checking FTP servers for vulnerability. This tool leverages Shodan, a popular search engine for Internet-connected devices, to discover FTP servers with specific characteristics. It then attempts to upload a file to each discovered server to check for potential vulnerabilities in the server's file upload functionality.

## Features

- **Shodan Integration**: FTPDrop uses Shodan to search for FTP servers matching a specific query, allowing you to target specific server types or configurations.

- **Automated Server Checks**: The script connects to each discovered FTP server, checks for upload permissions, and attempts to upload a file, providing you with insights into potential vulnerabilities.

- **Concurrency**: FTPDrop utilizes multithreading to efficiently check multiple servers in parallel, saving time when scanning a large number of servers.

## Requirements

Before using FTPDrop, you need to install the Shodan CLI tool installed and configured on your system.

## Usage

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/9xN/ftpdrop.git
   ```

2. Navigate to the project directory:

   ```bash
   cd ftpdrop
   ```

3. Open the `ftpdrop.py` script and customize the following variables according to your needs:

   - `DORK`: Modify the Shodan dork to target specific FTP server characteristics.
   - `OUTPUT_FILE`: Specify the output file where Shodan results will be saved.
   - `DROPPED_FILE`: Set the path to the file you want to upload to the FTP servers for testing.
   - `SUCCESS_FILE`: Define the path to the file where successful server IP addresses will be stored.

4. Run the script:

   ```bash
   python3 ftpdrop.py
   ```

   The script will execute the Shodan search, connect to the FTP servers, and attempt to upload the specified file. Successful servers will be recorded in the `success.txt` file.

## Disclaimer

FTPDrop is a tool created for educational and research purposes. Ensure you have proper authorization before scanning or testing FTP servers that do not belong to you. Unauthorized testing of servers is illegal and unethical.

**Use this tool responsibly and at your own risk.**

## TODO:
- Add CLI interface to allow improved operability
- Improve/Segment shodan scanning to allow for faster scan && check time
- Implement a colour scheme/format/acsii art
