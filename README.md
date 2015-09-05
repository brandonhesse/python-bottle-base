# Basic Usage

## Install

* Tested with Python 3.4, if using 2.7.x you may run into issues with unicode
* Run the following setup with pip

```sh
$ pip install bottle bottle-sqlite jinja2 standardjson
$ python app.py # starts server listening on all interfaces on port 8000
```

This uses Python Bottle Web Microframework and SQLite for persistant storage
It will output JSON data with proper formatting for dates and timestamps using StandardJSON
In order to parse the SQLite with json.dumps, you must convert the data to a standard Python dictionary in order to not get a Error.

Included is jinja2 as the template system to give you more control and help assist with properly formatting the HTML and JavaScript without trying to link it all in the Python source files. There are three templates (base, index, and create) which should assist you in creating your own for any subpages you'd like to make.

Hopefully this will help you in generating your own.

# LICENSE
This example is provided with the MIT License