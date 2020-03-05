import contextlib
import os
import tempfile
from pathlib import Path
from typing import Any, ContextManager, Dict, List, Optional, Union

import pyarrow


def create_tempfile(prefix=None, suffix=None, dir=None) -> Path:
    fd, filename = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=dir)
    os.close(fd)
    return Path(filename)


@contextlib.contextmanager
def tempfile_context(prefix=None, suffix=None, dir=None) -> ContextManager[Path]:
    path = create_tempfile(prefix=prefix, suffix=suffix, dir=dir)
    try:
        yield path
    finally:
        with contextlib.suppress(FileNotFoundError):
            path.unlink()


@contextlib.contextmanager
def parquet_file(
    table: Union[Dict[str, List[Any]], pyarrow.Table], dir: Optional[Path] = None,
) -> ContextManager[Path]:
    """
    Yield a filename with `table` written to a Parquet file.
    """
    if isinstance(table, dict):
        table = pyarrow.table(table)

    with tempfile_context(dir=dir) as parquet_path:
        pyarrow.parquet.write_table(
            table,
            parquet_path,
            version="2.0",
            compression="SNAPPY",
            use_dictionary=[
                name.encode("utf-8")
                for name, column in zip(table.column_names, table.columns)
                if pyarrow.types.is_dictionary(column.type)
            ],
        )
        yield parquet_path


def assert_arrow_table_equals(actual: pyarrow.Table, expected: pyarrow.Table):
    assert actual.to_pydict() == expected.to_pydict()
