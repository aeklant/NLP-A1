#!/usr/bin/env python

# ibmTrain.py
# 
# This file produces 11 classifiers using the NLClassifier IBM Service
# 
# TODO: You must fill out all of the functions in this file following 
# 		the specifications exactly. DO NOT modify the headers of any
#		functions. Doing so will cause your program to fail the autotester.
#
#		You may use whatever libraries you like (as long as they are available
#		on CDF). You may find json, request, or pycurl helpful.
#

###IMPORTS###################################
import re
import json
import requests

TOTAL_EXAMPLES = 1600000
SUBSET_TOTAL = 11000
###HELPER FUNCTIONS##########################

def convert_training_csv_to_watson_csv_format(input_csv_name, group_id, output_csv_name): 
	# Converts an existing training csv file. The output file should
	# contain only the 11,000 lines of your group's specific training set.
	#
	# Inputs:
	#	input_csv - a string containing the name of the original csv file
	#		ex. "my_file.csv"
	#
	#	output_csv - a string containing the name of the output csv file
	#		ex. "my_output_file.csv"
	#
	# Returns:
	#	None
	
	neg_lower_bound = group_id * (SUBSET_TOTAL/2)	
	neg_upper_bound = ((group_id + 1) * (SUBSET_TOTAL/2)) - 1
	pos_lower_bound = neg_lower_bound + (TOTAL_EXAMPLES/2)
	pos_upper_bound = neg_upper_bound + (TOTAL_EXAMPLES/2)

	input_file = open(input_csv_name)
	output_file = open(output_csv_name, "w")

	for i, line in enumerate(input_file):
	    if (neg_lower_bound <= i <= neg_upper_bound or
                pos_lower_bound <= i <= pos_upper_bound):
	        
	        line = re.sub(r"\n", r"\\n", line)
	        line = re.sub(r"\t", r"\\t", line)
	        items = line.split("\",\"")
	        items[0] = items[0][1:]
	        items[-1] = items[-1][:-2]
                text = re.sub(r"\"", r"", items[5])
                if ',' in text:
                    text = "\"" + text + "\""
	        output_file.write(text + ",")
	        output_file.write(items[0] + "\n")

	input_file.close()
	output_file.close()

	return
	
def extract_subset_from_csv_file(input_csv_file, n_lines_to_extract, output_file_prefix='ibmTrain'):
	# Extracts n_lines_to_extract lines from a given csv file and writes them to 
	# an outputfile named ibmTrain#.csv (where # is n_lines_to_extract).
	#
	# Inputs: 
	#	input_csv - a string containing the name of the original csv file from which
	#		a subset of lines will be extracted
	#		ex. "my_file.csv"
	#	
	#	n_lines_to_extract - the number of lines to extract from the csv_file, as an integer
	#		ex. 500
	#
	#	output_file_prefix - a prefix for the output csv file. If unspecified, output files 
	#		are named 'ibmTrain#.csv', where # is the input parameter n_lines_to_extract.
	#		The csv must be in the "watson" 2-column format.
	#		
	# Returns:
	#	None
	
	input_file = open(input_csv_file)
	output_file = open(output_file_prefix + str(n_lines_to_extract) + ".csv", "w")

	for i, line in enumerate(input_file):
	    if (0 <= i < n_lines_to_extract/2 or
	        SUBSET_TOTAL/2 <= i < (SUBSET_TOTAL/2 + (n_lines_to_extract/2))):

	        output_file.write(line)

	input_file.close()
	output_file.close()
	
	return
	
def create_classifier(username, password, n, input_file_prefix='ibmTrain'):
	# Creates a classifier using the NLClassifier service specified with username and password.
	# Training_data for the classifier provided using an existing csv file named
	# ibmTrain#.csv, where # is the input parameter n.
	#
	# Inputs:
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	n - identification number for the input_file, as an integer
	#		ex. 500
	#
	#	input_file_prefix - a prefix for the input csv file, as a string.
	#		If unspecified data will be collected from an existing csv file 
	#		named 'ibmTrain#.csv', where # is the input parameter n.
	#		The csv must be in the "watson" 2-column format.
	#
	# Returns:
	# 	A dictionary containing the response code of the classifier call, will all the fields 
	#	specified at
	#	http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/natural-language-classifier/api/v1/?curl#create_classifier
	#   
	#
	# Error Handling:
	#	This function should throw an exception if the create classifier call fails for any reason
	#	or if the input csv file does not exist or cannot be read.
	#
	
	url = "https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers"
	auth = (username, password)
        input_file_name = input_file_prefix + str(n) + ".csv"
        training_data = open(input_file_name, 'rb')
       
        language = 'en'
        name = 'Classifier ' + str(n)
        params = {'language':language, 'name':name}
                  
        files = [('training_metadata', ('training.json', json.dumps(params))),
                 ('training_data', training_data)]	

        headers = {'accept':'application/json'}

        r = requests.post(url, files=files, auth=auth, headers=headers)

        if not 200 <= r.status_code <= 299: 
            status = response.status_code
	    raise HTTPException('The classifier call failed. Status code: '
	                        + status)
	return
	
if __name__ == "__main__":
	import os

	GID = 26
	
        username = '9877636d-8c98-46a8-9460-9c1ef01162be'
        password = 'ivzWkXB4DNb9'

	### STEP 1: Convert csv file into two-field watson format
	input_csv_name = '/u/cs401/A1/tweets/training.1600000.processed.noemoticon.csv'
	#DO NOT CHANGE THE NAME OF THIS FILE
	output_csv_name = os.path.join(os.getcwd(), 'training_11000_watson_style.csv')
	convert_training_csv_to_watson_csv_format(input_csv_name, GID, output_csv_name)
	
	subsets = [500, 2500, 5000]
	for n in subsets:
	    ### STEP 2: Save 3 subsets in the new format into ibmTrain#.csv files
	    extract_subset_from_csv_file(output_csv_name, n, 'hail_mary')
	    ### STEP 3: Create the classifiers using Watson
            create_classifier(username, password, n)
