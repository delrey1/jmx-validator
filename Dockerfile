FROM python:3

WORKDIR /usr/src/app

ENV JMX_WILDCARD_LOCATION=/usr/src/app/scripts/*.jmx

COPY app/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY app .

CMD [ "python", "-m", "pytest", "-v", "--log-cli-level=10"]