#!/usr/bin/env python

# ibmTest.py
# 
# This file tests all 11 classifiers using the NLClassifier IBM Service
# previously created using ibmTrain.py
# 
# TODO: You must fill out all of the functions in this file following 
# 		the specifications exactly. DO NOT modify the headers of any
#		functions. Doing so will cause your program to fail the autotester.
#
#		You may use whatever libraries you like (as long as they are available
#		on CDF). You may find json, request, or pycurl helpful.
#		You may also find it helpful to reuse some of your functions from ibmTrain.py.
#
import requests
import json
from httplib import HTTPException

URL = "https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers"

def get_classifier_ids(username, password):
	# Retrieves a list of classifier ids from a NLClassifier service 
	# an outputfile named ibmTrain#.csv (where # is n_lines_to_extract).
	#
	# Inputs: 
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#		
	# Returns:
	#	a list of classifier ids as strings
	#
	# Error Handling:
	#	This function should throw an exception if the classifiers call fails for any reason
	#
	
	res = []

	response = requests.get(URL, auth=(username, password))

	if not 200 <= response.status_code <= 299:
	    status = response.status_code
	    raise HTTPException('The classifier call failed. Status code: '
	                        + status)

	data = json.loads(response.content)

	for classifier in data['classifiers']:
	    res.append(classifier['classifier_id'])

	return res
	

def assert_all_classifiers_are_available(username, password, classifier_id_list):
	# Asserts all classifiers in the classifier_id_list are 'Available' 
	#
	# Inputs: 
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	classifier_id_list - a list of classifier ids as strings
	#		
	# Returns:
	#	None
	#
	# Error Handling:
	#	This function should throw an exception if the classifiers call fails for any reason AND 
	#	It should throw an error if any classifier is NOT 'Available'
	#
	
	for classifier_id in classifier_id_list:
	    response = requests.get(URL+"/"+classifier_id, auth=(username, password))
	    if not 200 <= response.status_code <= 299:
	        status = response.status_code
	        raise HTTPException('The classifier call failed. Status code: '
	                            + status)

	    data = json.loads(response.content)
	    if not data['status'].lower() == 'available':
	        raise HTTPException('At least one classifier is unavailable')
	
	return

def classify_single_text(username, password, classifier_id, text):
	# Classifies a given text using a single classifier from an NLClassifier 
	# service
	#
	# Inputs: 
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	classifier_id - a classifier id, as a string
	#		
	#	text - a string of text to be classified, not UTF-8 encoded
	#		ex. "Oh, look a tweet!"
	#
	# Returns:
	#	A "classification". Aka: 
	#	a dictionary containing the top_class and the confidences of all the possible classes 
	#	Format example:
	#		{'top_class': 'class_name',
	#		 'classes': [
	#					  {'class_name': 'myclass', 'confidence': 0.999} ,
	#					  {'class_name': 'myclass2', 'confidence': 0.001}
	#					]
	#		}
	#
	# Error Handling:
	#	This function should throw an exception if the classify call fails for any reason 
	#
	
	data = json.dumps({'text':text.encode('utf-8')})
	classify_url = URL + "/" + classifier_id + "/classify"
	headers = {'accept':'application/json', 
	           'content-type':'application/json'}

	response = requests.post(classify_url, auth=(username, password), data=data, 
	                         headers=headers)

	if not 200 <= response.status_code <= 299:
	    status = response.status_code
	    raise HTTPException('The classifier call failed. Status code: '
	                        + status)
	
	prediction = json.loads(response.content)
	return {'classes':prediction['classes'], 'top_class':prediction['top_class']}


