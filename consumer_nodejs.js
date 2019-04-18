const kafka = require('kafka-node');
let kafkaHost = '10.10.10.145:9092';

const Consumer = kafka.Consumer;
const client = new kafka.KafkaClient({kafkaHost: kafkaHost});

const consumer = new Consumer(
    client,
    [
        { topic: 'test_topic' },
    ],
    {
        autoCommit: false,
        fromOffset: 'latest'
    }
);

consumer.on('message', function (message) {
    console.log(message);
});

consumer.on('error', function (err) {
    console.log('Error:',err);
});

consumer.on('offsetOutOfRange', function (err) {
    console.log('offsetOutOfRange:',err);
});