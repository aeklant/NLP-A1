#!/usr/bin/env python

def create_partitions(file_name, num_partitions):
    text = open(file_name).readlines()
    lines = enumerate(text)

    # find the line that signals beginning of data samples
    start_ix = 0
    for i, line in lines:
        if "@data" in line.strip():
            start_ix = i + 1
            break

    num_lines = len(text)
    num_examples = num_lines - (start_ix) 

    partition_size = num_examples/num_partitions

    ranges = []
    for i in range(num_partitions):
        neg_start = start_ix + (i * partition_size/2)
        neg_end = start_ix + ((i + 1) * partition_size/2) - 1
        pos_start = neg_start + (num_examples/2)
        pos_end = neg_end + (num_examples/2)

        ranges.append((neg_start, neg_end, pos_start, pos_end))

    return ranges

def create_cross_validation_files(file_path, partitions):
    input_file = open(file_path)
    text = input_file.readlines()
    input_file.close()

    start = partitions[0][0]
    for num, partition in enumerate(partitions):
        train = [] 
        test = []
        headers = []

        for i, line in enumerate(text):
            if (partition[0] <= i <= partition[1] or
                partition[2] <= i <= partition[3]):

                test.append(line)

            elif i > start:
                train.append(line)

            else:
                headers.append(line)

        train_output = open("train_xvalidation_" + str(num) + ".arff", "w")
        test_output = open("test_xvalidation_" + str(num) + ".arff", "w")

        for line in headers:
            train_output.write(line)
            test_output.write(line)

        for line in train:
            train_output.write(line)

        for line in test:
            test_output.write(line)

        train_output.close()
        test_output.close()

if __name__ == '__main__':
    file_path = '/h/u4/c5/03/c5escala/train.arff'
    num_partitions = 10
    
    ranges = create_partitions(file_path, num_partitions)
    create_cross_validation_files(file_path, ranges)
