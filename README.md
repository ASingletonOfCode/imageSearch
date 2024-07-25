# HEB Image Search

## Requirements

[Requirements Doc](./documentation-artifacts/ES-BackendSoftwareEngineerCodingExercise-250722-1431.pdf)

## Frontend Application

A corresponding frontend UI can be found here: https://github.com/ASingletonOfCode/imageSearchFE

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
    First, lets instantiate our DB with our models:

    ```
    # Django provides tooling that wraps the creation and altering our database tables:

    python manage.py migrate

    ```

    Now, let's populate our DB with a superuser followed by some AppConfig and FeatureFlag entires.
    This app makes use of feature flags and app configuration values stored in the DB in order to modify application behavior on the fly, without requiring a restart (or redeploy, e.g. in a running Docker container).
    The following executes a custom [Django Management Command](https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/) named `populate_db`, which bundles the superuser and population of AppConfig and FeatureFlags to get running quickly. To run it enter:

    ```
    # Since this is a local environment enter whatever information
    # works best for you in the resulting prompts.
    # The current configuration of the application allows us to use these same credentials for basic authentication
    # for API requests and the Django-Admin tool (which we'll use in the next step)

    python manage.py populate_db
    ```

    Last, we need to make sure our Imagga API creds are setup. Open the file [local.env](./local.env) and replace the values for `IMAGGA_API_KEY` and `IMAGGA_AUTH_KEY` with your personal values.

2.  Let's start the app and make sure we can access Django-Admin. Provided in the root directory is a [makefile](./makefile) with a few targets to save us some typing.

    ```

    # Start the local server using our the make target `runserver` which simply shortens the command `python manage.py runserver`
    make runserver

    ```

    _Fingers Crossed_ We should see the resulting message in the terminal:

    ```
    python manage.py runserver
    Watching for file changes with StatReloader
    Performing system checks...

    System check identified no issues (0 silenced).
    July 24, 2024 - 17:46:33
    Django version 5.0.7, using settings 'imageSearch.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.
    ```

    Now, let's navigate to the [Django Admin Dashboard](http://localhost:8000/admin), using the same credentials as before to authenticate.

3.  From here, we can view and manage the various models stored in our local database. After running the `populate_db` command earlier, we should be able to see 3 entries in the `AppConfig` table by navigating to the [App configs](http://localhost:8000/admin/core/appconfig/) entry in the nav menu on the left.

    #### `safety_confidence_threshold`

    _default value_: `51.0`

    This configuration allows us to set the threshold for what the app to safely allow an image based on it's content. This is used to check against the `confidence` level returned from the Imagga [`GET /categories/<categorizer_id>` API](https://docs.imagga.com/?python#categories-categorizer_id). i.e. if the `confidence` value for the `safe` field in the response is **Less than** this value, the app makes the image as blacklisted.

    When setting this value, simply enter a number; e.g: 25.0

    #### `blacklisted_items`

    _default value_: `None`

    This configuration allows us to set a list of items that we want to blacklist from being stored in the application. For example, if we set this value to `["dog", "cat"]`, the application will not store images that are categorized as having dog or cat in them.

    When setting this value, enter a comma-separated string, no spaces between entries; e.g.: dog,cat

    _Ultimately, I included this to provide a way to test image acceptance validation without having to search, use, and upload NSFW images_

    #### `imagga_nsfw_categorizer_id`

    _default value_: `nsfw_beta`

    This configuration allows us to change the value of the Imagga categorizer for NSFW object detection that the app passes to their API.

    When setting this value, the app will take exactly what you put in and pass it as the query parameter `categorizer_id` for Imagga's `categories/{categorizer_id}` endpoint.

4.  Next, we can navigate to see a single entry in the `FeatureFlag` table by navigating to the [Feature flags](http://localhost:8000/admin/core/featureflag/) entry in the nav menu on the left.

    #### `imagga_nsfw_check`

    _default active_: `false`

    This feature flag gives us the ability to toggle on-and-off if we want to make the Imagga NSFW check.

    _This was added primarily for the use case of not wanting to waste Imagga usage on personal accounts for NSFW checks as I didn't intend to detect objects for NSFW material on the local environment_

5.  Now that we have our local environment setup, we can start the app by running:
    ```
    make runserver
    ```
    Which we can now start making requests to the app using the API's defined in the [Requirements Doc](#requirements) at `localhost:8000/api/*`.

### Additional Help

As mentioned in the [Local Setup](#local-setup) section, a `makefile` has been provided for some common commands.

To run tests:

```
# the following make target wraps `python manage.py test`
make test
```

To run tests and get a code coverage report:

```
# the following runs the tests (just like `make test` above) but with code coverage, and generates a report
make coverage
```

To run the python formatter, Black:

```
# the following make target wraps `black .`
make black
```

To start the app server:

```
make runserver
```

To build the app as a docker image with the name `image-search`:

```
make build
```

To run the built docker image in a container with the name `imageSearch`

```
make run
```

To build and run the app in a docker image:

```
# Warning: this command will attempt to stop and remove any existing containers with the name `imageSearch`
make docker_run
```
