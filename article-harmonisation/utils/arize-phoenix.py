import time

import pandas as pd
import phoenix as px
from phoenix.experiments.types import Dataset

from .paths import get_root_dir

ROOT_DIR = get_root_dir()


def upload_parquet(
    dataset_name: str,
    input_keys: list[str],
    output_keys: list[str],
    parquet_filepath: str = f"{ROOT_DIR}/article-harmonisation/data/merged_data.parquet",
    upload_url: str = "http://127.0.0.1:6006",
) -> Dataset:
    """
    Uploads a dataset from a parquet file to a specified URL.

    This function reads data from a parquet file, uploads it to a remote service
    using the provided URL, and returns the uploaded dataset.

    Args:
        dataset_name (str): The name of the dataset to be uploaded.
        input_keys (list[str]): A list of input keys that identify the input columns in the dataset.
        output_keys (list[str]): A list of output keys that identify the output columns in the dataset.
        parquet_filepath (str, optional): The file path to the parquet file to be uploaded.
            Defaults to "{ROOT_DIR}/article-harmonisation/data/merged_data.parquet".
        upload_url (str, optional): The URL of the remote service to upload the dataset to.
            Defaults to "http://127.0.0.1:6006".

    Returns:
        Dataset: The uploaded dataset object returned by the client.

    Example:
        dataset = upload_parquet(
            dataset_name="my_dataset",
            input_keys=["input1", "input2"],
            output_keys=["output1"],
            parquet_filepath="/path/to/my_data.parquet",
            upload_url="http://127.0.0.1:6006"
        )
    """
    client = px.Client(endpoint=upload_url)

    df = pd.read_parquet(parquet_filepath)

    dataset = client.upload_dataset(
        dataframe=df,
        dataset_name=dataset_name,
        input_keys=input_keys,
        output_keys=output_keys,
    )

    return dataset


if __name__ == "__main__":
    timestr = time.strftime("%Y%m%d-%H%M%S")
    print(
        upload_parquet(
            f"test1234-{timestr}",
            input_keys=["content_body", "content_category"],
            output_keys=["extracted_content_body"],
        )
    )
