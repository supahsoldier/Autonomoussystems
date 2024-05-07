
# Autonomoussystems

Project that uses a swarm of robots to form letters which will be used to spell out words. 

## Authors

- Mick Vermeulen
- Niels Laarhoven
- Melle Herlaar
- Prashant Chotkan



## Features

- The application will have a front-end which will be used to send words to the swarm to spell out.
- the swarm will be able to form up to one letter at a time.

- movement functionality
    - individual robots will be able to perform basic movements to move in any direction.

- visual recognition by opencv
    - individual robots will be tracked by opencv to determine the location

- pathfinding algorithms will be used to guide individual robots to their designated spot to form letters.
## Deployment
The following steps will be required to get the project up and running.

### Prerequisites
 - make sure that [docker](https://docs.docker.com/desktop/install/windows-install/) is installed.
 - the plugin for [docker-compose](https://docs.docker.com/compose/install/) will also be required 

### Steps to start the server
 - clone this repository
 - move to server directory using
```bash
cd server
```
 - start server using the following command
```bash
docker-compose up
```


## Contact

- Mick Vermeulen - 0909880@hr.nl
- Niels Laarhoven - 0998070@hr.nl
- Melle Herlaar - 1029218@hr.nl
- Prashant Chotkan - 1042569@hr.nl


