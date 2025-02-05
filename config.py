# import os

# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')    
#     # Google Cloud SQL (MySQL) configuration
#     DB_USER = 'billing-admin'
#     DB_PASS = 'NA{E4Yg%OIL17]`G'
#     DB_NAME = 'billing-db'
#     CLOUD_SQL_CONNECTION_NAME = 'double-port-422104:asia-south2:mysql-billing-app'

#     # For VM instance connecting to Cloud SQL via the proxy
#     SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@127.0.0.1:3306/{DB_NAME}"
    
#     SQLALCHEMY_TRACK_MODIFICATIONS = False


#local 
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    
    # Local MySQL database configuration
    DB_USER = 'root'
    DB_PASS = 'root'
    DB_NAME = 'billing'
    DB_HOST = '127.0.0.1'
    DB_PORT = '3306'

    # SQLAlchemy database URI for local MySQL instance
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# import os

# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    
#     # Local MySQL configuration
#     DB_USER = 'root'
#     DB_PASS = 'root'
#     DB_NAME = 'billing'
#     DB_HOST = '127.0.0.1'

#     # For local MySQL
#     SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
    
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
