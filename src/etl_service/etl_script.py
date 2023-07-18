import logging

from decouple import config

from src.etl_service.extract_utils import extract_all_data
from src.etl_service.load_utils import load_data_to_redis
from src.etl_service.logging_config import configure_logging
from src.etl_service.redis_connector import get_redis_client
from src.etl_service.spark_session import create_spark_session
from src.etl_service.transform_utils import transform_data


def main() -> None:
    # Configure logging
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Define the base URL
    url = "https://xloop-dummy.herokuapp.com"

    # Create a SparkSession
    spark = create_spark_session("Capstone_Project")

    # Connect to Redis
    redis_host = config("REDIS_HOST")
    redis_port = config("REDIS_PORT")
    redis_client = get_redis_client(redis_host, redis_port)

    # Define the API URLs dictionary directly and use the keys as arguments for transform_data
    api_urls = {
        "rating": f"{url}/rating",
        "appointment": f"{url}/appointment",
        "councillor": f"{url}/councillor",
        "patient_councillor": f"{url}/patient_councillor",
    }

    # Call the extract_all_data function and pass the API URLs dictionary as input
    logger.info("Extracting data from APIs...")
    data = extract_all_data(api_urls)

    # Call the transform_data function to calculate average ratings and extract specializations
    logger.info("Transforming data...")
    avg_ratings_list, specializations = transform_data(
        spark, data, "rating", "appointment", "councillor", "patient_councillor"
    )

    for specialization in specializations:
        logger.info(f"Loading data for specialization: {specialization}")
        load_data_to_redis(redis_client, specialization, avg_ratings_list)

    # Stop the SparkSession
    spark.stop()


if __name__ == "__main__":
    main()
