# Super Simple Static JMeter JMX Validator

## Purpose

Super simple JMeter JMX validator to catch basic mistakes before execution in a pipeline.

Integrate this in your pipeline to catch basic mistakes that can prevent a remote execution.

Currently, this script catches the following:

* Request Response and Connect timeouts are set on the top Request Defaults (If Present)
* Confirms there are no absolute paths present (e.g. `C:\Users\...\data.csv` or `//a/b/data.csv`)
* Confirms fragments are correctly linked (Currently a basic check - Room to improve if needed)
* Duplicate configurations are not present (Designed for JMXs that have load profiles set as `User Defined Variables`
  elements)

## How to use

Designed to be run as part of a pipeline, if this is running from a shell executor
then run the following command

* `cd directory/containing/jmx/files`
* `docker run -v $(pwd):/usr/src/app/scripts/ delrey/jmx-validator:latest`

Alternatively run from the image and either place jmx files to validate in `/usr/src/app/scripts` or set the
environment variable `JMX_WILDCARD_LOCATION` appropriate for your volume. Then trigger pytest to run from 
`/usr/src/app`

**GitLab CI Example**

```
...
validate:
  stage: validate
  image: delrey/jmx-validator:latest
  script:
    # Moving scripts folder to scripts folder within the container
    - cp -r script/location /usr/src/app
    # Running pytest command from app dir. This then validates the JMX files
    - cd /usr/src/app && pytest
  # Only run this stage when there has been a change to the jmx files
  only:
    changes:
      - "**/*.jmx"
  allow_failure: true
  tags:
    - docker
...
```

## Support
For any issue or support questions, please create an issue and we'll get back to you.

If you wish to contribute, please raise a Pull Request.
