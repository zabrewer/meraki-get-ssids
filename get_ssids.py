import meraki.aio
import meraki
import asyncio
import project_logger
import logging
import argparse
import csv

__author__ = 'Zach Brewer'
__email__ = 'zbrewer@cisco.com'
__version__ = '0.1.0'
__license__ = 'MIT'

parser = argparse.ArgumentParser(description='Get SSID Info for all networks in a given org')
parser.add_argument('api_key', metavar='API Key', type=str, nargs=1,
                    help='API Key with access to Meraki Dashboard Organization')
parser.add_argument('org_name', metavar='Org Name', type=str, nargs=1,
                    help='Name of the Org to target.')
parser.add_argument('--ssids', metavar='SSID Names', type=str, nargs='+',
                    help='List of SSIDs to filter by seperated by a space.')
parser.add_argument('--filename', metavar='CSV Export File Name', type=str, nargs=1,
                    help='List of SSIDs to filter by seperated by a space.')
parser.add_argument('--speed', metavar='script speed (slow | medium | fast | ludacris)', type=str, nargs=1,
                    help='List of SSIDs to filter by seperated by a space.')

args = parser.parse_args()
log = logging.getLogger('get_ssids.py')

'''
meraki - get_ssids.py

small async tool that returns SSID info from every network in a given org and writes to CSV.
Example Use:  python get_ssids_.py [apikey] [orgname] --ssids 'MY SSID 1' 'MY SSID 2' --speed medium

If no --filename argument, filename is ORGNAME_ssids.csv.  
If no --speed argument default is set to slow
If no --ssids argument, will return ALL ssids for each network (including Meraki Default and disabled SSIDs)

HINT: If you hit API rate limit, try a slower speed (slow/medium/fast/ludacris)
'''

async def get_ssids(aiomeraki, network, org_name):
    '''
    Async function that returns SSIDs for a given NetworkID
    Returns a Python list containing nested dicts with getNetworkSSID data
    '''
    try:
        networks_json = await aiomeraki.wireless.getNetworkWirelessSsids(
            networkId=network['id']
        )
    except meraki.exceptions.AsyncAPIError as e:
        print(f'Meraki API ERROR: {e}\n')
        print(f'Error recieved on network: { network["name"] }\n\n')
    except Exception as e:
        print(f'some other ERROR: {e}')
    if networks_json:

        return {
            'networkName': network['name'],
            'networkId': network['id'],
            'organizationId': network['organizationId'],
            'organizationName': org_name[0],
            'ssid_data': [ssid for ssid in networks_json],
        }

    else:
        return None

async def async_apicall(api_key,org_name, speed, debug_values):
    if speed == 'slow':
        concurrent_requests=2
    elif speed == 'medium':
        concurrent_requests=4
    elif speed == 'fast':
        concurrent_requests=8
    elif speed == 'ludacris':
        concurrent_requests=10
    else:
        log.error('Valid speed arguments are slow, medium, fast, or ludacris\n')
        exit(0)

    # Instantiate a Meraki dashboard API session
    # NOTE: you have to use "async with" so that the session will be closed correctly at the end of the usage
    async with meraki.aio.AsyncDashboardAPI(
            api_key,
            base_url='https://api.meraki.com/api/v1',
            log_file_prefix=__file__[:-3],
            maximum_concurrent_requests=concurrent_requests,
            wait_on_rate_limit=True,
            output_log=debug_values['output_log'],
            print_console=debug_values['output_console'],
        ) as aiomeraki:

        log.info(f'Getting all networks and SSID information for org "{org_name[0]}"...\n')

        orgs = await aiomeraki.organizations.getOrganizations()
        org_id = [org for org in orgs if org['name'] == org_name[0]][0]['id'] # messy but in a hurry...

        all_networks = await aiomeraki.organizations.getOrganizationNetworks(organizationId=org_id)
        network_tasks = [get_ssids(aiomeraki, network, org_name=org_name) for network in all_networks if 'wireless' in network['productTypes']]
        all_ssids = []
        for task in asyncio.as_completed(network_tasks):
            network_id_json = await task
            log.info(f'Returned SSIDs for network {network_id_json["networkName"]}')
            all_ssids.append(network_id_json)

        return all_ssids

def return_ssids(api_key, org_name, speed, debug_app=False):
    if debug_app:
        debug_values = {'output_log' : True, 'output_console' : True}
    else:
        debug_values = {'output_log' : False, 'output_console' : False}

    #begin async loop
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(async_apicall(api_key, org_name, speed, debug_values))

# set defaults for arguments if not set...
api_key = args.api_key[0]
if not args.speed:
    args.speed = ['slow']
if not args.filename:
    args.filename = [args.org_name[0]+'_ssids.csv']
if not args.ssids:
    log.warning('No SSIDs specified (--ssids argument). This will get all SSIDs for network in the org including default and disabled SSIDs.\n')


# start our async call...
networks_and_ssids = return_ssids(api_key=api_key, org_name=args.org_name, speed=args.speed[0])
print('\n')
log.info('API Calls Complete!')
print('\n')

if args.ssids:
    log.info(f'Writing SSID info for network SSIDs "{", ".join(str(x) for x in args.ssids)}" in "{args.org_name[0]}" to file {args.filename[0]}...\n')
else:
    log.info(f'Writing SSID info for all existing SSIDs in "{args.org_name[0]}" to file {args.filename[0]}...\n')

writer = csv.writer(open(args.filename[0],'w'))
writer.writerow(['OrgName','NetworkName','SSIDName','SSIDEnabled','SplashPage','RadiusServers','AdminSplash','WalledGardenEnabled','WalledGardenRanges'])

for network in networks_and_ssids:
    log.info(f'Writing SSID info for network {network["networkName"]}')

    org_name = network['organizationName']
    network_name = network['networkName']
    if args.ssids:
        filtered_ssids = [ssid for ssid in network['ssid_data'] if ssid['name'] in args.ssids]
    else:
        filtered_ssids = network['ssid_data']

    for ssid in filtered_ssids:
        ssid_name = ssid['name']
        if ssid['enabled'] == True:
            ssid_enabled = 'Yes'
        if ssid['enabled'] == False:
            ssid_enabled = 'No'
        auth_mode = ssid['authMode']
        splash_page = ssid['splashPage']
        radius_data = ssid.get('radiusServers')
        if radius_data:
            radius_server = radius_data[0]['host']
        else:
            radius_server = 'None'
        admin_splash = ssid.get('adminSplashUrl')
        walled_garden_enabled = ssid.get('walledGardenEnabled')
        if walled_garden_enabled:
            walled_garden_enabled = 'Yes'
            walled_garden_ranges = ssid['walledGardenRanges']
        else:
            walled_garden_enabled = 'No'
            walled_garden_ranges = ['None']

        # Write data to CSV file
        writer.writerow([org_name, network_name, ssid_name, ssid_enabled, splash_page, radius_server, admin_splash, walled_garden_enabled, ", ".join(str(x) for x in walled_garden_ranges)])

log.info(f'FINISHED! See file {args.filename[0]} for results.')
