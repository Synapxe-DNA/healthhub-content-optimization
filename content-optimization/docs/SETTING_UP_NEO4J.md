# Setting Up Neo4J

## Prerequisites <a id="clustering-prerequisites"></a>

### Configuration <a id="clustering-configuration"></a>

For more information, refer to the [conf/README.md](../conf/README.md#clustering-credentials).

### Neo4j Set Up

1. Download and install Neo4j

   - Follow the [installation guide](https://neo4j.com/docs/operations-manual/current/installation/) provided by Neo4j according to your operating system.

2. Add Local DBMS

   - Open Neo4j Desktop
   - Create a new project or select an existing project
   - Click on "Add" and select "Add Local DBMS"
   - Use the `username` and `password` specified in your `credentials.yml` file in the [`conf/local/`](../conf/local/) directory

3. Create Database

   - Create a database with the `database` variable specified in [`parameters_clustering.yml`](../conf/base/parameters_clustering.yml).

4. Install GDS library plugin

   - Follow the instructions in the [Neo4j GDS Library Installation Guide](https://neo4j.com/docs/graph-data-science/current/installation/neo4j-desktop/) to install the GDS library plugin.

### Data

Verify that the file `ground_truth.xlsx` is available in the [`data/01_raw/`](../data/01_raw/) directory.
