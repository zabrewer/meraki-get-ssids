Meraki Get SSIDs
-----------------

## Description

meraki - get_ssids.py

Async tool that returns SSID info from every network in a given meraki dashboard organization and writes to CSV.

Example Use:  python get_ssids.py [apikey] [orgname] --ssids 'MY SSID 1' 'MY SSID 2' --speed medium

* If no --filename argument, filename is ORGNAME_ssids.csv.  
* If no --speed argument default is set to slow
* If no --ssids argument, will return ALL ssids for each network (including Meraki Default SSIDs and disabled SSIDs)

HINT: If you hit API rate limit, try a slower speed (slow/medium/fast/ludacris).  

Slow (default when no --speed argument is given) should be fine for most use cases as this tool makes use of the meraki.aio async library.

Common use cases for this tool:
- checking SSID naming consistency
- getting all RADIUS servers for SSIDs across the Organization and Networks
- getting walled garden or other settings per network/SSIDs in the Organization

Install and more use examples below.

## Installation

Python Virtual Environment is the preferred  ered install method but to install to your default python (3.5 or newer):
**1. Clone this repository locally**
```
git clone https://github.com/zabrewer/meraki-get-ssids.git
```
**2. Install from requirements.txt**

```
pip install -r requirements.txt
```

### Installing to a Python Virtual Environment

Note: For Mac OSX, replace "python" with "python3" and for both platforms, make sure the output of python -v (or python3 -v) is 3.5 or greater.

**1. Clone this repository locally**
```
git clone https://github.com/zabrewer/meraki-get-ssids.git
```
**2. Create the virtual environment**
```
python3 -m venv meraki-get-ssids
```

**3. Change to the meraki-get-ssids directory**
```
cd meraki-get-ssids
```

**4. Activate the virtual environment**

For Windows
```
Scripts\activate.bat
```

For Mac
```
source bin/activate
```

**5. Satisfy dependencies by installing external packages**
```
pip install -r requirements.txt
```

**6. Launch meraki-get-ssids while in virtual environment**
```
python get_ssids.py
```

To deactivate the virtual environment:

For Windows
```
Scripts\deactivate.bat
```

For Mac
```
deactivate
```

## Example Use

At a minimum, an API key that has access to the given org should be supplied as well as a Meraki Dashboard Organization name.  

**Note: these arguments are positional (apikey must be followed by orgname)**

```
python get_ssids.py [apikey] [orgname]
```

e.g.
```
python get_ssids.py apikey12345678 myOrgName
```
Running get_ssids.py with the positional arguments above will output all SSID info to a CSV file named 'myOrgName_SSIDs.csv' in the same directory as get_ssids.py

**Note: If your orgName has a space in it, surround it by quotes e.g.
```
python get_ssids.py apikey12345678 "my Org Name"
```

If you want to filter by one or more SSIDs, add them with the --ssids argument followed by the SSID names
e.g.
```
python get_ssids.py apikey12345678 "my Org Name" --ssids "My SSID 1" "My SSID 2"
```
There is no limit to the number of --ssid arguments but like the orgname positional argument, if the SSID name contains spaces it *must* be wrapped in quotes like the example above. 

A good use case for get_ssids.py is to verify that all SSIDs match across networks in one or more orgs. It's not uncommon to find that a space was added between words in the SSID name for networks when the SSID was setup across an org with different network-level admins.

If you wish to change the # of requests per second (speed), add the --speed argument:
e.g.
```
python get_ssids.py apikey12345678 "my Org Name" --ssids "My SSID 1" "My SSID 2" 
```

Note: get_ssids.py makes use of the meraki.aio async library. Some --speed options may exceed the Meraki Dashboard API rate limit of 10 requests per second, even with backoff settings used by this tool.

For more info on the Meraki Dashboard rate limit see [here](https://developer.cisco.com/meraki/api-v1/#!rate-limit).

If you find yourself hitting the rate limit, lower the speed.

**Speed Settings:**

slow - maximum  concurrent requests = 2
medium - maximum  concurrent requests = 4
fast - maximum  concurrent requests = 6
ludacris - maximum  concurrent requests = 8

## Example CSV Output
Note: with small changes to the python file other data can be added to the CSV

| OrgName    | NetworkName    | SSIDName | SSIDEnabled | SplashPage | RadiusServers | AdminSplash | WalledGardenEnabled | WalledGardenRanges |
|:----------------------|-----------|------|------|------|------|------|------|------|
| My Org Name | MyNetworkName | MySSID | Yes | Password-protected with custom RADIUS | whatever-your-radius-srv.elb.us-east-1.amazonaws.com | https://random.execute-api.us-east-1.amazonaws.com/you/url | Yes | WHATEVER.execute-api.us-east-1.amazonaws.com, WHATEVER2.execute-api.us-east-1.amazonaws.com, *.YOURDOMAIN.com |