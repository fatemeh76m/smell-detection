import csv
import requests
import subprocess
import os
import stat
from git import Repo



CSV_PATH = './dataset.csv'
BASE_FOLDER_NAME = './repositories/'
OUTPUT_FOLDER_NAME = './outputs'
DESIGNATE_PATH = '~/Downloads/DesigniteJava.jar'
REPO_LIMIT = 5


class DesigniteStatistics(object):
	def __init__(self):
		super(DesigniteStatistics, self).__init__()
		self.links = []
		

	def get_repositories_links(self):
		print('Reading Repositories...')
		links = []
		try:
			with open(CSV_PATH, 'r') as file:
			    csvreader = csv.DictReader(file)
			    for row in csvreader:
			    	if (len(row) != 0 and row['language'] == 'Java' and int(row['size']) < 20000):
				        github_url = 'https://github.com/' + row['repository']
				        response = requests.get(github_url + '/info/refs?service=git-upload-pack')
				        #check if the repository is public
				        if (response.status_code == 200):
			        		links.append(github_url)
			        	if (len(links) == REPO_LIMIT):
			        		break
			file.close()
		except Exception as e:
			print('Error in reading repositories!')
		
		self.links = links


	def download_repositories(self):
		try:
			for link in self.links:
				print('Downloading ' + link + '...')
				folder_name = BASE_FOLDER_NAME + link.split('/')[-1]
				Repo.clone_from(link, folder_name)
		except Exception as e:
			print('Error in downloading repositories!')
		


	def run_designite_tool(self):
		print('Creating Bash Script...\n')
		try:
			with open ('run.sh', 'w') as rsh:
			    rsh.write('#!/bin/bash\n')
			    for link in self.links:
			    	rsh.write('java -jar ' + DESIGNATE_PATH + ' -i "' + BASE_FOLDER_NAME + 
			    		link.split('/')[-1] + '" -o "' + OUTPUT_FOLDER_NAME + '/' + link.split('/')[-1] + '"\n')
			st = os.stat('./run.sh')
			os.chmod('./run.sh', st.st_mode | stat.S_IEXEC)
			print('Running Bash Script...\n')
			subprocess.call('./run.sh', shell=True)
		except Exception as e:
			print('Error in running designite java tool!')
		


	def get_summary_statistics(self):
		print('\n--- Summary Statistics ---')
		try:
			for link in self.links:
				folder_name = OUTPUT_FOLDER_NAME + '/' + link.split('/')[-1]

				architecture_smells_path = folder_name + '/ArchitectureSmells.csv'
				architecture_smells_file = open(architecture_smells_path)
				architecture_smells = csv.reader(architecture_smells_file)
				architecture_smells_count = sum(1 for row in architecture_smells)
				architecture_smells_file.close()
				print('Project: ' + link + '\n')
				print('Architecture Smells: ' + str(architecture_smells_count) + '\n')

				design_smells_path = folder_name + '/DesignSmells.csv'
				design_smells_file = open(design_smells_path)
				design_smells = csv.reader(design_smells_file)
				design_smells_count = sum(1 for row in design_smells)
				design_smells_file.close()
				print('Design Smells: ' + str(design_smells_count) + '\n')

				implementation_smells_path = folder_name + '/ImplementationSmells.csv'
				implementation_smells_file = open(implementation_smells_path)
				implementation_smells = csv.reader(implementation_smells_file)
				implementation_smells_count = sum(1 for row in implementation_smells)
				implementation_smells_file.close()
				print('Implementation Smells: ' + str(implementation_smells_count) + '\n')

				print('Total Number of Smells: ' + str(implementation_smells_count + 
					design_smells_count + architecture_smells_count))

				print('-----------------------------')
		except Exception as e:
			print('Error in generating summary statistics!')
		



if __name__ == '__main__':
	designite_statistics = DesigniteStatistics()
	designite_statistics.get_repositories_links()
	designite_statistics.download_repositories()
	designite_statistics.run_designite_tool()
	designite_statistics.get_summary_statistics()