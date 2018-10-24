#!/usr/bin/python

import getopt
import sys

from netaddr import IPAddress
from JumpScale import j

def usage():
    print sys.argv[0] + " -c cloudspaceID -a new_IP_addr"

def main(argv):

    try:
        opts, args = getopt.getopt(argv,"hc:a:n:",["csid=","addr=","nid="])
    except getopt.GetoptError:
        print sys.argv[0] + " -c loudspaceID -a new_IP_addr -n external_network_id"
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

    change_IP(csID, IPaddr, extnetID)

def change_ip(csID, IPaddr, extnetID):
    # Get needed namespaces from OSIS
    cb = j.clients.osis.getNamespace('cloudbroker')
    fw = j.clients.osis.getNamespace('vfw')

    # Create tmp OSIS objects from persisnent by IDs
    cs = cb.cloudspace.get(csID)
    vfw = fw.virtualfirewall.get(rosID)
    extnet = cb.cloudspace.get(extnetID)

    # Get info from OSIS objects
    rosID = cs.networkID
    prefix=IPAddress(extnet.subnetmask).netmask_bits()
    portForwarding = vfw.tcpForwardRules

    # Set info to tmp OSIS objects
    cs.externalnetworkId=extnetID
    cs.externalnetworkip="{0}/{1}".format(IPaddr,prefix)
    vfw.vlan=extnet.vlan
    vfw.pubips=[u'{}'].format(IPaddr)

    for i in portForwarding:
        i.fromAddr = IPaddr

    # Save tmp OSIS object permanently
    cb.cloudspace.set(cs)
    fw.virtualfirewall.set(vfw)

    # Restore ROS to factory setting to apply the new settings
    restoreROS(csID)

def restoreROS(csID):

    # Get JWT from itsyou.online
    r = requests.post(IYO_URL + "/v1/oauth/access_token", data={'grant_type': 'client_credentials', 'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'response_type': 'id_token'})
    if r.status_code != 200:
        print("ERROR: Can't get JWT from" + IYO_URL)
        return 1
        jwt = r.text

    # Prepare headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Authorization": "bearer " + jwt
    }

    # Push request to API server
    r = requests.post("https://" + env + ".digitalenergy.online/restmachine/cloudbroker/cloudspace/resetVFW", data={'cloudspaceIDId': csID, 'resettype': 'factory'}, headers=headers)
    print("Resetting ROS of CloudSpace {}").format(csID)
    if ((r.status_code != 200) or (r.text != "true")):
        print("ERROR: Can't reset ROS in this time! Status code: {0}, response: {1}").format(r.status_code, r.text)
        return 1
    return 0

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        usage()
        sys.exit(2)
    main(sys.argv[1:])



