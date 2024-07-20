from enum import Enum


class Environment(str, Enum):
    LOCAL = "LOCAL"
    TESTING = "TESTING"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"

    @property
    def is_debug(self):
        return self in (self.LOCAL, self.TESTING, self.STAGING)
    
    @property
    def is_testing(self):
        return self in (self.TESTING)

    @property
    def is_deploy(self):
        return self in (self.STAGING, self.PRODUCTION)
