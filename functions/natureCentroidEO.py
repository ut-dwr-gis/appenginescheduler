
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
select EODATA21,
EODATA20,
EODATA19, 
EODATA18,
EODATA17,
EODATA16,
EODATA15,
EODATA14,
EODATA13,
EODATA12,
EODATA11,
EODATA10,
EODATA9,
EODATA8,
EODATA7,
EODATA6,
EODATA5,
EODATA4,
EODATA3,
EODATA2,
EODATA1,
GENDESC14,
GENDESC13,
GENDESC12,
GENDESC11,
GENDESC10,
GENDESC9,
GENDESC8,
GENDESC7,
GENDESC6,
GENDESC5,
GENDESC4,
GENDESC3,
GENDESC2,
GENDESC1,
LASTOBS,
FIRSTOBS,
SURVEYDATE,
SURVEYSITE,
EO_NUM,
EO_ID from CENTROID_VW_EO_2016   
'''
    curs.execute(sql)
    columns = [col[0] for col in curs.description]
    curs.rowfactory = lambda *args: dict(zip(columns, args))
    gcp = curs.fetchall()

    PROJECT_ID = 'ut-dnr-biobase-dev'
    client = bigquery.Client(project=PROJECT_ID, location="US")
    # set location 
    dataset_id = 'biotics'
    table_id = 'natureCentroidEO'
    # set config
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    job_config = bigquery.LoadJobConfig()
    job_config.autodetect = True
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
    job = client.load_table_from_json(
          gcp, table_ref, job_config=job_config
    ) 
    job.result()  # Wait for the job to complete.
      
    curs.close()
    conn.close()
    
    return "Loaded {} rows into {}:{}".format(job.output_rows, dataset_id, table_id)
