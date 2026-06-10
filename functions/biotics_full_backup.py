from google.cloud import bigquery
import oracledb
import logging
from env import *

logging.basicConfig(level=logging.INFO)

# Map out instructions for specific tables
# Test configuration covering all major data types in your Biotics database
TABLES_CONFIG = {
    # -------------------------------------------------------------
    # 1. STANDARD LOOKUP TABLES (Small, safe text/number tables)
    # -------------------------------------------------------------
    "NATION": {
        "query": "SELECT * FROM NATION"
    },
    "CONTACT": {
        "query": "SELECT * FROM CONTACT"
    },
    "D_DATASET": {
        "query": "SELECT * FROM D_DATASET"
    },
    "SOURCE_FEATURE_PRE_POLY": {
        "query": "SELECT * FROM D_DATASET"
    },
    
    # -------------------------------------------------------------
    # 2. VIEWS
    # -------------------------------------------------------------
    "BCD_EOR": {
        "query": "SELECT * FROM BCD_EOR"
    },
    
    # -------------------------------------------------------------
    # 3. SPATIAL TABLES (Extracts centroid coordinates vs WKT Text)
    # -------------------------------------------------------------
    "SOURCE_FEATURE_PRE_POLY_CENT": {
        "query": """
            SELECT source_feature_id,
                   SDO_GEOM.SDO_CENTROID(shape, 0.005).sdo_point.x AS x,
                   SDO_GEOM.SDO_CENTROID(shape, 0.005).sdo_point.y AS y
            FROM SOURCE_FEATURE_PRE_POLY
            WHERE shape IS NOT NULL AND ROWNUM <= 10000
        """
    },
    "EO_SHAPE": {
        "query": """
            SELECT eo_id, 
                   SDO_UTIL.TO_WKTGEOMETRY(shape) AS wkt_geometry
            FROM EO_SHAPE
            WHERE shape IS NOT NULL AND ROWNUM <= 10000
        """
    }
}

def run():
    curs = conn.cursor()
    project_id = 'ut-gee-dwr-biot-dev'
    dataset_id = 'bioticsBackup'
    client = bigquery.Client(project=project_id, location="US")

    for table_name, config in TABLES_CONFIG.items():
        logging.info(f"Processing table: {table_name}")
        try:
            # Execute the specific query designed for this table
            curs.execute(config["query"])
            
            columns = [col[0] for col in curs.description]
            curs.rowfactory = lambda *args: dict(zip(columns, args))
            
            # Memory safeguard: fetch rows in smaller chunks rather than all at once
            # This prevents crashing on massive log or _DEL tables
            ROW_BATCH_SIZE = 50000
            first_batch = True
            
            while True:
                data = curs.fetchmany(ROW_BATCH_SIZE)
                if not data and not first_batch:
                    break
                if not data and first_batch:
                    logging.info(f"Table {table_name} is empty. Skipping.")
                    break

                table_ref = client.dataset(dataset_id).table(table_name)
                job_config = bigquery.LoadJobConfig()
                job_config.autodetect = True
                
                # Truncate on the very first batch write, then append subsequent chunks
                if first_batch:
                    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
                    first_batch = False
                else:
                    job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

                job = client.load_table_from_json(data, table_ref, job_config=job_config)
                job.result()
                
            logging.info(f"Successfully migrated: {table_name}")

        except Exception as e:
            logging.error(f"Failed to copy {table_name}. Error: {str(e)}")
            continue

    curs.close()
    conn.close()
