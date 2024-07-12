import os
from pathlib import PurePosixPath
from typing import Any

import fsspec
import numpy as np
import plotly.graph_objects as go
from kedro.io import AbstractVersionedDataset
from kedro.io.core import Version, get_filepath_str, get_protocol_and_path


class HTMLDataset(AbstractVersionedDataset[np.ndarray, np.ndarray]):
    def __init__(
        self,
        filepath: str,
        save_args: dict[str, Any] = {},
        version: Version | None = None,
    ):
        """
        A constructor method for initializing the HTMLDataset object.

        Parameters:
            filepath (str): The path to the file.
            save_args (dict[str, Any], optional): Arguments to save the file. Defaults to {}.
            version (Version | None, optional): The version of the dataset. Defaults to None.
        """
        # parse the path and protocol (e.g. file, http, s3, etc.)
        protocol, path = get_protocol_and_path(filepath)
        self._protocol = protocol
        self._fs = fsspec.filesystem(self._protocol, **save_args)

        super().__init__(
            filepath=PurePosixPath(path),
            version=version,
            exists_function=self._fs.exists,
            glob_function=self._fs.glob,
        )

    def _load(self) -> None:
        pass

    def _save(self, fig: go.Figure) -> None:
        """
        Saves the given plotly Figure object as an HTML file using the specified path.

        Args:
            fig (go.Figure): The plotly Figure object to save as HTML.

        Returns:
            None
        """
        # Using get_filepath_str ensures that the protocol and path are appended correctly for different filesystems
        save_path = get_filepath_str(self._get_save_path(), self._protocol)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.write_html(save_path)

    def _describe(self) -> dict[str, Any]:
        """Returns a dict that describes the attributes of the dataset."""
        return dict(
            filepath=self._filepath, version=self._version, protocol=self._protocol
        )
