FROM python:3

LABEL org.opencontainers.image.source=https://github.com/delrey1/jmx-validator

WORKDIR /usr/src/app

ENV JMX_WILDCARD_LOCATION=/usr/src/app/scripts/*.jmx
# Assumption is that the bin folder is the parent location within jmeter.
#   and we assume that the structure is /jmeter/bin/data/*
ENV DATA_PARENT_LOCATION=/usr/src/app/

COPY app/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY app .

CMD [ "python", "-m", "pytest", "-v", "--log-cli-level=10"]
