import time

import pandas as pd
import phoenix as px


def upload_parquet(
    dataset_name: str,
    input_keys: list[str],
    output_keys: list[str],
    parquet_filepath: str = "../data/merged_data.parquet",
    upload_url: str = "http://127.0.0.1:6006",
):
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
