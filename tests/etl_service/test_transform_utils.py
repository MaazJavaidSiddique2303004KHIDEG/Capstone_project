from typing import Dict

import pytest
from pyspark.sql import SparkSession
from pytest import LogCaptureFixture

from src.etl_service.extract_utils import extract_all_data
from src.etl_service.transform_utils import transform_data


# Fixture for SparkSession
@pytest.fixture
def spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()


def test_transform_data_types(spark: SparkSession) -> None:
    """Test data transformation types."""

    api_urls = {
        "rating": "https://xloop-dummy.herokuapp.com/rating",
        "appointment": "https://xloop-dummy.herokuapp.com/appointment",
        "councillor": "https://xloop-dummy.herokuapp.com/councillor",
        "patient_councillor": "https://xloop-dummy.herokuapp.com/patient_councillor",
    }
    # Prepare test data
    data = extract_all_data(api_urls)

    rating_key = "rating"
    appointment_key = "appointment"
    councillor_key = "councillor"
    patient_councillor_key = "patient_councillor"

    # Call the function being tested
    avg_ratings_list, specializations = transform_data(
        spark, data, rating_key, appointment_key, councillor_key, patient_councillor_key
    )

    assert isinstance(avg_ratings_list[0]["id"], int)
    assert isinstance(avg_ratings_list[0]["specialization"], str)
    assert isinstance(avg_ratings_list[0]["average_rating"], float)


def test_transform_data_average_ratings(spark: SparkSession) -> None:
    """Test data transformation for average ratings."""

    # Prepare test data
    data = {
        "rating": [
            {"appointment_id": 1, "value": 4.5},
            {"appointment_id": 2, "value": 3.8},
        ],
        "appointment": [{"id": 1, "patient_id": 1}, {"id": 2, "patient_id": 2}],
        "councillor": [
            {"id": 1, "specialization": "Psychology"},
            {"id": 2, "specialization": "Therapy"},
        ],
        "patient_councillor": [
            {"patient_id": 1, "councillor_id": 1},
            {"patient_id": 2, "councillor_id": 2},
        ],
    }
    rating_key = "rating"
    appointment_key = "appointment"
    councillor_key = "councillor"
    patient_councillor_key = "patient_councillor"

    # Call the function being tested
    avg_ratings, _ = transform_data(
        spark, data, rating_key, appointment_key, councillor_key, patient_councillor_key
    )

    # Assert the result
    expected_avg_ratings = [(1, "Psychology", 4.5), (2, "Therapy", 3.8)]
    assert sorted(avg_ratings) == sorted(expected_avg_ratings)


def test_transform_data_distinct_specializations(spark: SparkSession) -> None:
    """Test extraction of distinct specializations."""

    # Prepare test data
    data = {
        "rating": [
            {"appointment_id": 1, "value": 4.5},
            {"appointment_id": 2, "value": 3.8},
        ],
        "appointment": [{"id": 1, "patient_id": 1}, {"id": 2, "patient_id": 2}],
        "councillor": [
            {"id": 1, "specialization": "Psychology"},
            {"id": 2, "specialization": "Therapy"},
        ],
        "patient_councillor": [
            {"patient_id": 1, "councillor_id": 1},
            {"patient_id": 2, "councillor_id": 2},
        ],
    }
    rating_key = "rating"
    appointment_key = "appointment"
    councillor_key = "councillor"
    patient_councillor_key = "patient_councillor"

    # Call the function being tested
    _, specializations = transform_data(
        spark, data, rating_key, appointment_key, councillor_key, patient_councillor_key
    )

    # Assert the result
    expected_specializations = ["Psychology", "Therapy"]
    assert sorted(specializations) == sorted(expected_specializations)


def test_transform_data_duplicate_specializations(spark: SparkSession) -> None:
    """Test handling of duplicate specializations."""

    # Prepare test data with duplicate specializations for councillors
    data = {
        "rating": [
            {"appointment_id": 1, "value": 4.5},
            {"appointment_id": 2, "value": 3.8},
        ],
        "appointment": [{"id": 1, "patient_id": 1}, {"id": 2, "patient_id": 2}],
        "councillor": [
            {"id": 1, "specialization": "Psychology"},
            {"id": 2, "specialization": "Therapy"},
            {"id": 3, "specialization": "Psychology"},
        ],  # Duplicate specialization for councillors 1 and 3
        "patient_councillor": [
            {"patient_id": 1, "councillor_id": 1},
            {"patient_id": 2, "councillor_id": 2},
        ],
    }
    rating_key = "rating"
    appointment_key = "appointment"
    councillor_key = "councillor"
    patient_councillor_key = "patient_councillor"

    # Call the function being tested
    avg_ratings, specializations = transform_data(
        spark, data, rating_key, appointment_key, councillor_key, patient_councillor_key
    )

    # Assert the result
    expected_avg_ratings = [(1, "Psychology", 4.5), (2, "Therapy", 3.8)]
    assert avg_ratings == expected_avg_ratings
    expected_specializations = ["Psychology", "Therapy"]
    assert sorted(specializations) == sorted(expected_specializations)


