import psycopg2

try:
    connection = psycopg2.connect(
        host = "localhost",
        user = "user_test",
        password = "12345",
        database = "api_users"
    )
    
    print("Conexion exitosa")
    
except Exception as ex:
    print(ex)