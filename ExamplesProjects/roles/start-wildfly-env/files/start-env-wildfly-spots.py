import sys
import requests
import json
import time

# For terminate automation (ChenA)
time_now = time.strftime("%d-%m-%Y")

spotinst_account = sys.argv[1]
spotinst_token = sys.argv[2]
env_name = sys.argv[3]
start_agents = sys.argv[4]
start_onlines = sys.argv[5]

#print (spotinst_account, spotinst_token, env_name, start_agents, start_onlines)

def startSpotInstances(spotInstSIG, spotInstSSID, spotinst_group_name):
	headers={'Authorization': 'Bearer ' + str(spotinst_token)}
	try:
		print('Starting Spot instance ' + str(spotinst_group_name))
		r = requests.get('https://api.spotinst.io/aws/ec2/group/'+spotInstSIG+'/statefulInstance/?accountId='+str(spotinst_account),headers=headers,)
		if r.json()['response']['items'][0]['state'] != 'PAUSED':
			return
		addTagsArraytoSpotGroupByGid(spotInstSIG,spotinst_group_name)
		time.sleep(10)
		requests.put('https://api.spotinst.io/aws/ec2/group/'+spotInstSIG+'/statefulInstance/'+spotInstSSID+'/resume?accountId='+str(spotinst_account),headers=headers,)
		r = requests.get('https://api.spotinst.io/aws/ec2/group/'+spotInstSIG+'/statefulInstance/?accountId='+str(spotinst_account),headers=headers,)
		timeout = 600
		while (r.json()['response']['items'][0]['state'] != 'ACTIVE'):
			if (timeout <= 0):
				print ('Error starting Spot instance ' + str(spotinst_group_name), 'timeout exceeded')
				return
			r = requests.get('https://api.spotinst.io/aws/ec2/group/'+spotInstSIG+'/statefulInstance/?accountId='+str(spotinst_account),headers=headers,)
			time.sleep(5)
			timeout-=5
		print('Spot instance ' + str(spotinst_group_name) + ' started')
	except Exception as e:
		print('Starting Spot instance ' + str(spotinst_group_name))

def getSpotinstGroups():
	headers={'Authorization': 'Bearer ' + str(spotinst_token)}
	try:
		response = requests.get('https://api.spotinst.io/aws/ec2/group/?accountId='+str(spotinst_account),headers=headers,)
		spotInstGroups = response.json()['response']['items']
		return(spotInstGroups)
	except Exception as e:
		print('Error listing Spotinst elastigroups')

def getSpotinstSigByName(spotinst_group_name,spotinst_group_list):
	try:
		for group in spotinst_group_list:
			if group['name'] == spotinst_group_name:
				return (group['id'])
	except Exception as e:
		print("Error finding Spotinst group "+ spotinst_group_name)

def getSpotinstSsidBySig(spotinst_group_id, spotinst_group_name):
	headers={'Authorization': 'Bearer ' + str(spotinst_token)}
	try:
		response = requests.get('https://api.spotinst.io/aws/ec2/group/'+str(spotinst_group_id)+'/statefulInstance?accountId='+str(spotinst_account),headers=headers,)
		if len(response.json()['response']['items']) != 1:
			print("Error more than one stateful instance on "+ spotinst_group_name)
		return(response.json()['response']['items'][0]['id'])
	except Exception as e:
		print("Error getting stateful instance from group "+ spotinst_group_name)

def addTagsArraytoSpotGroupByGid(spotinst_group_id, spotinst_group_name):
	headers={"Content-Type": "application/json",'Authorization': 'Bearer ' + str(spotinst_token)}
	try:
		response = requests.get('https://api.spotinst.io/aws/ec2/group/'+str(spotinst_group_id)+'/?accountId='+str(spotinst_account),headers=headers,)
		current_tags_array = response.json()['response']['items'][0]['compute']['launchSpecification']['tags']
		find = 'False'
		array = []
		for tag in current_tags_array:
			if tag['tagKey'] == 'LastChange':
				find = 'True'
				tag['tagValue'] = time_now
			array.append(tag)
		if find == 'False':
			array = [{'tagKey': 'LastChange', 'tagValue': time_now}]
			current_tags_array.extend(array)
		else:
			current_tags_array = array
		data = {"group":{"compute":{"launchSpecification":{"tags": current_tags_array}}}}
		data_json = json.dumps(data)
		requests.put('https://api.spotinst.io/aws/ec2/group/'+spotinst_group_id+'?accountId='+str(spotinst_account),data = data_json,headers=headers,)
	except Exception as e:
		print("Error adding LastChange tag to Spotinst elastigroup "+ spotinst_group_name)

spotinst_groups = getSpotinstGroups()
for group in spotinst_groups:
    for tag in group['compute']['launchSpecification']['tags']:
        if tag['tagKey'] == "Name" and env_name in tag['tagValue']:
            print (tag)
            if str(env_name+"_Analytical") in tag['tagValue']:
                spotinst_ssid = getSpotinstSsidBySig(group['id'],group['name'])
                print (spotinst_ssid)
                startSpotInstances(group['id'], spotinst_ssid, group['name'])
            if str(env_name+"_Agent") in tag['tagValue'] and start_agents == 'true':
                spotinst_ssid = getSpotinstSsidBySig(group['id'],group['name'])
                print (spotinst_ssid)
                startSpotInstances(group['id'], spotinst_ssid, group['name'])
            if str(env_name+"_AgentPP") in tag['tagValue'] and start_agents == 'true':
                spotinst_ssid = getSpotinstSsidBySig(group['id'],group['name'])
                print (spotinst_ssid)
                startSpotInstances(group['id'], spotinst_ssid, group['name'])
            if str(env_name+"_Online") in tag['tagValue'] and start_onlines == 'true':
                spotinst_ssid = getSpotinstSsidBySig(group['id'],group['name'])
                print (spotinst_ssid)
                startSpotInstances(group['id'], spotinst_ssid, group['name'])
time.sleep(120)