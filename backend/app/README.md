
# FastAPI Backend

> [!NOTE]
> This `README` will be updated.

---

## Getting Started

> [!NOTE]
> At this point, it is assumed that `poetry` has been installed on your device.

Create an environment file, and populate the keys found in `.env.sample` with the values specific for you.

```bash
touch ./.env
```

Navigate to this directory and enter into a poetry shell.

```bash
poetry shell
```

Poetry is used to start the backend server. Currently, there is only one command that can start the server.

```bash
poetry run dev
```

---

## Endpoint Documentation

Endpoints should be documented in `EndpointDocs.yaml` using [OpenAPI specification](https://swagger.io/docs/specification/basic-structure/).

---

## Scripts

### Generate Mock Data

A python script has been created to generate mock data. This is runnable using poetry.

```bash
poetry run mock
```

### Populate MongoDB with Actual Data

```bash
poetry run data
```
