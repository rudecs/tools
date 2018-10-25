#!/usr/bin/python

name = "change_ros_subnet"
category = "osis"
organization = "digitalenergy.online"
author = "vadim.sorokin@digitalenergy.online"

import getopt
import os
import sys
sys.path.append('/opt/jumpscale7/lib')
import requests

from netaddr import IPAddress
from JumpScale import j
IYO_URL='https://itsyou.online'
env="ds1.digitalenergy.online"

def usage():
    print "        {} -c cloudspaceID -a new_IP_addr -n external_network_id".format(sys.argv[0])
    print "        Also you should set environment variables CLIENT_ID and CLIENT_SECRET from IYO"

def get_jwt(CLIENT_ID, CLIENT_SECRET, IYO_URL):
    # Get JWT from itsyou.online
    r = requests.post(IYO_URL + "/v1/oauth/access_token", data={'grant_type': 'client_credentials', 'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'response_type': 'id_token'})
    if r.status_code != 200:
        print("ERROR: Can't get JWT from" + IYO_URL)
        return 1
    jwt = r.text
    return jwt

def main(argv):

    try:
        CLIENT_ID=os.environ["CLIENT_ID"]
        CLIENT_SECRET=os.environ["CLIENT_SECRET"]
    except KeyError as e:
        print("    You didn't set environment variable {0}!").format(e)
        usage()
        sys.exit(1)

    try:
        opts, args = getopt.getopt(argv,"hc:a:n:",["csid=","addr=","nid="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-a", "--addr"):
            IPaddr = arg
        elif opt in ("-c", "--csid"):
            csID = arg
        elif opt in ("-n", "--nid"):
            extnetID = arg
        else: 
            usage()
            sys.exit(2)

    r = change_ip(csID, IPaddr, extnetID)
    # if OK r == None...
    
    # Restore ROS to factory setting to apply the new settings
    jwt = get_jwt(CLIENT_ID, CLIENT_SECRET, IYO_URL)
    r = restoreROS(csID, jwt, env)
    if (r == 0):
        print("Public IP for cloudspace {0} is changed to {1}").format(csID, IPaddr)
    else: 
        print("ERROR: Can't reset ROS for CS {0} in this time! Status code: {1}, response: {2}").format(csID, r.status_code, r.text)
    if (r != 0):
        sys.exit(1)

def change_ip(csID, IPaddr, extnetID):
    # Get needed namespaces from OSIS
    cb = j.clients.osis.getNamespace('cloudbroker')
    fw = j.clients.osis.getNamespace('vfw')

    print("CSID: {0}, IPADDR: {1}, extnetID: {2}").format(csID, IPaddr, extnetID)

    # Create tmp OSIS objects from persisnent by IDs
    cs = cb.cloudspace.get(int(csID))
    rosID = cs.networkId
    vfw = fw.virtualfirewall.get(rosID)
    extnet = cb.externalnetwork.get(int(extnetID))

    # Get info from OSIS objects
    prefix=IPAddress(extnet.subnetmask).netmask_bits()
    portForwarding = vfw.tcpForwardRules

    # Set info to tmp OSIS objects
    cs.externalnetworkId=extnetID
    cs.externalnetworkip="{0}/{1}".format(IPaddr,prefix)
    vfw.vlan=extnet.vlan
    vfw.pubips=unicode(IPaddr)

    for i in portForwarding:
        i.fromAddr = IPaddr

    # Save tmp OSIS object permanently
    cb.cloudspace.set(cs)
    fw.virtualfirewall.set(vfw)

def restoreROS(csID, jwt, env):

    # Prepare headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Authorization": "bearer " + jwt
    }

    # Push request to API server
    print("Resetting ROS of CloudSpace {}").format(csID)
    r = requests.post("https://" + env + "/restmachine/cloudbroker/cloudspace/resetVFW", data={'cloudspaceId': csID, 'resettype': 'factory'}, headers=headers)
    if (r.status_code != 200):
        print("ERROR: Can't reset ROS in this time! Status code: {0}, response: {1}").format(r.status_code, r.text)
        return 1
    return 0

if __name__ == "__main__":
    if (len(sys.argv) < 3):
        usage()
        sys.exit(2)
    main(sys.argv[1:])



