import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.db.connection as connection


class DBConnectionConfigTests(unittest.TestCase):
    def setUp(self):
        connection._client = None
        connection._db = None

    @patch("app.db.connection.MongoClient")
    @patch("app.db.connection.mongomock.MongoClient")
    def test_get_db_uses_short_timeout_when_mongo_uri_is_present(self, mongomock_client, mongo_client):
        os.environ["MONGODB_URI"] = "mongodb+srv://example:test@cluster.example.mongodb.net/test?retryWrites=true&w=majority"
        os.environ["MONGODB_DB_NAME"] = "nexira_test"
        mongo_client.side_effect = Exception("simulated database outage")

        connection.get_db()

        mongo_client.assert_called_once_with(
            os.environ["MONGODB_URI"],
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
        )
        mongomock_client.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
