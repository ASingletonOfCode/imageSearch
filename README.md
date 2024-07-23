# HEB Image Search

## Requirements

[Requirements Doc](./documentation-artifacts/ES-BackendSoftwareEngineerCodingExercise-250722-1431.pdf)

### API Spec

#### Common Specifications

- **Error Codes**
  - `400 Bad Request` - Returned for invalid image input that 3rd party service cannot process or the application deems inappropriate
  - `404 Not Found`
  - `403`
  - `500`
- **Headers**

#### Individual API Specifications

`GET /images`

- Returns HTTP `200` OK with JSON response
  - `{TODO BODY}
`Image URL's not public accessible
    `GET /images?objects="{object1,object2,...}"`
- Returns HTTP `200` OK with JSON response containing images that contain the detected objects from query params
  - `{TODO BODY}`

`GET /images/{imageId}`

- Returns HTTP `200` OK with a JSON response containing image metadata for the specified image
  - `{TODO BODY}`

`POST /images`

- Send a JSON request body including an image file or URL, an optional label for the image, and an optional field to enable object detection
  - `{TODO Request Body}`
- Returns HTTP `200` OK with a JSON response body including the image data, its label (auto-generated if not provided), it's identifier provided by persistent data store, and any objects detected (if oabject detection was enabled).
  - `{TODO Response BODY}`

### Service Dependencies

- React Frontend (TBD)
  - Provides a UI for users to make requests and upload images
- Python Django Backend
  - REST API's for image handling and issuing requests to 3rd party image detector
- Database
  - Storing of Images and Image metadata
- [Imagga API](https://docs.imagga.com/#tags)
  - 3rd party image detection service

#### Sequence Diagrams

##### `GET /images`

![`GET /images` Sequence Diagram](./documentation-artifacts/GET-images.png)

##### `GET /images?objects="{object1,object2,...}"`

![`GET /images?objects="{object1,object2,...}"` Sequence Diagram](./documentation-artifacts/GET-images-by-objects.png)

##### `GET /images/{imageId}`

![`GET /images/{imageId}` Sequence Diagram](./documentation-artifacts/GET-image-by-id.png)

##### `POST /images`

![`POST /images` Sequence Diagram](./documentation-artifacts/POST-images.png)

### Limitations

1. Since this application depends on the ability for third-party services to detect the requested objects in a provided image, accuracy of object detection may be impacted. That said, the application will do it's best to accept, validate, detect objects, and store requests for safe-for-work (SFW) images.

2. The third-party API's require service agreements that may contain costs; the intention of this application is to support the requirements with as little cost, ideally none, to the implementor. The API contract may be impacted by this limitation.

3. The application will not support additional authentication to reach image URL's not publicly available; for example, an image only accessible privately in someone's Google Photo's suite which would require the application to authenticate with Google to access the photo.

4. Another limitation of the Imagga API is that there is a 5 second limit for downloading an image via URL; that is, if a user requests an image to be searched using a URL rather than uploading the image directly Imagga will return a timeout error, which the application will be forced to bubble up to the user.

## Application Details

### Framework Dependencies

_TODO_

### Local Setup

0.  After cloning the repo, we'll need to setup our local python environment.

    ```
    # Ensure we're in the imageSearch repo

    cd ~/{path-to-imageSearch}/imageSearch

    # install Pyenv https://github.com/pyenv/pyenv?tab=readme-ov-file#automatic-installer
    curl https://pyenv.run | bash


    # activate our environment
    pyenv activate imageSearch

    # install dependencies
    pip install

    ```

1.  Now we need to perform some application setup steps

    ```
    # Create a super user; since this is a local environment enter whatever information works best for you in the resulting prompts.
    # The current configuration of the application allows us to use these same credentials for basic authentication for API requests and the Django-Admin tool (which we'll use in the next step)
    python manage.py createsuperuser

    # Instantiate our DB with our models
    # Django provides tooling that wraps the creation and altering our database tables:
    python manage.py migrate

    ```

    Then we need to make sure our Imagga API creds are setup. Open the file [local.env](./local.env) and replace the values for `IMAGGA_API_KEY` and `IMAGGA_AUTH_KEY` with your personal values.

2.  Let's start the app and make sure we can access Django-Admin. Provided in the root directory is a [makefile](./makefile) with a few targets to save us some typing.

    ```

    # Start the local server using our first make target `runserver` which simply shortens the command `python manage.py runserver`
    make runserver


    ```

### Usage

_TODO_

### Additional Help

As mentioned in the [Local Setup](#local-setup) section, a `makefile` has been provided for some common commands.

To run tests:

```
# the following make target wraps `python manage.py test`
make test
```

To run the python formatter, Black:

```
# the following make target wraps `black .`
make black
```
