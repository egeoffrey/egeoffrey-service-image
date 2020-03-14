### EGEOFFREY ###

### define base image
## the SDK version to bind to has to be passed by the builder so to select the right base image
ARG SDK_VERSION
ARG ARCHITECTURE
FROM egeoffrey/egeoffrey-sdk-raspbian:${SDK_VERSION}-${ARCHITECTURE}

### install module's dependencies
RUN apt-get update && apt-get install -y python-opencv && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade setuptools && pip install clarifai imutils

### copy files into the image
COPY . $WORKDIR
