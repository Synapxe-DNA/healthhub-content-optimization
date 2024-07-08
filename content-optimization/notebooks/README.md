## Neo4j Set Up (Local)
Follow the [installation guide](https://neo4j.com/docs/operations-manual/current/installation/) provided by Neo4j 

## Setup Instructions
1. Configure Environment Variables
    - Create a `.env` file in the `conf/local` directory.
    - Add the following lines to the `.env` file:
        ```python
        neo4j_username=neo4j
        neo4j_password=YOUR_PASSWORD_HERE
        ```

2. Add Local DBMS
    - Open Neo4j Desktop
    - Create a new project or select an existing project
    - Click on "Add" and select "Add Local DBMS"
    - Set the password to be the same as specified in the `.env` file

3. Create Database
    - Create a database with the name specified in the `CONTENT_CATEGORY` variable in `cluster_evaluation.ipynb`

4. Install GDS Library Plugins:
    - Follow the instructions in the [Neo4j GDS Library Installation Guide](https://neo4j.com/docs/graph-data-science/current/installation/neo4j-desktop/) to install the GDS library plugins

## Additional Instructions
- Ensure Neo4j is installed in the virtual environment
- Place embedding files in the `data/07_model_output` directory