def test_transform_data_large_dataset(spark: SparkSession) -> None:
    """Test transformation with a large dataset."""

    # Prepare a large dataset with multiple appointments and councillors
    data = {
        "rating": [
            {"appointment_id": i, "value": i % 5 + 1} for i in range(1, 1001)
        ],  # Ratings from 1 to 5 cyclically
        "appointment": [
            {"id": i, "patient_id": i % 100 + 1} for i in range(1, 1001)
        ],  # 100 patients
        "councillor": [
            {"id": i, "specialization": f"Specialization{i % 10 + 1}"}
            for i in range(1, 101)
        ],  # 10 specializations
        "patient_councillor": [
            {"patient_id": i % 100 + 1, "councillor_id": i % 100 + 1}
            for i in range(1, 1001)
        ],  # 100 patients
    }
    rating_key = "rating"
    appointment_key = "appointment"
    councillor_key = "councillor"
    patient_councillor_key = "patient_councillor"

    # Call the function being tested
    avg_ratings, specializations = transform_data(
        spark, data, rating_key, appointment_key, councillor_key, patient_councillor_key
    )

    # Assert the result
    assert len(avg_ratings) == 100  # 100 councillors
    assert len(specializations) == 10  # 10 specializations
    assert all(
        isinstance(record[0], int)
        and isinstance(record[1], str)
        and isinstance(record[2], float)
        for record in avg_ratings
    )


def test_transform_data_no_data(spark: SparkSession) -> None:
    """Test transformation with no data."""

    # Prepare test data with no data provided
    data: Dict[str, str] = {}
    rating_key = "rating"
    appointment_key = "appointment"
    councillor_key = "councillor"
    patient_councillor_key = "patient_councillor"

    # Call the function being tested and assert the exception
    with pytest.raises(ValueError) as error:
        transform_data(
            spark,
            data,
            rating_key,
            appointment_key,
            councillor_key,
            patient_councillor_key,
        )
    assert str(error.value) == "Missing or empty data for field: rating"


def test_transform_data_missing_fields(spark: SparkSession) -> None:
    """Test handling of missing fields in data."""

    # Prepare test data with missing fields in the data dictionary
    data = {
        "rating": [
            {"appointment_id": 1, "value": 4.5},
            {"appointment_id": 2, "value": 3.8},
        ],
        "appointment": [{"id": 1, "patient_id": 1}, {"id": 2, "patient_id": 2}],
        "councillor": [
            {"id": 1, "specialization": "Psychology"},
            {"id": 2, "specialization": "Therapy"},
        ],
        # Missing patient_councillor field
    }
    rating_key = "rating"
    appointment_key = "appointment"
    councillor_key = "councillor"
    patient_councillor_key = "patient_councillor"

    # Call the function being tested and assert the exception
    with pytest.raises(ValueError) as error:
        transform_data(
            spark,
            data,
            rating_key,
            appointment_key,
            councillor_key,
            patient_councillor_key,
        )
    assert str(error.value) == "Missing or empty data for field: patient_councillor"


def test_transform_data_specializations_with_spaces(spark: SparkSession) -> None:
    """Test handling of Specilization with spaces."""

    # Prepare test data with specializations containing leading/trailing spaces
    data = {
        "rating": [
            {"appointment_id": 1, "value": 4.5},
            {"appointment_id": 2, "value": 3.8},
        ],
        "appointment": [{"id": 1, "patient_id": 1}, {"id": 2, "patient_id": 2}],
        "councillor": [
            {"id": 1, "specialization": " Psychology"},
            {"id": 2, "specialization": "Therapy "},
        ],
        "patient_councillor": [
            {"patient_id": 1, "councillor_id": 1},
            {"patient_id": 2, "councillor_id": 2},
        ],
    }
    rating_key = "rating"
    appointment_key = "appointment"
    councillor_key = "councillor"
    patient_councillor_key = "patient_councillor"

    # Call the function being tested
    avg_ratings, specializations = transform_data(
        spark, data, rating_key, appointment_key, councillor_key, patient_councillor_key
    )

    # Assert the result
    expected_avg_ratings = [(1, " Psychology", 4.5), (2, "Therapy ", 3.8)]
    assert avg_ratings == expected_avg_ratings
    expected_specializations = ["Therapy ", " Psychology"]
    assert specializations == expected_specializations


