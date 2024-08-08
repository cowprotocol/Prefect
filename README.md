# Prefect Dashboard

This repository sets up and runs a Prefect dashboard for visualizing and managing data workflows. You can deploy the application using either Docker Compose or Kubernetes.

## Application Components

The application consists of four main components:

1. **nginx**: Acts as a reverse proxy for the dashboard, routing traffic to the prefect-server and using oauth2-proxy for authentication..
2. **oauth2-proxy**: Handles user authentication to secure access to the dashboard.
3. **prefect-server**: The core application that hosts and manages the Prefect dashboard for data workflow visualization and management.
4. **prefect-deployments**: Manages and runs the Prefect deployments that drive the dashboard’s operations.

## Deployment Options

- **Docker Compose**: Use Docker Compose to build and run the application locally.
- **Kubernetes**: Deploy the application in a Kubernetes cluster for a more scalable and production-ready setup.

## Getting Started

### Using Docker Compose

>docker compose up

This will build the repo using the `docker-compose.yaml` file. Doing this will run the main dashboard on localhost:80 so you can access the dashboard by going to `https://localhost` in your browser.


### Using Kubernetes

>kubectl apply -f ./kuberenetes

This does not automatically expose the nginx proxy, so in order to access the dashboard you will have to manually publish the pod's port 80: `kubectl port-forward <nginx-....> 8080:80` (you can find the nginx pod name with `kubectl get po`). After this you can find the dashboard on https://localhost:8080.

## Configuration

If you are using docker-compose then the build should automatically read the environment variables from your .env file. With kubernetes you would have to first create a secret store named `oauth-secret` to store the oauth2-proxy environment variables:

>kubectl create secret generic oauth-secret --from-env-file=.env
