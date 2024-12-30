#!/usr/bin/python3

from termcolor import colored # colored use for print text in color.
# Domain to Ip Converter.

print(colored("\n******************** Domain to IP Converter  ********************", "cyan"))
print(colored("******************** Created By Sagar Biswas ********************", "red"))

import socket # socket use for make connection between two devices (server and client).
import pyfiglet # pyfiglet use for print text in ASCII Art.

banner = colored(pyfiglet.figlet_format("IP converter"), "green")
print(banner)

Domain = input("..:: Please enter domain name: ")  
IP = socket.gethostbyname(Domain)  # gethostbyname() method is used to get the IP address of the domain name.

print(f"\n--> IP address of {Domain} is: {IP}")  # print the IP address of the domain name.

# Easiest way to find the IP address of a domain name is to use the command line tool ping google.com