# Tests that the function works with valid input data
def test_valid_input_data(spark: SparkSession) -> None:
    """Test handling of valid fields in data."""

    data = {
        "rating": [{"id": 1, "appointment_id": 1, "value": 4}],
        "appointment": [{"id": 1, "patient_id": 1, "councillor_id": 1}],
        "councillor": [{"id": 1, "name": "John Doe", "specialization": "Psychology"}],
        "patient_councillor": [{"patient_id": 1, "councillor_id": 1}],
    }
    result = transform_data(
        spark, data, "rating", "appointment", "councillor", "patient_councillor"
    )
    assert len(result[0]) == 1
    assert len(result[1]) == 1
    assert result[0][0]["id"] == 1
    assert result[0][0]["specialization"] == "Psychology"
    assert result[0][0]["average_rating"] == 4.0
    assert result[1][0] == "Psychology"


# Tests that the function works with different input data
def test_different_input_data(spark: SparkSession) -> None:
    """Test handling of different fields in data."""

    data = {
        "rating": [
            {"id": 1, "appointment_id": 1, "value": 4},
            {"id": 2, "appointment_id": 2, "value": 3},
        ],
        "appointment": [
            {"id": 1, "patient_id": 1, "councillor_id": 1},
            {"id": 2, "patient_id": 2, "councillor_id": 2},
        ],
        "councillor": [
            {"id": 1, "name": "John Doe", "specialization": "Psychology"},
            {"id": 2, "name": "Jane Doe", "specialization": "Psychiatry"},
        ],
        "patient_councillor": [
            {"patient_id": 1, "councillor_id": 1},
            {"patient_id": 2, "councillor_id": 2},
        ],
    }
    result = transform_data(
        spark, data, "rating", "appointment", "councillor", "patient_councillor"
    )
    assert len(result[0]) == 2
    assert len(result[1]) == 2
    assert result[0][0]["id"] == 1
    assert result[0][0]["specialization"] == "Psychology"
    assert result[0][0]["average_rating"] == 4.0
    assert result[0][1]["id"] == 2
    assert result[0][1]["specialization"] == "Psychiatry"
    assert result[0][1]["average_rating"] == 3.0
    assert result[1][0] == "Psychiatry"
    assert result[1][1] == "Psychology"


# Tests that the function returns a tuple
def test_returns_tuple(spark: SparkSession) -> None:
    """Test handling of return datatype."""

    data = {
        "rating": [{"appointment_id": 1, "value": 4.5}],
        "appointment": [{"id": 1, "patient_id": 1}],
        "councillor": [{"id": 1, "specialization": "Psychology"}],
        "patient_councillor": [{"patient_id": 1, "councillor_id": 1}],
    }
    result = transform_data(
        spark, data, "rating", "appointment", "councillor", "patient_councillor"
    )
    assert isinstance(result, tuple)


# Tests that the function logs the expected messages
def test_logs_expected_messages(spark: SparkSession, caplog: LogCaptureFixture) -> None:
    """Test Expected logs messages in data."""

    data = {
        "rating": [{"id": 1, "appointment_id": 1, "value": 4}],
        "appointment": [{"id": 1, "patient_id": 1, "councillor_id": 1}],
        "councillor": [{"id": 1, "name": "John Doe", "specialization": "Psychology"}],
        "patient_councillor": [{"patient_id": 1, "councillor_id": 1}],
    }
    transform_data(
        spark, data, "rating", "appointment", "councillor", "patient_councillor"
    )
    assert "Reading appointment data." in caplog.text
    assert "Reading councillor data." in caplog.text
    assert "Reading patient-councillor data." in caplog.text
    assert "Performing joins on the dataframes." in caplog.text
    assert "Calculating average ratings." in caplog.text
    assert "Extracting distinct specializations." in caplog.text


# Tests that the function handles null values in input data
def test_null_values_in_input_data(spark: SparkSession) -> None:
    """Test handling of Null fields in data."""

    with pytest.raises(ValueError):
        transform_data(
            spark,
            {
                "rating": None,
                "appointment": None,
                "councillor": None,
                "patient_councillor": None,
            },
            "rating",
            "appointment",
            "councillor",
            "patient_councillor",
        )


def test_datatype_mismatch(spark: SparkSession) -> None:
    """Test handling of datatype Mismatch."""

    data = {
        "rating": 123,
        "appointment": "invalid",
        "councillor": {},
        "patient_councillor": [],
    }
    with pytest.raises(ValueError):
        transform_data(
            spark=SparkSession.builder.appName("test").getOrCreate(),
            data=data,
            rating_key="rating",
            appointment_key="appointment",
            councillor_key="councillor",
            patient_councillor_key="patient_councillor",
        )
