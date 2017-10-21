from configparser import ConfigParser


class Config:
    config_filename = 'config.ini'
    parser = ConfigParser()
    parser.read(config_filename)

    @classmethod
    def get_postgresql_conn_parameters(cls, section='postgresql'):
        # get section, default to postgresql
        db = {}
        if cls.parser.has_section(section):
            params = cls.parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, cls.config_filename))

        return db
