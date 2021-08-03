import requests
import json
import base64
from datetime import datetime
from pick import pick
import pyperclip

JIRA_MAIL = '' # Ex: dai.pham@paradox.ai
JIRA_API_TOKEN = '' # Get here: https://id.atlassian.com/manage-profile/security/api-tokens
JIRA_URL = 'https://paradoxai.atlassian.net'

credentail = "Basic " + base64.b64encode(bytes(JIRA_MAIL + ':' + JIRA_API_TOKEN, "utf-8")).decode("utf-8") 
headers = {
  "Accept": "application/json",
  "Content-Type": "application/json",
  "Authorization" : credentail
}
url = JIRA_URL + '//rest/api/3/search'

def api_get_issues(type, url, headers):
  if type == "doing":
    params = {
      'jql': """
          project = OL &
          assignee = currentUser() &
          issuetype in (Bug, Task) &
          status = 'In Progress' or 
          ( status changed during (startOfDay(), now()) by currentUser() &
          status != Open )
      """,
      'maxResults': 10,
      "fields": ["summary", "status"],
    }
  else:
    params = {
      'jql': """
        project = OL &
        assignee = currentUser() &
        status = Open
      """,
      'maxResults': 5,
      "fields": ["summary"],
      'orderBy': '-priority'
    }
  res = requests.request("GET", url, params=params, headers=headers)
  return json.loads(res.text).get("issues")

print("Fetching data.............")
doing_issues = api_get_issues('doing', url, headers)
report = "Today Tasks: \n"

# Gen Today task
in_progress_issues = []
for issue in doing_issues:
  field_data = issue.get('fields')
  status = field_data.get('status').get('name')
  summary = field_data.get('summary')
  ticket_code = issue.get('key')
  line = f"- {ticket_code}: {summary}"
  if status == "In Progress":
    in_progress_issues.append(line)
    percent = input(f"Enter percent {ticket_code} - {summary}: ")
    line += f" - {percent}%"
  else:
    line += f" - {status.upper()}"
  report += f"{line} \n"

todo_issues = api_get_issues('todo', url, headers)
# Gen tomorrow task
if datetime.today().weekday() == 4: # Check today is Friday
  report += "Monday Tasks: \n"
else:
  report += "Tomorrow Tasks: \n"

for line in in_progress_issues:
  report += f"{line} \n"

# Choose from terminal
title = 'Please choose your tomorrow task (press SPACE to mark, ENTER to continue): '
options = ['- Fix bugs']
for issue in todo_issues:
  field_data = issue.get('fields')
  summary = field_data.get('summary')
  ticket_code = issue.get('key')
  options.append(f"- {ticket_code}: {summary}")
selected = pick(options, title, multiselect=True, min_selection_count=0)
for item in selected:
  report += f"{item[0]} \n"

print('Copying report to clipboard...')
pyperclip.copy(report)
print('========== Report ===========')
print(report)