
from google.cloud import bigquery
import flask
import json
from flask import jsonify
import oracledb
import os
import logging #package for error logging
from env import * # you must make an env.py file with your oracle.db connection named as "conn"

#tracks error messaging
logging.basicConfig(level=logging.INFO)

def run():
    # conn = oracledb.connect(
    #         the actual connection is found in env.py
    # )
    curs = conn.cursor()
    sql = '''
SELECT source_feature_id,
SDO_GEOM.SDO_CENTROID(shape,0.005).sdo_point.x as x,
SDO_GEOM.SDO_CENTROID(shape,0.005).sdo_point.y as y
FROM SOURCE_FEATURE_PRE_POLY
'''
    curs.execute(sql)
    columns = [col[0] for col in curs.description]
    curs.rowfactory = lambda *args: dict(zip(columns, args))
    gcp = curs.fetchall()

    PROJECT_IDS = ['ut-dnr-biobase-dev', 'ut-gee-dwr-biot-dev']
    dataset_id = 'biotics'
    table_id = 'naturePoly'
    results = []

    for project in PROJECT_IDS:
        # Re-initialize client for the specific project
        client = bigquery.Client(project=project, location="US")
        
        dataset_ref = client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)
        
        job_config = bigquery.LoadJobConfig()
        job_config.autodetect = True
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
        
        # Trigger the load
        job = client.load_table_from_json(
              gcp, table_ref, job_config=job_config
        ) 
        job.result()  # Wait for the job to complete
        
        results.append(f"{project} ({job.output_rows} rows)")
      
    curs.close()
    conn.close()
    
    return "Loaded {} rows into {}:{}".format(job.output_rows, dataset_id, table_id)
