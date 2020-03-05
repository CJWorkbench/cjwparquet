# We run everything in a Dockerfile so we can pull arrow-tools binaries
FROM workbenchdata/parquet-tools:v2.0.1 as parquet-tools

FROM python:3.8.1-buster AS test

COPY --from=parquet-tools /usr/bin/parquet-to-arrow /usr/bin/parquet-to-arrow
COPY --from=parquet-tools /usr/bin/parquet-to-text-stream /usr/bin/parquet-to-text-stream

RUN pip install black pyflakes isort

# __init__.py is read by setup.py for __version__.
RUN mkdir -p /app/cjwparquet/ && echo "__version__ = '0.0.1'" > /app/cjwparquet/__init__.py
# README is read by setup.py
COPY setup.py README.md /app/
COPY cjwparquet/__init__.py /app/cjwparquet/
WORKDIR /app
RUN pip install .[tests]

COPY . /app/

RUN true \
      && pyflakes . \
      && black --check . \
      && isort --check-only --diff --recursive cjwparquet tests \
      && pytest --verbose
