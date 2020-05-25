#!/bin/bash

set -x
set -e

echo 'loopback_users = none' >> /etc/rabbitmq/rabbitmq.conf
rabbitmq-server &
rabbitmqctl wait --pid $!
rabbitmqadmin import /etc/definitions.json
wait
