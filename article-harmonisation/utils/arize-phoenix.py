import requests
import pandas as pd
import phoenix as px


def upload_parquet(dataset_name: str, parquet_filepath: str = "../data/merged_data.parquet", upload_url: str = "http://127.0.0.1:6006"):
    client = px.Client(endpoint=upload_url)

    df = pd.read_parquet(parquet_filepath)

    dataset = client.upload_dataset(
        dataframe=df,
        dataset_name=dataset_name,
        input_keys=["content_body"],
        output_keys=["extracted_content_body"],
    )

    return dataset


if __name__ == "__main__":
    # parquet_filepath = sys.argv[1]
    # upload_url = sys.argv[2]
    # print(upload_dataset(upload_url, parquet_filepath))
    print(upload_parquet("test123"))
