import boto3
import traceback
import time
import datetime
from datetime import datetime, timedelta
import json
from pkg_resources import resource_filename

def lambda_handler(event, context):

    client_ec2 = boto3.client('ec2')
    
    client_sns = boto3.client('sns')
    
    client_ses = boto3.client('ses')
    
    alert = 'arn:aws:sns:sa-east-1:xxxxxx:xxxxxxxx'
    
    account = 'xxxxxxx'
    
    name = ''
    
    region = 'eu-west-1'
    
    environment = ''
    
    Type = ''
    
    spot_str = ''
    
    owner = ''
    
    instance_id = ''
    
    def sendalert(subject, var):
	    try:
	        contents = traceback.format_exc()
	        client_sns.publish(
	        TopicArn=alert,
	        Message=str(var) + '\n' + '\n' + str(contents),
	        Subject=str(subject) + ' on account ' + str(account)
	        )
	    except:
	        print('Failure in sending alert')
    
    try:
        print('test')
        instance_id = event["detail"]["instance-id"]
        print('Instance ID: ' + instance_id)
    except:
        sendalert('Failure in Spot', 'Unable to aquire instance ID')
        return
        
    try:
        instance = client_ec2.describe_instances(InstanceIds=[instance_id])
        instance_type = instance['Reservations'][0]['Instances'][0]['InstanceType']
        instance_tags = instance['Reservations'][0]['Instances'][0]['Tags']
        
    except:
        sendalert('Failure in Spot', 'Instance ID: ' + str(instance_id))
        return
    
    for tag in instance_tags:
        if tag['Key'] == 'Name':
            name = tag['Value']
        if tag['Key'] == 'Environment':
            environment = tag['Value']
        if tag['Key'] == 'Type':
            Type = tag['Value']
        if tag['Key'] == 'Owner':
            owner = tag['Value']
    
    
    ##Get Date##
    date = datetime.now()
    dateprint = date.strftime('%d-%b')
    date = date.strftime('%d-%b-%Y-%H-%M')
    print(date)
    
    state = 'SpotInterruption'
    spot_str = name+"$$$$"+instance_type+"$$$$"+region+"$$$$"+environment+"$$$$"+Type+"$$$$"+state+"$$$$"+str(date)
    print(spot_str)
    
    
    print("Upload File to Bucket S3")
    string = spot_str
    encoded_string = string.encode("utf-8")
    
    file_name = str(name) +"-"+str(state) +"-"+ str(date) +'.txt'
    
    bucket_name = "xxxxxxxx-logs"
    s3_path = file_name
    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).put_object(Key=s3_path, Body=encoded_string)



    SENDER = "xxxxxxx@earnix.com"
    
    if '@earnix.com' in owner:
        print("Owner OK")
    else:
        owner = owner+'@earnix.com'
        print(owner)

    RECIPIENT = ['xxxxxxx@earnix.com'']
    
    if environment == 'Development':
        RECIPIENT.append(owner)
        RECIPIENT.append('xxxxxxx@earnix.com')
        RECIPIENT.append('xxxxxxx@earnix.com')
    
    logo = "./Earnix.png"

    AWS_REGION = "eu-west-1"
    
    # The subject line for the email.
    SUBJECT = "Spot Interruption - "
    SUBJECT += name
    
    # The email body for recipients with non-HTML email clients.
    #BODY_TEXT = ("test")
                
    # The HTML body of the email.
    BODY_HTML = """
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>Demystifying Email Design</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        </head>
        <body style="margin: 0; padding: 0;">
        <table border="0" cellpadding="0" cellspacing="0" width="100%"> 
        <tr>
        <td style="padding: 10px 0 30px 0;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="800" style="border: 1.4px solid #cccccc; border-collapse: collapse;">
        <tr>
        <td align="center" >
        <img src="https://xxxxxxxx.s3-eu-west-1.amazonaws.com/xxxxxxx.jpg" alt="Creating Email Magic" width="400" height="350" style="display: block;" />
        </td>
        </tr>
        <tr>
        <td bgcolor="#ffffff" style="padding: 40px 30px 40px 30px;">
        <table border="0" cellpadding="0" cellspacing="0" width="100%">
        <tr>
        <td  style="color: #153643; font-family: Arial, sans-serif; font-size: 20px;">
        Hi,
        </td>
        </tr>
        <tr>
        <td  style="color: #153643; font-family: Arial, sans-serif; font-size: 20px;">
        <b>&nbsp;</b>
        </td>
        </tr>
        <tr>
        <td style="color: #153643; font-family: Arial, sans-serif; font-size: 20px;">
        The following Spot was interrupted:
        </td>
        </tr>
        <tr>
        <td  style="color: #153643; font-family: Arial, sans-serif; font-size: 20px;">
        <b>&nbsp;</b>
        </td>
        </tr>"""
        
    BODY_HTML += """<tr><td style="color: #153643; font-family: Arial, sans-serif; font-size: 20px;">Owner: &nbsp;"""
    BODY_HTML += str(owner)
    BODY_HTML += """</td></tr><tr><td  style="color: #153643; font-family: Arial, sans-serif; font-size: 20px;"><b>&nbsp;</b></td></tr>"""
    BODY_HTML += """   
        <tr>
        <table cellpadding="8" cellspacing="0" style="width:100%; border-collapse: collapse; color: #153643; font-family: Arial, sans-serif; font-size: 18px;">
        <tr>
        <th align="center" style="border-bottom: 1px solid #000; font-weight:bold">Name</th>
        <th align="center" style="border-bottom: 1px solid #000; font-weight:bold">Type</th>
        <th align="center" style="border-bottom: 1px solid #000; font-weight:bold">Region</th>
        <th align="center" style="border-bottom: 1px solid #000; font-weight:bold">Environment</th>
        <th align="center" style="border-bottom: 1px solid #000; font-weight:bold">Type</th>
        <th align="center" style="border-bottom: 1px solid #000; font-weight:bold">Date</th>
        </tr>
    """
    
    
    BODY_HTML += """<tr style="border: solid; border-width: 1px 0;">"""
    BODY_HTML += """<td align="center" style="border-bottom: 1px solid #000;">"""
    BODY_HTML += name
    BODY_HTML += """</td>"""
    BODY_HTML += """<td align="center" style="border-bottom: 1px solid #000;">"""
    BODY_HTML += instance_type
    BODY_HTML += """</td>"""
    BODY_HTML += """<td align="center" style="border-bottom: 1px solid #000;">"""
    BODY_HTML += region
    BODY_HTML += """</td>"""
    BODY_HTML +="""<td align="center" style="border-bottom: 1px solid #000;">"""
    BODY_HTML += environment
    BODY_HTML +="""</td>"""
    BODY_HTML +="""<td align="center" style="border-bottom: 1px solid #000;">"""
    BODY_HTML += Type
    BODY_HTML +="""</td>"""
    BODY_HTML +="""<td align="center" style="border-bottom: 1px solid #000;">"""
    BODY_HTML += dateprint
    BODY_HTML +="""</td></tr>"""
    
    
    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    # Create a new SES resource and specify a region.
    print("work")
    
    #client = boto3.client('ses',region_name='eu-west-1')
    if len(RECIPIENT) >= 1:
        for i in RECIPIENT:
            # Try to send the email.
            try:
                #Provide the contents of the email.
                response = client_ses.send_email(
                    Destination={
                        'ToAddresses': [
                            i,
                        ],
                    },
                    Message={
                        'Body': {
                            'Html': {
                                'Charset': CHARSET,
                                'Data': BODY_HTML,
                            },
                        },
                        'Subject': {
                            'Charset': CHARSET,
                            'Data': SUBJECT,
                        },
                    },
                    Source=SENDER,
                )
            # Display an error if something goes wrong.	
            except:
                print("Email Error!")
            else:
                print("Email sent!")