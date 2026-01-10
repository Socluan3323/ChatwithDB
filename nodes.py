from theflow import Node
import psycopg2
import pandas as pd
        


class GetSchemas(Node):
    def prep(self,shared_data):
        return shared_data
    
    def exec(self,pres):
        conn_params = pres["conn_params"]
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
  
        def detail_schema_table(table_name):
            query = f""" SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table_name}'; 
            """
            cursor.execute(query)
            result = cursor.fetchall()
            df = pd.DataFrame(result, columns=['column_name', 'data_type'])
            return df
        get_schema = """ SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'; 
"""       
        cursor.execute(get_schema)
        result = cursor.fetchall()
        database_schema  = ""
 
        for i in range(len(result)):
            database_schema += "\n" + "TABLE " + result[i][0] + ":\n"
            database_schema += detail_schema_table(result[i][0]).to_string(index=False)
            # print(detail_schema_table(result[i][0]).to_string(index=False))
            
        cursor.close()
        conn.close()
        return database_schema  
    def post(self,shared_data,pres,exec_res):
        shared_data["database_schema"] = exec_res
        
if __name__ == "__main__":
    
    shared = {}
    
    conn_params = {
    "host": "localhost",
    "user": "postgres",
    "password": "Strongpassword1234",
    "port": "5432",
    "dbname": "songdb"
}
    shared["conn_params"] = conn_params
    
    print(shared)
    node = GetSchemas()
    node.run(shared)
    
    
    print(shared["database_schema"])
    
    