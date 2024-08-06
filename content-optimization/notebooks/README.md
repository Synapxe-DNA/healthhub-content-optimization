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

   - Create a database with the name specified in the `CONTENT_CATEGORY` variable in `clustering.ipynb`

4. Install GDS Library Plugins:
   - Follow the instructions in the [Neo4j GDS Library Installation Guide](https://neo4j.com/docs/graph-data-science/current/installation/neo4j-desktop/) to install the GDS library plugins

## Clustering notebooks

1. sbert_embeddings.ipynb

   - Description: Generates embeddings from selected columns.

2. clustering.ipynb

   - Description: Runs clustering using neo4j gds.
   - Note:
     - Ensure Neo4j is installed in the virtual environment
     - Setup of neo4j database required
     - Current notebook only uses 1 column for clustering (extracted_body_content). Refinement needed depending on methodology to use multiple columns for clustering

3. cluster_viz.ipynb
   - Description: Visualisation of clusters using pyvis, for qualitative evaluation
