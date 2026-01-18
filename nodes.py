from theflow import Node,Flow
import psycopg2
import pandas as pd
from call_llm import call_llm
# giao dien -> input  -> list all song release before 2010 -> shared_data["user_query"]  = " list all song release before 2010" -> run node


class GetSchemas(Node):
    def prep(self,shared_data):
        return shared_data["conn_params"]
    
    def exec(self,pres):
        conn_params = pres
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
        return 'default'        

 

# shared_data["user_query"]

class CreateQuery(Node):

    def prep(self,shared_data):
        return  shared_data["user_query"], shared_data["database_schema"]
        
    def exec(self,pres):
        # a,b  = c
        user_query, database_schema = pres
        

        prompt = f"""
You are an expert PostgreSQL SQL assistant.

Your task:
- Convert a natural language question into a SINGLE PostgreSQL SQL query.
- Use ONLY tables and columns defined in the database_schema.
- Do NOT hallucinate tables, columns, or relationships.
- Use explicit JOINs.
- PostgreSQL syntax only (DATE_TRUNC, ILIKE, COALESCE, FILTER, DISTINCT ON allowed).
- If the query is ambiguous, make the smallest reasonable assumption and list it.
- If it cannot be answered, return an error in YAML.

Output MUST be valid YAML and nothing else.

EXAMPLE 1
user_query: "Total revenue per month in 2024"

database_schema: |
  Table orders:
    - order_id (INT)
    - order_date (DATE)
    - total_amount (NUMERIC)

YAML output:
sql_query: |
  SELECT
      DATE_TRUNC('month', order_date) AS month,
      SUM(total_amount) AS total_revenue
  FROM orders
  WHERE order_date >= DATE '2024-01-01'
    AND order_date < DATE '2025-01-01'
  GROUP BY month
  ORDER BY month;
assumptions:
  - Revenue is represented by total_amount.
notes:
  - Used DATE_TRUNC for monthly aggregation.
confidence: high

EXAMPLE 2
user_query: "List customers who placed more than 5 orders"

database_schema: |
  Table customers:
    - customer_id (INT)
    - name (TEXT)

  Table orders:
    - order_id (INT)
    - customer_id (INT)`
    - order_date (DATE)

YAML output:
sql_query: |
  SELECT
      c.customer_id,
      c.name,
      COUNT(o.order_id) AS order_count
  FROM customers c
  JOIN orders o
    ON c.customer_id = o.customer_id
  GROUP BY c.customer_id, c.name
  HAVING COUNT(o.order_id) > 5;
assumptions: []
notes:
  - COUNT is applied per customer.
confidence: high

EXAMPLE 3 (AMBIGUOUS)
user_query: "Top products"

database_schema: |
  Table products:
    - product_id (INT)
    - name (TEXT)

  Table order_items:
    - order_id (INT)
    - product_id (INT)
    - quantity (INT)

YAML output:
sql_query: |
  SELECT
      p.product_id,
      p.name,
      SUM(oi.quantity) AS total_quantity
  FROM products p
  JOIN order_items oi
    ON p.product_id = oi.product_id
  GROUP BY p.product_id, p.name
  ORDER BY total_quantity DESC
  LIMIT 10;
assumptions:
  - Top products means products with highest total quantity sold.
notes:
  - Used quantity as popularity metric.
confidence: medium

EXAMPLE 4 (NOT ANSWERABLE)
user_query: Average delivery time per customer

database_schema: |
  Table orders:
    - order_id (INT)
    - customer_id (INT)
    - order_date (DATE)

YAML output:
error:
  type: not_answerable
  message: Delivery time cannot be calculated without delivery or shipping dates.
  missing_info:
    - delivery_date
    - shipped_date


NOW YOUR TURN
user_query: "{user_query}"

currently, database schema looks like this: 
{database_schema}

your YAML output:
"""
        result = call_llm(prompt)
        import yaml
        cleaned_result = result.strip().split("```yaml")[-1].split("```")[0].strip()
        res_dict = yaml.safe_load(cleaned_result)
        
        assert isinstance(res_dict, dict), "LLM output is not a valid YAML dictionary."
        return res_dict["sql_query"]
                
    def post(self,shared_data,pres,exec_res):
        shared_data["sql_query"] = exec_res
        return 'default'

class ExecuteQuery(Node):
    def prep(self,shared_data):
        return shared_data["conn_params"], shared_data["sql_query"]

    def exec(self,pres):
        conn_params, sql_query = pres
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        print(result)        
                    
        cursor.close()
        conn.close()
        return result
    def post(self,shared_data,pres,exec_res):
        shared_data["sql_query"] = exec_res
        return 'default'

    
        
if __name__ == "__main__":
    
    shared = {}
    
    conn_params = {
    "host": "localhost",
    "user": "postgres",
    "password": "Strongpassword1234",
    "port": "5432",
    "dbname": "sport"
}
    shared["conn_params"] = conn_params
    shared["user_query"] = "how many athletes are there ?"
    
    g = GetSchemas()
    c = CreateQuery()
    e = ExecuteQuery()
    g >> c
    c >> e
    
    
    f  =  Flow(start=g)
    f.run(shared)
    