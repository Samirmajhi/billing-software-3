import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')    
    # Google Cloud SQL (MySQL) configuration
    DB_USER = 'billing-admin'
    DB_PASS = 'NA{E4Yg%OIL17]`G'
    DB_NAME = 'billing-db'
    CLOUD_SQL_CONNECTION_NAME = 'double-port-422104:asia-south2:mysql-billing-app'

    # For VM instance connecting to Cloud SQL via the proxy
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@127.0.0.1:3306/{DB_NAME}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False