Introduction  
============  

This project is to introduce how to setup kafka and some examples in Python and C++.  

Initial Setup  
==============  

Install Docker. Skip if you already have
```    
    $ sudo apt-get remove docker docker-engine docker.io  
    $ sudo apt-get update && sudo apt-get install apt-transport-https ca-certificates curl software-properties-common  
    $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -  
    $ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    $ sudo apt-get update && sudo apt-cache search docker-ce

    docker-ce - Docker: the open-source application container engine

    $ sudo apt-get update && sudo apt-get install docker-ce docker-compose
    $ sudo usermod -aG docker $USER
```  

Clone source code  
```  
    $ git clone --recursive https://github.com/supertigim/kafka_setup_and_examples.git  
    $ cd kafka_setup_and_examples
```

Setup Python environment       
```  
    $ conda create -n kafka python=3  
    $ source activate kafka  
    $(kafka) pip install -r requirements.txt  
```  

Kafka Installation  
==================  

Pull Kafka Docker image  

```
    $ docker pull wurstmeister/kafka
```

Change KAFKA_ADVERTISED_HOST_NAME in docker-dompose-single-broker.yml into **127.0.0.1** (for local use)

```
    $ cd kafka-docker

    # go to line 12
    $ vim docker-dompose-single-broker.yml
```

Start

```
    $ docker-compose -f docker-compose-single-broker.yml up
```

Stop (Open another terminal)

```
    $ docker-compose stop 
```

## Test 

The version of docker written in "Dockerfile" needs to be downloaded from the [link](http://archive.apache.org/dist/kafka/). 

For example, if the setting is like below, download **kafka_2.12-2.2.0.tgz** files.   

    ARG kafka_version=2.2.0  
    ARG scala_version=2.12  

Then, unzip the file  

```  
    $ tar xzvf kafka_2.12-0.10.2.0.tgz  
    $ cd kafka_2.12-0.10.2.0  
```  

Create a topic named **test_topic**  
```  
    $ bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic test_topic  
```  

On a new terminal, run producer in which you can type a message

``` 
    $ cd kafka_2.12-0.10.2.0
    $ ./bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test_topic  
```

On a new terminal, run consumer in whch you receive messages  

```
    $ cd kafka_2.12-0.10.2.0
    $ ./bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test_topic --from-beginning
```

Kafka Client Examples  
=====================  

## For Python  

```
    $ source activate kafka  
    $(kafka) python example_producer_kafka.py localhost:9092 test_topic  
```

## For C++, 

First, librdkafka needs to be installed. Please make sure not to install the library by using "sudo apt-get install"  

```  
    $ pwd   
    your_path/kafka_setup_and_examples/  

    $ cd librdkafka   
    $ ./configure  
    $ make  
    $ sudo make install  
```

Then install cppkafka. Please install boost if you don't have.  

```  
    $ pwd
    your_path/kafka_setup_and_examples/
    
    $ cd cppkafka  
    $ mkdir build  
    $ cd build  
    $ cmake ..  
    $ make   
    $ sudo make install  
```

Put the followings in ./kafka_setup_and_examples/cppkafka/examples/CMakeLists.txt 

    cmake_minimum_required(VERSION 3.9)
    FIND_PACKAGE(Boost COMPONENTS program_options REQUIRED)
    INCLUDE_DIRECTORIES(${Boost_INCLUDE_DIRS})

    set(CMAKE_CXX_FLAGS "-std=c++11 -Wall")
    SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-rpath -Wl,/usr/local/lib")

Then build

```  
    $ pwd
    your_path/kafka_setup_and_examples/
    
    $ cd cppkafka/examples/
    $ mkdir build
    $ cd build
    $ cmake ..
    $ make producer 
    $ ./producer -b localhost:9092 -t test_topic

```  

## For JavaScript (NodeJS)

Please make sure that NodeJS is already installed. 

```  
    # Install required modules  
    $ npm install kafka-node optimist  
```  

```
    # Run cosumer  
    $ node consumer_nodejs.js  

    # Run producer  
    $ node producer_nodejs.js  
```  

Reference  
=========  
- [Kafka Visualization Tool](http://www.kafkatool.com/features.html)  
- [librdkafka](https://github.com/edenhill/librdkafka)  
- [cppkafka](https://github.com/mfontanini/cppkafka)  
- [How to add path to LD_LIBRARY](https://stackoverflow.com/questions/480764/linux-error-while-loading-shared-libraries-cannot-open-shared-object-file-no-s)  
- [How to fix CMake Library Path problem](https://stackoverflow.com/questions/30380257/how-can-ld-library-path-be-changed-within-cmake)  