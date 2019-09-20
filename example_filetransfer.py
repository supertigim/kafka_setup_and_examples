# -*- coding:utf-8 -*-
import os
import sys
import json
#import binascii # For Python 2.7

from confluent_kafka import Producer, Consumer, KafkaException
import random 
from collections import defaultdict
from datetime import datetime

#######################################################

CHUNK_SIZE = 1024 * 3       # 3K         
BROKER = 'YOUR_BROKER_IP:9092'
BROKER_ZK = BROKER.split(':')[0] + ':2181'  # Not used, just for test 
TOPIC_TEST_FILE = 'test.file'

#######################################################


def file_to_json_list(file_path, dedicated_filename=None, chunk_size=CHUNK_SIZE):
    '''
        args- file_path: file path including file name at the end
            - chunck_size: maximum size of data item in JSON 
        ret- list of JSON
    '''
    if dedicated_filename is None:
        filename = file_path.split('/')[-1] # to get extension 
        filename = str(datetime.now()).split('.')[0].replace(' ','-').replace(':','-') + '.' + filename.split('.')[-1]
    else:
        filename = dedicated_filename.split('.')[0] + '.' + file_path.split('/')[-1].split('.')[-1]

    list_of_splited_file_bin = []
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk: break
            list_of_splited_file_bin.append(chunk)

    def make_serialized_json(filename, cur_seq, total_num, bin_data):
        json_data = {}
        json_data['filename'] = filename
        json_data['cur_seq'] = cur_seq
        json_data['total_num'] = total_num 
        #json_data['data'] = binascii.hexlify(bin_data) # For python 2.7
        json_data['data'] = bin_data.hex()      # Binary to Hex

        return json.dumps(json_data)            # Serialization 

    ret = []
    for i, bin_data in enumerate(list_of_splited_file_bin):
        ret.append(make_serialized_json(filename, i+1, len(list_of_splited_file_bin), bin_data))
    
    return ret, filename

def json_list_to_file(json_list, path):
    '''
        args- json_list: list of json 
              path: path where to save 
        ret- None 
    '''
    if len(json_list) == 0: return  # nothing to save 
    filename = json.loads(json_list[0])['filename']

    with open(path + '/' + filename, 'wb') as f:
        for j in json_list:
            #data = bytearray.fromhex(json.loads(j)['data']) # For Python 2.7
            data = bytes.fromhex(json.loads(j)['data']) # Hex to Binary 
            f.write(data)

def test_generate_json_list_for_an_image_and_restore_the_image():
    '''
        Test json to file conversion and vice versa  
    '''
    path = 'data'
    filename = 'sample_map.pgm'

    file_path = path +'/' + filename

    # From File to Json
    json_list, filename= file_to_json_list(file_path)

    # From Json to File
    json_list_to_file(json_list, path)

    print('Done test: generate JSON list for an image and restore the image')


def test_produce_json_list():
    '''
        Test Producing Json List to Kafka
    '''
    print ('\nConsumer test started... ')

    # In case of emptying the topic before sending files 
    #command = './kafka_2.12-2.2.0/bin/kafka-delete-records.sh --bootstrap-server ' + BROKER + ' -offset-json-file ./empty_topic.json'
    #os.system(command)

    FIRST_FILE_PATH = 'put your first file'
    SECOND_FILE_PATH = 'put your second file'
    
    # First file 
    json_list_yaml, filename_first = file_to_json_list(FIRST_FILE_PATH)
    # Second file 
    json_list_pgm, filename_second = file_to_json_list(SECOND_FILE_PATH, filename_first)

    # merge two JSON lists
    json_list = json_list_yaml + json_list_pgm
    sent_files = [filename_first, filename_second]

    conf = {'bootstrap.servers': BROKER}

    # Create Producer instance
    p = Producer(**conf)

    # Produce each json to Kafka
    for j in json_list:
        try:
            # Produce line (without newline)
            p.produce(TOPIC_TEST_FILE, j)

        except BufferError:
            sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %len(p))

        # Serve delivery callback queue.
        # NOTE: Since produce() is an asynchronous API this poll() call
        #       will most likely not serve the delivery callback for the
        #       last produce()d message.
        p.poll(0)

    # Wait until all messages have been delivered
    p.flush()

    for filename in sent_files:
        print(filename + ' has been sent to Kafka')

def test_consume_and_restore_image():
    '''
        Test consuming JSON List from Kafka and restore an file from it 
    '''
    group = str(random.random()) # Randomly generate Group ID
    conf = {'bootstrap.servers': BROKER
            , 'group.id': group
            , 'session.timeout.ms': 6000
            , 'auto.offset.reset': 'earliest' #'latest'
            }

    c = Consumer(conf)
    c.subscribe([TOPIC_TEST_FILE])

    path = 'received'
    received_data = defaultdict(list)

    print('\nKafka consumer started - group id:', group)
    try:
        while True:
            msg = c.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                #print(msg.topic())
                data = json.loads(msg.value())  # JSON to Python Dictionary
                filename = data['filename']
                cur_seq = data['cur_seq']
                total_num = data['total_num']

                received_data[filename].append(msg.value())
                if cur_seq == total_num:
                    json_list_to_file(received_data[filename], path)
                    del received_data[filename]  # delete key-value from dictionary 
                    print(filename + ' file has been received!')

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')

    finally:
        # Close down consumer to commit final offsets.
        c.close()


if __name__ == '__main__':
    test_produce_json_list()
    #test_consume_and_restore_image()

# end of file