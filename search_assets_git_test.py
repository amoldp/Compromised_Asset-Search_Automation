import sys
import os
import requests
import json
import subprocess
import re
import socket
from git import Repo
from pprint import pprint
from datetime import datetime

#root directory to store repos
root_dir =  os.getcwd()+"/data"

#regex for validating keys (not used anymore, keeping them for future reference)
aws_access_key_regex = '(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])'
aws_secret_key_regex = '(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])'
access_pattern = re.compile(aws_access_key_regex)
secret_pattern = re.compile(aws_secret_key_regex)

#opens query_parameters.json and loads parameters in a list
with open('query_parameters.json') as j_data:
	q = json.load(j_data)
key_regex = []
for k in q.keys():
	inner_q = q[str(k)]
	inner_keys =  inner_q.keys()
	for ik in inner_keys:
		tmp_tuple=str(ik+":"+inner_q[ik])
		#tmp_tuple=u''.join((ik, ':', inner_q[ik])).encode('utf-8').strip()
		print "tmp_tuple= " + tmp_tuple
		key_regex.append(tmp_tuple)



#function to search through all commits of a particular branch for all parameters
def search_all_commits(path_to_data,branch):
	result_tuple=[]
	os.chdir(path_to_data)
	get_commits = ['git' , 'rev-list', '--all']
	gc_out=subprocess.check_output(get_commits, stderr=subprocess.STDOUT)
	gc_out_split = gc_out.split('\n')
	
	try: 	
		for c in gc_out_split:
			try:
				if c != '':
					for param in key_regex:
						try:
							print "DEBUG: " + param
							print "Pass in the LOOP -------------- " + param 
							patt = re.compile(param)
							param_split=param.split(":")
							print "Searching for: " + param_split[0]
							print "Commit: " + c
							tuple_string =""
							ch_cmd = ['git', 'grep', '-P', str(param_split[1]), c]
							ch_out = subprocess.check_output(ch_cmd, stderr=subprocess.STDOUT)
								
							hits = ch_out.split('\n')

							for i in range(0,len(hits)):
								
								if hits[i]!='':
									hits_split = hits[i].split(':')
									#result_tuple.append("Searching in the branch --->" + branch+"\n")
									hits_split_string=""
									for j in range(2, len(hits_split)):
										#if len(hits_split[j])>200:
										#	tuple_string=tuple_string+ "   " + "File too large. "
										#	tuple_string=tuple_string+"\n\n"
										#	break 
										#else:

										if len(hits_split[j])<200:
											hits_split_string = hits_split_string + hits_split[j]
										else:
											hits_split_string = hits_split_string + hits_split[j][:200] +"   ...........FILE TOO LARGE"
										#print hits_split
										string_found = filter_results(hits_split[j],param_split[1])
										if string_found == "NONE":
											continue
										else:
											result_tuple.append("Searching in the branch --->" + branch+"\n")	
											tuple_string = 'Searching for: ' +param_split[0] +'\n'+'Commit Hash: ' + hits_split[0] +"\n" + 'File path: ' + hits_split[1] +"\n" + "String: "
											tuple_string=tuple_string+"  " + hits_split_string +"\n"
											tuple_string=tuple_string+"Found: "+ string_found+"\n\n"
										#if(filter_results_2(hits_split[j])==1):
										#	print "Match found *********************************"
										#	if len(hits_split[j])>200:
										#		tuple_string = 'Searching for: ' +param_split[0] +'\n'+'Commit Hash: ' + hits_split[0] +"\n" + 'File path: ' + hits_split[1] +"\n" + "String: "
										#		tuple_string=tuple_string+ "   " + "File too large. "
										#		tuple_string=tuple_string+"\n\n"
										#		break 
										#	else:
										#		tuple_string = 'Searching for: ' +param_split[0] +'\n'+'Commit Hash: ' + hits_split[0] +"\n" + 'File path: ' + hits_split[1] +"\n" + "String: "
										#		tuple_string=tuple_string+"  " + hits_split[j]
										#		tuple_string=tuple_string+"\n\n"
										#else:
										#	tuple_string = "No compromised assets"+ "\n\n"
										result_tuple.append(tuple_string)
										hits_split_string=""
									print tuple_string
								else:
									print "No hits"
									#continue
						except Exception,e:
							print "ERROR: "+ str(e) 
							continue 				
			except Exception,e:
				print "ERROR: "+ str(e) 
				continue 
	except Exception,e:
		result_tuple.append("Commit Hash: "+ c +"\n")
		result_tuple.append("No compromised asset \n\n")
		print "No compromised Asset"
		print "ERROR: " + str(e)
	return result_tuple


