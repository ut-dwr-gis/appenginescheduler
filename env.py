import oracledb
conn = oracledb.connect(
            user='username in quotes',
            password='password in quotes',
            host='bioticsut.natureserve.org',
            port=1521,
            service_name='biotics'
      )
