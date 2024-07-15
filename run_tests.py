import argparse
import os
import sys
from argparse import Namespace

import pandas as pd
import pytest


def parse_arguments() -> Namespace:
    """
    A function that parses arguments for running pytest with specific options.

    Returns:
        Namespace: The parsed arguments as a Namespace object.
    """
    parser = argparse.ArgumentParser(description="run pytest with specified options")
    parser.add_argument(
        "-f", "--files", type=str, help="specific test files to run", nargs="*"
    )
    parser.add_argument(
        "-k", "--functions", type=str, help="specific test functions to run", nargs="*"
    )
    return parser.parse_args()


def run_tests(args: Namespace) -> int:
    """
    A function that runs tests with specified options using pytest.

    Parameters:
        args (Namespace): The namespace object containing parsed arguments.

    Returns:
        int: The exit status of the pytest execution.
    """
    # Disable SettingWithCopyWarning
    pd.options.mode.chained_assignment = None

    os.chdir("content-optimization")

    # Default pytest arguments
    pytest_args = ["-v"]

    # Add specific files if provided
    if args.files:
        pytest_args.extend(args.files)

    # Add specific functions if provided
    if args.functions:
        pytest_args.extend(["-k", " or ".join(args.functions)])

    print(pytest_args)

    return pytest.main(pytest_args)


def main():
    """
    The main function that serves as the entry point. It parses command line arguments,
    runs tests with the specified options, and exits the program. It expects the following
    arguments:

    - --files:
        A list of file paths to run pytest on.
    - --functions:
        A list of test function names to run pytest on.

    Example usage:
        python run_tests.py --files tests/pipelines/data_processing/test_pipeline.py \
            tests/pipelines/data_processing/test_nodes.py

        python run_tests.py --functions test_data_processing_pipeline \
            test_project_path
    """
    args = parse_arguments()
    sys.exit(run_tests(args))


if __name__ == "__main__":
    main()
