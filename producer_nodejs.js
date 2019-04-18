'use strict';

const kafka = require('kafka-node');
let kafkaHost = '10.10.10.145:9092';

var Producer = kafka.Producer;
var KeyedMessage = kafka.KeyedMessage;

const client = new kafka.KafkaClient({kafkaHost: kafkaHost});
var argv = require('optimist').argv;
var topic = argv.topic || 'test_topic';
var p = argv.p || 0;
var a = argv.a || 0;
var producer = new Producer(client, { requireAcks: 1 });

producer.on('ready', function () {
  var message = 'a message';
  var keyedMessage = new KeyedMessage('keyed', 'a keyed message');

  producer.send([{ topic: topic, partition: p, messages: [message, keyedMessage], attributes: a }], function (
    err,
    result
  ) {
    console.log(err || result);
    process.exit();
  });
});

producer.on('error', function (err) {
  console.log('error', err);
});