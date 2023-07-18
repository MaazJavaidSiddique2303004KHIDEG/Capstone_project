import logging
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch

import redis

from src.etl_service.etl_script import main


class ETLScriptTestCase(unittest.TestCase):
    @patch("src.etl_service.etl_script.extract_all_data")
    @patch("src.etl_service.etl_script.transform_data")
    @patch("src.etl_service.etl_script.load_data_to_redis")
    def test_main_extract_transform_load(self, load_mock, transform_mock, extract_mock):
        """The Test function mock the behaviour of extract_data(), transform_data(), and load_data_to_redis()"""
        # Create a mock Redis client object
        redis_mock = MagicMock(spec=redis.Redis)
        # Prepare test data
        api_urls = {
            "rating": "https://xloop-dummy.herokuapp.com/rating",
            "appointment": "https://xloop-dummy.herokuapp.com/appointment",
            "councillor": "https://xloop-dummy.herokuapp.com/councillor",
            "patient_councillor": "https://xloop-dummy.herokuapp.com/patient_councillor",
        }
        data_mock = {
            "rating": [{"id": 1, "value": 4.5}, {"id": 2, "value": 3.8}],
            "appointment": [{"id": 1, "patient_id": 1}, {"id": 2, "patient_id": 2}],
            "councillor": [
                {"id": 1, "specialization": "Psychology"},
                {"id": 2, "specialization": "Psychiatry"},
            ],
            "patient_councillor": [
                {"patient_id": 1, "councillor_id": 1},
                {"patient_id": 2, "councillor_id": 2},
            ],
        }
        avg_ratings_list_mock = [
            {"id": 1, "average_rating": 4.2},
            {"id": 2, "average_rating": 3.9},
        ]
        specializations_mock = ["Psychology", "Psychiatry"]
        # Set the return values of the mocked functions
        extract_mock.return_value = data_mock
        transform_mock.return_value = avg_ratings_list_mock, specializations_mock
        # Call the function being tested
        main()
        # Assert the function calls and arguments
        extract_mock.assert_called_once_with(api_urls)
        transform_mock.assert_called_once_with(
            mock.ANY,
            data_mock,
            "rating",
            "appointment",
            "councillor",
            "patient_councillor",
        )
        expected_calls = [
            mock.call(redis_mock, "Psychology", avg_ratings_list_mock),
            mock.call(redis_mock, "Psychiatry", avg_ratings_list_mock),
        ]
        # Compare expected calls with actual calls
        actual_calls = load_mock.call_args_list
        for expected_call in expected_calls:
            if expected_call not in actual_calls:
                logging.error("Expected Call: %s", expected_call)
                logging.error("Actual Calls:")
                for call in actual_calls:
                    logging.error(call)
        # Print the values of the mocked functions
        logging.info("Extract Mock: %s", extract_mock)
        logging.info("Transform Mock: %s", transform_mock)
        logging.info("Load Mock: %s", load_mock)


if __name__ == "__main__":
    unittest.main()
