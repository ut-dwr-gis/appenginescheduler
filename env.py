import oracledb
conn = oracledb.connect(
            user='username in quotes',
            password='password in quotes',
            host='hostname can be the webaddress or ip address of the service (in quotes)',
            port=1521,
            service_name='servicename in quotes'
      )
