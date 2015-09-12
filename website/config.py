import os
basedir = os.path.abspath(os.path.dirname(__file__))

if os.path.exists('.env'):
    #root.info('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=',1)
        if len(var) == 2:
            os.environ[var[0]] = var[1]
         

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'd987j'
    DEBUG = False
    # SQLALCHEMY_DATABASE_URI = r'sqlite:////home/azureuser/website_runs_from_here/HMRCTradeDataParser/website/trade_data.db'




class DevelopmentConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join((basedir), 'trade_data.db')
    #SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STRING_SQLALCHEMY_WINDOWS')

class AzureConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')





config = {
    "development": DevelopmentConfig,
    "azure": AzureConfig,
    "default": Config
}
