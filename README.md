# egeoffrey-service-image

This is an eGeoffrey service package.

## Description

Retrieve images from a url or command, perform motion detection and object recognition.

## Install

To install this package, run the following command from within your eGeoffrey installation directory:
```
egeoffrey-cli install egeoffrey-service-image
```
After the installation, remember to run also `egeoffrey-cli start` to ensure the Docker image of the package is effectively downloaded and started.
To validate the installation, go and visit the *'eGeoffrey Admin'* / *'Packages'* page of your eGeoffrey instance. All the modules, default configuration files and out-of-the-box contents if any will be automatically deployed and made available.
## Content

The following modules are included in this package.

For each module, if requiring a configuration file to start, its settings will be listed under *'Module configuration'*. Additionally, if the module is a service, the configuration expected to be provided by each registered sensor associated to the service is listed under *'Service configuration'*.

To configure each module included in this package, once started, click on the *'Edit Configuration'* button on the *'eGeoffrey Admin'* / *'Modules'* page of your eGeoffrey instance.
- **service/image**: retrieve images from a url or by running a command
  - Module configuration:
    - *clarifai_api_key*: clarifai API Key (https://portal.clarifai.com/signup) for object detection
  - Service configuration:
    - Mode 'pull':
      - *url*: download the image from this URL (e.g. http://domain.com/image.jpg)
      - *username*: username if the URL requires basic authentication (e.g. username)
      - *password*: password if the URL requires basic authentication (e.g. password)
      - *command*: run a command returning an image (e.g. raspistill -w 640 -h 480 -o -)
      - *detect_motion_threshold*: ignore the image unless a motion (higher than this %) is detected (e.g. 20)
      - *detect_people_threshold*: ignore the image unless at least this number of people are detected in the image (e.g. 1)
      - *detect_object_name*: ignore the image unless this object is detected in the image (e.g. people)
      - *detect_object_threshold*: ignore the image unless the detected object has a confidence level higher than this percentage (e.g. 98)

## Contribute

If you are the author of this package, simply clone the repository, apply any change you would need and run the following command from within this package's directory to commit your changes and automatically push them to Github:
```
egeoffrey-cli commit "<comment>"
```
After taking this action, remember you still need to build (see below) the package (e.g. the Docker image) to make it available for installation.

If you are a user willing to contribute to somebody's else package, submit your PR (Pull Request); the author will take care of validating your contributation, merging the new content and building a new version.

## Build

Building is required only if you are the author of the package. To build a Docker image and automatically push it to [Docker Hub](https://hub.docker.com/r/egeoffrey/egeoffrey-service-image), run the following command from within this package's directory:
```
egeoffrey-cli build egeoffrey-service-image
```

## Uninstall

To uninstall this package, run the following command from within your eGeoffrey installation directory:
```
egeoffrey-cli uninstall egeoffrey-service-image
```
Remember to run also `egeoffrey-cli start` to ensure the changes are correctly applied.
## Tags

The following tags are associated to this package:
```
service image webcam
```

## Version

The version of this egeoffrey-service-image is 1.1-1 on the development branch.
