# What is this for?

This folder should be used to store configuration files used by Kedro or by separate tools.

This file can be used to provide users with instructions for how to reproduce local configuration with their own credentials. You can edit the file however you like, but you may wish to retain the information below and add your own section in the section titled **Instructions**.

## Local configuration

The `local` folder should be used for configuration that is either user-specific (e.g. IDE configuration) or protected (e.g. security keys).

### Clustering Credentials <a id="clustering-credentials"></a>

If it does not already exist, create a new `credentials.yml` file in the [`local/`](local/) directory and include these Neo4j credentials:

```yaml
neo4j_credentials:
  username: <YOUR_USERNAME>
  password: <YOUR_PASSWORD>
```

Ensure that your [`parameters_clustering.yml`](base/parameters_clustering.yml) file contains the necessary Neo4j configurations:

```yaml
neo4j_config:
  uri: neo4j://localhost:7687
  database: hh-articles
```

### Azure Credentials <a id="azure-credentials"></a>

If it does not already exist, create a new `credentials.yml` file in the [`local/`](local/) directory and include these Azure credentials:

```yaml
azure_credentials:
  api_version: <API_VERSION>
  azure_endpoint: <MODEL_ENDPOINT>
  cognitive_services: <NAME_OF_COGNITIVE_SERVICES>
  model_deployment: <DEPLOYMENT_NAME>
```

**Step 1:** For API version, see here for the latest version: [API Version Reference](https://learn.microsoft.com/azure/ai-services/openai/reference)

**Step 2:**
![Step 2](/content-optimization/docs/images/azure_1.png)

**Step 3:**
![Step 3](/content-optimization/docs/images/azure_2.png)

**Step 4:**
![Step 4](/content-optimization/docs/images/azure_3.png)

**Step 5:**
![Step 5](/content-optimization/docs/images/azure_4.png)

**Step 6:**
![Step 6](/content-optimization/docs/images/azure_5.png)

> [!NOTE]
> Please do not check in any local configuration to version control.

## Base configuration

The `base` folder is for shared configuration, such as non-sensitive and project-related configuration that may be shared across team members.

> [!WARNING]
> Please do not put access credentials in the base configuration folder.

## Find out more

You can find out more about configuration from the [user guide documentation](https://docs.kedro.org/en/stable/configuration/configuration_basics.html).
