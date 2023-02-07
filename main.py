import os
import requests
import tqdm

from config import *

# Set the base URL for the ZenDesk API
base_url = "https://{subdomain}.zendesk.com/api/v2".format(subdomain="m2nikninc")

# Set the headers for the API request
headers = {
    "Content-Type": "application/json",
    "Authorization": "Basic {api_key}".format(api_key=api_key),
}

# Set the folder where attachments will be downloaded
download_folder = "attachments"

# Create the download folder if it does not already exist
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

# Set the page size for the API request (number of tickets to retrieve per page)
page_size = 100
page = 1
ticket_count = 0

# Set a flag to indicate whether there are more tickets to retrieve
more_tickets = True
ss=[]

while more_tickets:
    # Make the API request to retrieve tickets assigned to the user
    response = requests.get(
        "{base_url}/tickets.json".format(base_url=base_url),
        params={
            "page": page,
            "per_page": page_size,
        },
        headers=headers,
        auth=(f"{email}/token", api_key),
    )
    
    # Check the status code of the response
    if response.status_code != 200:
        print("An error occurred: {}".format(response.text))
        break
    
    # Get the list of tickets from the response
    tickets = response.json()["tickets"]
    
    # Loop through the tickets and download their attachments
    for ticket in tickets:
        
        # Only comb through open tickets
        if (ticket["status"] != "open" or user_id != ticket["assignee_id"]): #  
            continue
        
        response = requests.get(
            f"{base_url}/tickets/{ticket['id']}/comments.json",
            headers=headers,
            auth=(f"{email}/token", api_key),
        )
        
        if response.status_code != 200:
            print("An error occurred: {}".format(response.text))
            break
        
        i = 0
        # Loop through the attachments in each comment and download them
        for c in response.json()["comments"]:
            for attachment in c["attachments"]:
                # Get the URL and file name of the attachment
                url = attachment["content_url"]
                file_name = attachment["file_name"]
                
                # Download the attachment
                attachment_response = requests.get(url)

                response = requests.get(
                    f"{base_url}/users/{c['author_id']}",
                    headers=headers,
                    auth=(f"{email}/token", api_key),
                )
                
                # Check the status code of the response
                if response.status_code != 200:
                    print("An error occurred: {}".format(response.text))
                    break
                
                # Get the list of tickets from the response
                user = response.json()["user"]
                if "Natasha Mini" in user["name"]: break # todo: delete the file
                
                # Save the attachment to the download folder
                extension = '.pdf'
                while(True):
                    try: 
                        with open(p:=os.path.join(download_folder, user['name']+"_"+str(i)+extension), "wb") as f:
                            f.write(attachment_response.content)
                        break
                    except: 
                        i+=1
                        if i > 100: print("error"); break
                i+=1
                
    # Increment the ticket count and page number
    ticket_count += len(tickets)
    page += 1
    
    # Set the flag to indicate whether there are more tickets to retrieve
    more_tickets = len(tickets) == page_size

print("Downloaded attachments for {} tickets".format(ticket_count))