### Base Reqs
- [ ] Expose REST API's
    - [ ] `GET /images`
    - [ ] `GET /images?objects="{object1,object2,...}"`
    - [ ] `GET /images/{imageId}`
    - [ ] `POST /images`
        - [ ] URL Image
        - [ ] Uploaded Image
- [ ] 3rd party image search config and integration
- [ ] Persistence

### Nice to Haves
- [ ] Restricted Objects
- [ ] Documentation
    - [ ] Local setup instructions
    - [ ] UML Sequence Flow
    - [ ] UML Model Diagram
- [ ] Containerization
- [ ] User Registration
- [ ] Authentication
- [ ] Feature Flags
- [ ] Secrets management
- [ ] Frontend UI
- [ ] Multiple-backends to simulate Service migration
- [ ] Metrics


## Open Questions

1. How to share with the team?
2. Do I need to share 3rd party API keys or will the team provide their own?
3. Authentication is not mentioned as a requirement?
    * Provide instructions to create users?
4. What does "image metadata" entail?
5. All APIs include a response of "containing image metadata" except for `GET /images?objects="dog,cat"`. It states "response body containing only images that have the detected objects specified in the query parameter".
   * Is this the only API that should return the image object?
   * Is the objects parameter inclusive or exclusive? i.e. should it match images that contain one or more provided objects or should it match objects containing all provided objects?
   * Should it contain the metadata as well? This could include additional objects not requested but are contained within the images found.