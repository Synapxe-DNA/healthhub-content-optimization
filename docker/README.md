# Docker for Healthhub Content Optimization

Docker is currently used to host a MongoDB instance that is used for local development.

---

## Getting Started

1. Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/) on your local machine.
2. Started Docker Desktop.
3. Create an environment file named `dockercompose.env.local` in this directory, and populate the environment variables
   according to `dockercompose.env.sample`.

> [!NOTE]
> The environment variables set will determine your login credentials to the Mongo DB instance.

---

## Local Development

The `Makefile` in the parent directory contains the commands to start and stop the Mongo DB instance on the local
instance. To start or stop the Mongo DB, run the following commands in the root directory (the one with the `Makefile`).

```bash
# Starts Mongo DB
make local-db-start

# Stops Mongo DB
make local-db-stop
```

When connecting to Mongo DB, the following connection string can be used. Replace the variables in the connection
string with the variables you have set.

```text
mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@localhost:27017/
```

> [!IMPORTANT]
> The curly braces `{}` must removed.
