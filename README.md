# Compromised Asset Search Automation

## How to get this script working? 
* Clone the repository
* Follow repos_template.json to create repos.json that contains all the repositories that need to be scanned. 
* Save it as repos.json
* Modify query_parameters_template.json with parameters you need to search for along with the regular expression for the same. 
* Save it as query_parameters.json
* run search_driver.py 


## NOTE: 
Bitbucket requires an active session for private repositories. You might need to log in to be able to scan the repositories using this script. The account you will use for logging in should have access to the repository(ies) you are scanning. 

## TO-DO:
* Fix the session issue
* Eliminate false positives

