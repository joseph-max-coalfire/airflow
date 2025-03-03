#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

import unittest
import uuid

from moto import mock_dynamodb

from airflow.providers.amazon.aws.hooks.dynamodb import DynamoDBHook


class TestDynamoDBHook(unittest.TestCase):
    @mock_dynamodb
    def test_get_conn_returns_a_boto3_connection(self):
        hook = DynamoDBHook(aws_conn_id='aws_default')
        assert hook.get_conn() is not None

    @mock_dynamodb
    def test_insert_batch_items_dynamodb_table(self):

        hook = DynamoDBHook(
            aws_conn_id='aws_default', table_name='test_airflow', table_keys=['id'], region_name='us-east-1'
        )

        # this table needs to be created in production
        table = hook.get_conn().create_table(
            TableName='test_airflow',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'},
            ],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10},
        )

        table = hook.get_conn().Table('test_airflow')

        items = [{'id': str(uuid.uuid4()), 'name': 'airflow'} for _ in range(10)]

        hook.write_batch_data(items)

        table.meta.client.get_waiter('table_exists').wait(TableName='test_airflow')
        assert table.item_count == 10
