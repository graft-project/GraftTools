#!/usr/bin/python3


import sys
import requests
import json
import string
import logging
import os


SUPERNODE_HOST = "localhost"
WALLER_RPC_HOST = "localhost"


SUPERNODE_PORT = 28690
WALLER_RPC_PORT = 28682
DST_ADDRESS = ""
COIN = 10000000000
AMOUNT = 100


def get_auth_sample(hostname, port, payment_id, timeout_s):
	url = "http://" + hostname + ":" + str(port) + "/debug/auth_sample/" + payment_id
	resp = requests.get(url, timeout = timeout_s)
	result = json.loads(resp.text)
	return result

def pay_rta_mining(hostname, port, dst_address, amount, auth_sample, payment_id, auth_sample_fee_ratio = 0.005):
	url = "http://" + hostname + ":" + str(port) + "/json_rpc"
	headers = {'Content-Type' : 'application/json'}
	payload = {"jsonrpc":"2.0","id":"0","method":"transfer_rta"}
	request = {}
	destinations = []
	total_fee_atomic_units = int(COIN * AMOUNT * auth_sample_fee_ratio)
	amount_atomit_units = COIN * AMOUNT - total_fee_atomic_units

	destinations.append({"address" : dst_address, "amount" : amount_atomit_units})
	supernode_keys = []
	for item in auth_sample["items"]:
		destination = {"address": item["Address"], "amount" : int(COIN * AMOUNT * auth_sample_fee_ratio / len(auth_sample["items"]))}
		destinations.append(destination)
		supernode_keys.append(item["PublicId"])

	request["destinations"] = destinations
	request["supernode_keys"] = supernode_keys
	request["graft_payment_id"] = payment_id
	request["auth_sample_height"] = auth_sample["height"]
	request["priority"] = 0
	request["mixin"] = 7
	payload["supernode_signatures"] = []
	payload["params"] = request
	print (json.dumps(payload, indent = True))
	resp = requests.post(url, data = json.dumps(payload), headers = headers, timeout = 5)
	print (resp.text)

def get_stake_tx_params(hostname, port, timeout_s):
	url = "http://" + hostname + ":" + str(port) + "/dapi/v2.0/cryptonode/getwalletaddress"
	resp = requests.get(url, timeout = timeout_s)
	result = json.loads(resp.text)
	return result

def main():
	logging.info('=== starting checking ===')
	payment_id = '01234567890abcdefgh'
	auth_sample = get_auth_sample(SUPERNODE_HOST, SUPERNODE_PORT, payment_id, 5)

	if not 'result' in auth_sample:
		logging.error('Failed to build auth sample');
		return -1

	pay_rta_mining(WALLER_RPC_HOST, WALLER_RPC_PORT, DST_ADDRESS, AMOUNT, auth_sample["result"], payment_id)




if __name__ == '__main__':
	main()
