print 'Installing JsSeo...'

print 'Creating Database...'

db = mysqldbhelper.DatabaseConnection(config.hostname,
                    user=config.user,
                    passwd=config.passwd,
                    db=config.db)

f = open('schema/schema.sql')
schema = f.read()
db.put(schema)
