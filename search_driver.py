import os
import requests
import json
import sys
import search_assets_git_test
import socket
import time 
from datetime import datetime

start_time = time.time()

#loading repos.json
with open('repos.json') as json_data:
    d = json.load(json_data)


#loading queries into a list 
query_file=open("queries", "r")
queries=[]
for q in query_file:
	q=q.strip()
	queries.append(q)


#getting repository info
repo_names = d['repos'].keys()
repo = d['repos']
length = len(repo_names)
#git_repos = []



#opening a file to write logs to
file_name = "out_"+socket.gethostname()+"_"+str(datetime.now())+".log"
fo = open(file_name,"a")

for i in range(0,length):
	search_params=[]
	key=repo_names[i]
	search_params.append(str(key))
	search_params.append(str(repo[key]['url']))
	if 'github' in str(repo[key]['url']) or 'bitbucket' in str(repo[key]['url']):
		list_to_write = search_assets_git_test.search_git(search_params,queries)   #calling a function in search.py 
		print "===================================="
	else:
		print ' feature not supported'
	for list_element in list_to_write:
		fo.write(list_element)
fo.close()


#calculating execution time to keep track of efficiency 
print "******************************"
print("--- %s seconds ---" % (time.time() - start_time))
print "******************************"

