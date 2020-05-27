#!/bin/bash

set -xe

echo 'loopback_users = none' >> /etc/rabbitmq/rabbitmq.conf
rabbitmq-server &
rabbitmqctl wait --pid $!
rabbitmqadmin import /etc/definitions.json
wait
