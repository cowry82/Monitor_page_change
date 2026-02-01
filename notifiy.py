import json
import urllib.request
import urllib.error
import time
import ssl

# Load configuration file
def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f"Failed to read configuration file: {e}")
        return None

# Send Lark notification
def send_lark_notification(url, changes):
    config = load_config()
    if not config or not config.get('lark_webhook_url'):
        print("Lark Webhook URL not configured, skipping notification")
        return False
    
    webhook_url = config['lark_webhook_url']
    
    # Build markdown message
    message = f"## Web Page Change Notification\n\n"
    message += f"**URL**: {url}\n\n"
    message += f"**Detection Time**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for element_type, change_type, change_content in changes:
        if element_type == 'text' and change_type == 'modified':
            # Use special format for text changes
            modified_content = change_content.replace('- ', 'Old content: ').replace('+ ', 'New content: ')
            message += f"### Text Changes\n```\n{modified_content}\n```\n\n"
        else:
            message += f"### {element_type} Changes\n```\n{change_content}\n```\n\n"
    
    # Build Lark message format
    data = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "Web Page Change Notification"
                },
                "template": "red"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": message
                    }
                }
            ]
        }
    }
    
    try:
        # Create SSL context that doesn't verify certificates
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10, context=context) as response:
            response_data = response.read().decode('utf-8')
            print(f"Lark notification sent successfully: {response_data}")
            return True
    except Exception as e:
        print(f"Failed to send Lark notification: {e}")
        return False