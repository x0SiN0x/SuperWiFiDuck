"""
   This script converts web files into C arrays and generates a header file
   for use in ESP32-based devices, particularly for hosting a web server.

   This software is licensed under the MIT License. See the license file for details.
   Source: https://github.com/spacehuhntech/WiFiDuck
"""

import os
import binascii
import gzip

def get_file_content(path):
    """
    Reads the content of a file, compresses it using gzip, and returns the compressed content.

    Args:
    - path (str): Path to the file.

    Returns:
    - bytes: Compressed content of the file.
    """
    file = open(path, "r")
    content = file.read().encode("utf-8")
    file.close()

    gzip_content = gzip.compress(content)

    print(f"({len(content)} -> {len(gzip_content)} byte)...", end="")

    return gzip_content

def get_varname(filename):
    """
    Generates a variable name based on the filename.

    Args:
    - filename (str): Name of the file.

    Returns:
    - str: Variable name derived from the filename.
    """
    return filename.replace(".", "_").lower()

def get_file_type(filename):
    """
    Determines the content type of a file based on its extension.

    Args:
    - filename (str): Name of the file.

    Returns:
    - str: MIME type corresponding to the file extension.
    """
    file_ending = filename.split('.')[1]
    if file_ending == "js":
        return "application/javascript"
    elif file_ending == "css":
        return "text/css"
    elif file_ending == "html":
        return "text/html"
    elif file_ending == "svg":
        return "image/svg+xml"
    else:
        return "text/plain"

def get_response_code(filename):
    """
    Determines the HTTP response code based on the filename.

    Args:
    - filename (str): Name of the file.

    Returns:
    - int: HTTP response code.
    """
    if filename == "error404.html":
        return 404
    else:
        return 200

def build_hex_string(varname, content):
    """
    Converts file content into a hexadecimal string representation.

    Args:
    - varname (str): Variable name.
    - content (bytes): Content of the file.

    Returns:
    - str: Hexadecimal string representation of the content.
    """
    hexstr = f"const uint8_t {varname}[] PROGMEM = {{ "

    for c in content:
        hexstr += f"{hex(c)},"

    hexstr = hexstr[:-1]
    hexstr += " };\n\n"

    return hexstr

def write_server_callback(filename, output):
    """
    Writes server callback functions for handling HTTP requests.

    Args:
    - filename (str): Name of the file.
    - output (file object): Output file object to write to.
    """
    varname = get_varname(filename)
    filetype = get_file_type(filename)
    response_code = get_response_code(filename)

    output.write(f"\\\nserver.on(\"/{filename}\", HTTP_GET, [](AsyncWebServerRequest* request) {{")
    output.write(f"\\\n\treply(request, {response_code}, \"{filetype}\", {varname}, sizeof({varname}));")
    output.write(f"\\\n}});")

def write_hex_array(filename, output):
    """
    Writes C arrays containing the hexadecimal representation of file content.

    Args:
    - filename (str): Name of the file.
    - output (file object): Output file object to write to.
    """
    print(f"Converting {filename}...", end="")

    path = f"web/{filename}"
    content = get_file_content(path)
    varname = get_varname(filename)

    hex_array = build_hex_string(varname, content)

    output.write(hex_array)

    print("OK")

def write_callbacks(files, output):
    """
    Writes server callback functions for each file.

    Args:
    - files (list of str): List of filenames.
    - output (file object): Output file object to write to.
    """
    for filename in files:
        write_server_callback(filename, output)

def write_arrays(files, output):
    """
    Writes C arrays for each file.

    Args:
    - files (list of str): List of filenames.
    - output (file object): Output file object to write to.
    """
    for filename in files:
        write_hex_array(filename, output)

def main():
    """
    Main function to execute the script.
    """
    #web_files = os.listdir("web/")
    web_files = [f for f in os.listdir("web/") if not f.startswith(".")]


    outputfile = open("src/webfiles.h", "w+")
    outputfile.write("#pragma once\n\n")

    outputfile.write(f"#define WEBSERVER_CALLBACK ")

    write_callbacks(web_files, outputfile)

    outputfile.write("\n\n")

    write_arrays(web_files, outputfile)

    outputfile.close()

if __name__ == "__main__":
    main()
