import boto.glacier.layer1
import configparser
import hashlib
import os
import random
import string
import time


class Util:
    @staticmethod
    def randomname(l):
        return ''.join(random.choice(string.ascii_lowercase) for i in range(l))

    @staticmethod
    def get_new_vault():
        name = '%s-%s-%d' % (GlacierTestsConfig().prefix(), Util.randomname(8),
                             int(time.time()))
        return GlacierTestsConfig().connection().create_vault(name)

    @staticmethod
    def upload_archive(vault, archive, description):
        # TODO: currently only single part archives < 1MB are supported (since
        # we don't compute the sha256 tree hash
        h = hashlib.sha256()
        h.update(archive)
        digest = h.hexdigest()
        return GlacierTestsConfig().connection().upload_archive(vault, archive,
                                                                digest, digest,
                                                                description)


class GlacierTestsConfig:
    class __Glacier:
        CONFIG_VAR = "GLACIER_TEST_CONF"
        CONFIG_MAP = {
                      "access_key": "aws_access_key_id",
                      "secret_key": "aws_secret_access_key",
                      "https": "is_secure",
                      "port": "port",
                      "host": "host",
                      "prefix": None
                     }
        OPTION_MAP = {
                      "is_secure": "getboolean",
                      "port": "getint"
                     }

        def __init__(self):
            if self.CONFIG_VAR not in os.environ:
                print("Environment variable %s must be defined" %
                      self.CONFIG_VAR)
                exit(1)
            config_file = os.environ.get(self.CONFIG_VAR)
            self.config = self.read_config(config_file)
            if not self.config:
                print("Empty configuration read from %s" % config_file)
                exit(1)
            self.prefix = self.config['glacier']['prefix']
            self.glacier = self.connect()

        def read_config(self, config_file):
            config = configparser.ConfigParser()
            config.read(config_file)
            if not config.sections():
                return None
            return config

        def connect(self):
            connect_args = {}
            for section in self.config.sections():
                for k in self.config[section]:
                    boto_arg = self.CONFIG_MAP[k]
                    if not boto_arg:
                        continue
                    if boto_arg in self.OPTION_MAP:
                        method_name = self.OPTION_MAP[boto_arg]
                        method = getattr(self.config[section], method_name)
                        connect_args[boto_arg] = method(k)
                        continue
                    connect_args[self.CONFIG_MAP[k]] = self.config[section][k]
            return boto.glacier.layer1.Layer1(**connect_args)

    instance = None

    def __init__(self):
        if not GlacierTestsConfig.instance:
            self.instance = self.__Glacier()

    def connection(self):
        return self.instance.glacier

    def prefix(self):
        return self.instance.prefix
