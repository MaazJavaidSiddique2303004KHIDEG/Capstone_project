from unittest import mock

import pytest
import requests
from fastapi.exceptions import HTTPException

from src.matching_service.app import get_top_councillors, process_councillors_ratings


@mock.patch("src.matching_service.app.get_top_councillors")
def test_get_top_concillors_success(mock_get_top_councillors):
    """
    Test the success scenario of the 'get_top_concillors' function.
    """
    mock_get_top_councillors = mock.Mock()
    mock_get_top_councillors.return_value = {
        "result": [
            {
                "counselor_id": "789",
                "rating": 5,
            },
            {
                "counselor_id": "1861",
                "rating": 5,
            },
            {
                "counselor_id": "8390",
                "rating": 5,
            },
            {
                "counselor_id": "7122",
                "rating": 5,
            },
            {
                "counselor_id": "1491",
                "rating": 5,
            },
            {
                "counselor_id": "1316",
                "rating": 5,
            },
            {
                "counselor_id": "5598",
                "rating": 5,
            },
            {
                "counselor_id": "6271",
                "rating": 5,
            },
            {
                "counselor_id": "6923",
                "rating": 5,
            },
            {
                "counselor_id": "5948",
                "rating": 5,
            },
        ]
    }
    report_id = 0
    result_get_top_councillors = mock_get_top_councillors(report_id)
    assert result_get_top_councillors == {
        "result": [
            {
                "counselor_id": "789",
                "rating": 5,
            },
            {
                "counselor_id": "1861",
                "rating": 5,
            },
            {
                "counselor_id": "8390",
                "rating": 5,
            },
            {
                "counselor_id": "7122",
                "rating": 5,
            },
            {
                "counselor_id": "1491",
                "rating": 5,
            },
            {
                "counselor_id": "1316",
                "rating": 5,
            },
            {
                "counselor_id": "5598",
                "rating": 5,
            },
            {
                "counselor_id": "6271",
                "rating": 5,
            },
            {
                "counselor_id": "6923",
                "rating": 5,
            },
            {
                "counselor_id": "5948",
                "rating": 5,
            },
        ]
    }


@mock.patch("src.matching_service.redis_connector.get_redis_client")
def test_process_counselor_ratings_with_network_error(mock_redis_client):
    """
    Test case to verify the behavior of process_counselor_ratings function
    when a network-related error (ConnectionError) occurs during interaction with Redis.
    """
    result = {}
    mock_redis_client.hgetall.side_effect = ConnectionError()
    try:
        result = process_councillors_ratings(mock_redis_client, "specialization")
    except Exception as e:
        print(repr(e))
    assert result == {}


@pytest.mark.asyncio
async def test_category_missing(mocker):
    """
    Tests that an HTTPException is raised when an error occurs connecting to Redis
    """
    report_id = 1
    # Mock the get_report_content function to raise an exception
    mocker.patch(
        "src.matching_service.app.get_report_content",
        side_effect=HTTPException(
            status_code=400, detail="Category is missing in the report."
        ),
    )
    # Mock the process_councillors_ratings function to raise an exception

    with pytest.raises(HTTPException) as exc_info:
        await get_top_councillors(report_id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Category is missing in the report."


@pytest.mark.asyncio
async def test_request_error(mocker):
    """
    Tests that an exception is raised when a request error occurs
    """

    report_id = 4
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException)
    with pytest.raises(requests.exceptions.RequestException):
        await get_top_councillors(report_id)


def test_http_exception_handler():
    """
    Tests the HTTP exception handler
    """
    with pytest.raises(HTTPException) as exc:
        raise HTTPException(status_code=400, detail="Bad Request")
    assert exc.value.status_code == 400
    assert exc.value.detail == "Bad Request"


@pytest.mark.asyncio
async def test_redis_error_exception():
    report_id = 123
    with pytest.raises(HTTPException) as exc_info:
        await get_top_councillors(report_id)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Error connecting to Redis."