def classify_all_texts(username, password, input_csv_name):
        # Classifies all texts in an input csv file using all classifiers for a given NLClassifier
        # service.
        #
        # Inputs:
        #       username - username for the NLClassifier to be used, as a string
        #
        #       password - password for the NLClassifier to be used, as a string
        #      
        #       input_csv_name - full path and name of an input csv file in the 
        #              6 column format of the input test/training files
        #
        # Returns:
        #       A dictionary of lists of "classifications".
        #       Each dictionary key is the name of a classifier.
        #       Each dictionary value is a list of "classifications" where a
        #       "classification" is in the same format as returned by
        #       classify_single_text.
        #       Each element in the main dictionary is:
        #       A list of dictionaries, one for each text, in order of lines in the
        #       input file. Each element is a dictionary containing the top_class
        #       and the confidences of all the possible classes (ie the same
        #       format as returned by classify_single_text)
        #       Format example:
        #              {'classifiername':'classifiername'
        #                      [
        #                              {'top_class': 'class_name',
        #                              'classes': [
        #                                        {'class_name': 'myclass', 'confidence': 0.999} ,
        #                                         {'class_name': 'myclass2', 'confidence': 0.001}
        #                                          ]
        #                              },
        #                              {'top_class': 'class_name',
        #                              ...
        #                              }
        #                      ]
        #              , 'classifiername2': 'classifiername2'
        #                      [
        #                      ...
        #                      ]
        #              ...
        #              }
        #
        # Error Handling:
        #       This function should throw an exception if the classify call fails for any reason
        #       or if the input csv file is of an improper format.
        #

	input_raw_data = open(input_csv_name)
	lines = input_raw_data.readlines()
	input_raw_data.close()

	classifier_ids = get_classifier_ids(username, password)
	classifier_names = []

	for ix in classifier_ids:
	    response = requests.get(URL+"/"+ix, auth=(username,password))

	    if not 200 <= response.status_code <= 299:
	        status = response.status_code
	        raise HTTPException('The classifier call failed. Status code: '
	                            + status)

	    data = json.loads(response.content)
	    classifier_names.append(data['name'])

	res = {}
	for ix, name in zip(classifier_ids, classifier_names):
	    res[name] = []
	    for line in lines:
	        line = line.split("\",\"")
	        text = line[5]

	        # raises HTTPError if classify call fails
	        res[name].append(classify_single_text(username, password, 
	                                              ix, text)
	                        )
        return res


def compute_accuracy_of_single_classifier(classifier_dict, input_csv_file_name):
	# Given a list of "classifications" for a given classifier, compute the accuracy of this
	# classifier according to the input csv file
	#
	# Inputs:
	# 	classifier_dict - A list of "classifications". Aka:
	#		A list of dictionaries, one for each text, in order of lines in the 
	#		input file. Each element is a dictionary containing the top_class
	#		and the confidences of all the possible classes (ie the same
	#		format as returned by classify_single_text) 	
	# 		Format example:
	#			[
	#				{'top_class': 'class_name',
	#			 	 'classes': [
	#						  	{'class_name': 'myclass', 'confidence': 0.999} ,
	#						  	{'class_name': 'myclass2', 'confidence': 0.001}
	#							]
	#				},
	#				{'top_class': 'class_name',
	#				...
	#				}
	#			]
	#
	#	input_csv_name - full path and name of an input csv file in the  
	#		6 column format of the input test/training files
	#
	# Returns:
	#	The accuracy of the classifier, as a fraction between [0.0-1.0] (ie percentage/100). \
	#	See the handout for more info.
	#
	# Error Handling:
	# 	This function should throw an error if there is an issue with the 
	#	inputs.
	#
	
	num_elements = len(classifier_dict)

	# automatically raises error if anything wrong with input
	input_raw_data = open(input_csv_file_name)
	lines = input_raw_data.readlines()
	input_raw_data.close()

	correct_predictions = 0
	for ix, line in enumerate(lines):
	    line = line.split("\",\"")
            target = line[0][1]

	    if target == classifier_dict[ix]['top_class']:
	        correct_predictions += 1
	
	# might throw a division by zero error if classifier_dict is empty 
	return correct_predictions/(num_elements * 1.0)

