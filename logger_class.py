import logging
import logging.config
from logging_conf.logging_dictionary import log_config


class Logger:
    def __init__(self):

        logging.config.dictConfig(log_config)
        self.info_logger = logging.getLogger("info_logger")
        self.error_logger = logging.getLogger("error_logger")
        self.capacity_logger = logging.getLogger("capacity_logger")
        self.workspace_generate_logger = logging.getLogger("wkspc_generator_logger")
        self.datasource_generate_logger = logging.getLogger(
            "datasource_generator_logger"
        )

    def logger_info(self, i):
        self.info_logger.info(i)

    def logger_error(self, func_name, e):
        self.error_logger.error(e)

    def logger_capacity(self, capacity_msg):
        self.capacity_logger.info(capacity_msg)

    def logger_wkspc_generator(self, workspace_msg):
        self.workspace_generate_logger.info(workspace_msg)

    def logger_datasource_generator(self, datasource_msg):
        self.datasource_generate_logger.info(datasource_msg)
