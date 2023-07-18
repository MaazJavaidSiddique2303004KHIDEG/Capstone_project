from typing import List
from unittest import mock
from unittest.mock import Mock, call

import pytest
import redis  # type:ignore

from src.etl_service.load_utils import load_data_to_redis


@pytest.fixture
def redis_client() -> Mock:
    # Create a mock Redis client object
    return mock.Mock(spec=redis.Redis)


def test_load_data_to_redis_empty_specialization(redis_client: Mock) -> None:
    """Test the load_data_to_redis function."""
    # Prepare invalid input data
    specialization = ""
    avg_ratings_list = [
        {"id": 1, "average_rating": 4.5},
        {"id": 2, "average_rating": 3.8},
        {"id": 3, "average_rating": 4.2},
    ]
    # Call the function and assert the raised exception
    with pytest.raises(ValueError, match="specialization cannot be an empty string."):
        load_data_to_redis(redis_client, specialization, avg_ratings_list)


def test_load_data_to_redis_empty_avg_ratings_list(redis_client: Mock) -> None:
    """
    Test the load_data_to_redis function.
    """
    # Prepare invalid input data
    specialization = "Specialization"
    avg_ratings_list: List[str] = []
    # Call the function and assert the raised exception
    with pytest.raises(ValueError, match="avg_ratings_list cannot be empty."):
        load_data_to_redis(redis_client, specialization, avg_ratings_list)


# Tests the successful loading of a single dictionary.
def test_single_dict_load_data_to_redis(redis_client: Mock) -> None:
    # Mock Redis client
    redis_client.set.return_value = True
    specialization = "test"
    avg_ratings_list = [{"id": 1, "specialization": "test", "average_rating": 4.5}]
    # Call function under test
    result = load_data_to_redis(redis_client, specialization, avg_ratings_list)
    # Assert that the function returned True
    assert result
    # Assert that set was called with the correct arguments
    redis_client.set.assert_called_once_with(
        "specialization:test",
        '[{"id": 1, "specialization": "test", "average_rating": 4.5}]',
    )


# Tests with avg_ratings_list containing multiple dictionaries
def test_multiple_dict_avg_ratings_list(redis_client: Mock) -> None:
    # Mock Redis client
    redis_client.set.return_value = True
    specialization = "test"
    avg_ratings_list = [
        {"id": 1, "specialization": specialization, "average_rating": 4.5},
        {"id": 2, "specialization": specialization, "average_rating": 3.2},
    ]
    # Call function under test
    result = load_data_to_redis(redis_client, specialization, avg_ratings_list)
    # Assert that the function returned True
    assert result
    # Assert that set was called with the correct arguments for each dictionary
    expected_calls = [
        call(
            "specialization:test",
            """[{"id": 1, "specialization": "test", "average_rating": 4.5},
              {"id": 2, "specialization": "test", "average_rating": 3.2}]""",
        ),
    ]
    redis_client.set.assert_has_calls(expected_calls)


# Tests with empty avg_ratings_list
def test_empty_avg_ratings_list(redis_client: Mock) -> None:
    specialization = "test"
    avg_ratings_list: List[str] = []
    with pytest.raises(ValueError):
        load_data_to_redis(redis_client, specialization, avg_ratings_list)


# Tests with invalid redis client
def test_invalid_redis_client(redis_client: Mock) -> None:
    redis_client = "invalid"
    specialization = "test"
    avg_ratings_list = [
        {"id": 1, "average_rating": 4.5},
        {"id": 2, "average_rating": 3.2},
    ]
    with pytest.raises(TypeError):
        load_data_to_redis(redis_client, specialization, avg_ratings_list)


# Tests that the Redis key is set correctly and data is loaded successfully into Redis.
def test_redis_key_set_correctly(redis_client: Mock) -> None:
    # Mock Redis client
    redis_client.set.return_value = 1
    redis_client.exists.return_value = True
    specialization = "test"
    avg_ratings_list = [
        {
            "id": 1,
            "specialization": specialization,
            "average_rating": 4.5,
        },  # Add "specialization" key
        {
            "id": 2,
            "specialization": specialization,
            "average_rating": 3.2,
        },  # Add "specialization" key
    ]
    # Call function under test
    result = load_data_to_redis(redis_client, specialization, avg_ratings_list)
    # Assert that the function returned True
    assert result == redis_client.set.return_value
    # Assert that hset was called with the correct arguments for each dictionary
    expected_calls = [
        call(
            "specialization:test",
            """[{"id": 1, "specialization": "test", "average_rating": 4.5},
            {"id": 2, "specialization": "test", "average_rating": 3.2}]""",
        ),
    ]
    redis_client.set.assert_has_calls(expected_calls)
    # Call exists
    redis_client.exists("specialization:test_specialization")
    # Assert that exists was called with the correct key
    redis_client.exists.assert_called_with("specialization:test_specialization")


# Tests if data is loaded successfully
def test_data_loaded_successfully(redis_client: Mock) -> None:
    specialization = "test"
    avg_ratings_list = [
        {"id": 1, "specialization": specialization, "average_rating": 4.5},
        {"id": 2, "specialization": specialization, "average_rating": 3.2},
    ]
    load_data_to_redis(redis_client, specialization, avg_ratings_list)
    assert redis_client.set.call_args_list == [
        call(
            "specialization:test",
            """[{"id": 1, "specialization": "test", "average_rating": 4.5},
              {"id": 2, "specialization": "test", "average_rating": 3.2}]""",
        ),
    ]


# Tests if Redis hash is updated correctly
def test_redis_hash_updated_correctly(redis_client: Mock) -> None:
    specialization = "test_specialization"
    avg_ratings_list = [
        {"id": "1", "specialization": specialization, "average_rating": 4.5},
        {"id": "2", "specialization": specialization, "average_rating": 3.2},
    ]
    redis_client.hset.return_value = True
    redis_client.hget.return_value = b"4.5"
    load_data_to_redis(redis_client, specialization, avg_ratings_list)
    redis_client.hget(f"specialization:{specialization}", "1")
    assert redis_client.hget.called
    assert redis_client.hget.call_args == call(f"specialization:{specialization}", "1")
    assert redis_client.hget.return_value == b"4.5"


# Test with valid redis client, specialization and avg_ratings_list
def test_valid_redis_client(redis_client: Mock) -> None:
    specialization = "Python"
    avg_ratings_list = [
        {"id": 1, "specialization": specialization, "average_rating": 4.5},
        {"id": 2, "specialization": specialization, "average_rating": 3.2},
    ]
    redis_client.set.return_value = True
    assert load_data_to_redis(redis_client, specialization, avg_ratings_list)
    expected_calls = [
        call(
            f"specialization:{specialization}",
            """[{"id": 1, "specialization": "Python", "average_rating": 4.5},
            {"id": 2, "specialization": "Python", "average_rating": 3.2}]""",
        ),
    ]
    redis_client.set.assert_has_calls(expected_calls)


# Tests if function returns boolean value
def test_return_value(redis_client: Mock) -> None:
    specialization = "test"
    avg_ratings_list = [
        {"id": 1, "specialization": "test", "average_rating": 4.5},
        {"id": 2, "specialization": "test", "average_rating": 3.2},
    ]
    # Mock Redis client
    redis_client.set.return_value = True
    result = load_data_to_redis(redis_client, specialization, avg_ratings_list)
    assert isinstance(result, bool)