def compute_average_confidence_of_single_classifier(classifier_dict, input_csv_file_name):
	# Given a list of "classifications" for a given classifier, compute the average 
	# confidence of this classifier wrt the selected class, according to the input
	# csv file. 
	#
	# Inputs:
	# 	classifier_dict - A list of "classifications". Aka:
	#		A list of dictionaries, one for each text, in order of lines in the 
	#		input file. Each element is a dictionary containing the top_class
	#		and the confidences of all the possible classes (ie the same
	#		format as returned by classify_single_text) 	
	# 		Format example:
	#			[
	#				{'top_class': 'class_name',
	#			 	 'classes': [
	#						  	{'class_name': 'myclass', 'confidence': 0.999} ,
	#						  	{'class_name': 'myclass2', 'confidence': 0.001}
	#							]
	#				},
	#				{'top_class': 'class_name',
	#				...
	#				}
	#			]
	#
	#	input_csv_name - full path and name of an input csv file in the  
	#		6 column format of the input test/training files
	#
	# Returns:
	#	The average confidence of the classifier, as a number between [0.0-1.0]
	#	See the handout for more info.
	#
	# Error Handling:
	# 	This function should throw an error if there is an issue with the 
	#	inputs.
	#
	
	# automatically raises error if anything wrong with input
	input_raw_data = open(input_csv_file_name)
	lines = input_raw_data.readlines()
	input_raw_data.close()

	num_correct = 0
	num_incorrect = 0

	sum_correct_confidence = 0
	sum_incorrect_confidence = 0
	
	for ix, line in enumerate(lines):
	    line = line.split("\",\"")
            target = line[0][1]

	    if target == classifier_dict[ix]['top_class']:
	        num_correct += 1
	        confidence = classifier_dict[ix]['classes'][0]['confidence']
	        sum_correct_confidence += confidence
	    else:
	        num_incorrect += 1
	        confidence = classifier_dict[ix]['classes'][0]['confidence']
	        sum_incorrect_confidence += confidence
	
	avg_correct_confidence = (1.0 * sum_correct_confidence)/num_correct
	avg_incorrect_confidence = (1.0 * sum_incorrect_confidence)/num_incorrect

	return (avg_correct_confidence, avg_incorrect_confidence)


if __name__ == "__main__":

	# The following values are hardcoded since there is no usage 
	# description in the handout. We assume the script will run
	# without parameters. This could easily be changed in the future.
	input_test_data = '/u/cs401/A1/tweets/testdata.manualSUBSET.2009.06.14.csv'
	username = '9877636d-8c98-46a8-9460-9c1ef01162be'
	password = 'ivzWkXB4DNb9'
	
	#STEP 1: Ensure all 11 classifiers are ready for testing
	print ("\n" * 3)
	print ("Obtaining list of classifiers...")
	classifier_ids = get_classifier_ids(username, password)	
	print ("\n" * 3)
	print ("Classifiers found!")
	print ("*" * 80)

	print ("\n" * 3)
	print ("Checking classifiers for availability...")
	# No news here means good news.
	assert_all_classifiers_are_available(username, password, classifier_ids)
	print ("\n" * 3)
	print ("All classifiers are available!!!")
	print ("*" * 80)

	#STEP 2: Test the test data on all classifiers
	print ("\n" * 3)
	print ("Classifying texts... This might take awhile...")
	predictions = classify_all_texts(username, password, input_test_data)
	print ("\n" * 3)
	print ("All input texts have been classified!!!")
	print ("*" * 80)
	
	for classifier in predictions:
	    print ("\n" * 3)
	    print ("Calculating accuracy and confidence for: %s" % classifier)

	    #STEP 3: Compute the accuracy for each classifier
	    acc = compute_accuracy_of_single_classifier(predictions[classifier], 
	                                                input_test_data)
	    print ("\tAccuracy: \t%s" % acc)

	    #STEP 4: Compute the confidence of each class for each classifier
	    conf = compute_average_confidence_of_single_classifier(predictions[classifier],
	                                                           input_test_data) 
	    print ("\tConfidence when correct: \t%s" % conf[0])
	    print ("\tConfidence when incorrect: \t%s" % conf[1])
	    print ("*" * 80)

	print ("\n" * 3)
	print ("Script finished.")
	print ("*" * 80)
