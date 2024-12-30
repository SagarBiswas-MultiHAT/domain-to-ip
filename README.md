# Domain to IP Converter

This Python script allows you to convert a domain name into its corresponding IP address easily. The script leverages the `socket` module to retrieve the IP address of any given domain. With a simple user interface and colorful text, this tool provides a friendly experience for users.

## Features

- Converts a domain name to an IP address.
- Simple and easy-to-use interface.
- Displays the result with color and ASCII art for a fun, engaging experience.
- Written in Python 3.

## Requirements

- Python 3.x
- `termcolor` library
- `pyfiglet` library

You can install the required libraries using the following command:

```bash
pip install termcolor pyfiglet
```

## How to Use

1. Clone or download the script.
2. Run the script in your terminal:
   ```bash
   python3 domain_to_ip_converter.py
   ```
3. Enter a domain name when prompted.
4. The script will display the corresponding IP address of the entered domain.

## Example

```bash
..:: Please enter domain name: google.com
--> IP address of google.com is: 142.250.185.78
```

## License

This project is licensed under the MIT License.