def filter_results(hit, reg):
	#fil_str = "[A-Za-z0-9/+=]+(![)}\]'\"\s]|$)"
	fil_str = "(?<![\s<>@#$%^&*+=\-\|\(\[\{\'\"])[A-Za-z0-9/+=]{20,40}(?![)}\(\{\[\]'\"\-\_\s])"
	filter_pattern = re.compile(reg)
	second_level_filter = re.compile(fil_str)
	match_group = re.search(filter_pattern, hit)
	if match_group:
		second_level_match_group = re.search(second_level_filter, match_group.group(0))
		if second_level_match_group:
			return second_level_match_group.group(0)
		else:
			return "NONE"
	else:
		return "NONE"

#executing 'git branch -a' to get a list of all branches 
def get_all_branches(path):
    cmd = ['git', '-C', path, 'branch', '-a']
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    return out


#function to get branches and checking out each branch before calling search_all_commits function 
def branches_and_search(path_to_data, queries):
	result_list = []
	remote_branches = get_all_branches(path_to_data)
	remote_branches_split=remote_branches.split()
	current_branch=remote_branches_split[1]
	print 'Searching in --> ' + current_branch
	result = search_all_commits(path_to_data,current_branch)
	result_list.append(result)

	other_branches=[]
	for i in range (5,len(remote_branches_split)):
		if current_branch in remote_branches_split[i]:
			continue
		else:
			print 'Searching in ---> '+ remote_branches_split[i] 
			
			ch_cmd=['git', '-C', path_to_data, 'checkout', remote_branches_split[i]]
			ch_out = subprocess.check_output(ch_cmd, stderr=subprocess.STDOUT)
			
			result = search_all_commits(path_to_data, remote_branches_split[i])
			result_list.append(result)
	ch_cmd=['git', '-C', path_to_data, 'checkout', current_branch]
	ch_out = subprocess.check_output(ch_cmd, stderr=subprocess.STDOUT)

	return result_list

#TODO: check if already cloned repository is up to date. If not, git pull ---> RESOLVED
def check_and_update_repo(path_to_data):
	repo = Repo(path_to_data)
	for remote in repo.remotes:
		remote.pull()
	print "Pulled to the latest code"
	return


#function to decide if repository is already cloned. If yes, search for queries in the folder or else clone the repository and search. 
def search_git(search_params,queries):
	list_to_write=[]
	repo_name=search_params[0]
	print "Current Repository ----> " + repo_name
	file_name = "completed_repositories" # a temporary logging file to keep track of repositories scanned
	fo_tmp = open(file_name,"a")
	url=search_params[1]
	fo_tmp.write(repo_name+"\n")
	fo_tmp.close()
	path_to_data=root_dir+"/"+repo_name
	try:
		if os.path.isdir(path_to_data):
			check_and_update_repo(path_to_data)
			result_list = branches_and_search(path_to_data, queries)
			print 'directory already present'
		else:
			Repo.clone_from(url, path_to_data, env={'GIT_SSH_COMMAND':'ssh -i ~/.ssh/id_rsa'})
			#Repo.clone_from(url , path_to_data)
			print "Repository Cloned"
			result_list = branches_and_search(path_to_data, queries)

		for res in result_list:
			list_to_write.append("Repository Name: " + repo_name + "\n")
			list_to_write.append("Repository URL: " + url + "\n\n")
			for r in res:
				list_to_write.append(r)	
			list_to_write.append("====================================================================== \n\n")
	
	except:
		list_to_write.append("Repository Name: " + repo_name + "\n")
		list_to_write.append("Repository URL: " + url + "\n")
		list_to_write.append("ERROR: Cannot access repository\n\n")
	
	return list_to_write
