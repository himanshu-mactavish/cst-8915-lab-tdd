class BaseConfig:
    TESTING=False
    
class DevelopmentConfig(BaseConfig):
    pass

class TestingConfig(BaseConfig):
    pass

class ProductionConfig(BaseConfig):
    pass    
        