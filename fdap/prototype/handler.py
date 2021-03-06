from abc import ABC, abstractmethod
from fdap.utils.util import object_to_json
from fdap.utils.loggeradapter import LoggerAdapter
from fdap.utils.customlogger import CustomLogger
from datetime import datetime
from fdap.contracts.jsonable import Jsonable
from fdap.definitions import PROTOTYPE_PATH
from os.path import exists
import traceback
import json
import os


class Handler(ABC):
    TAG: str = 'test'
    output_format: str = '{datetime} - {name} - {level} - {message}'
    _logger: LoggerAdapter
    _save_result: bool
    _parameters: dict = {}

    def __init__(self, parameters: dict = None, save_result: bool = False):
        if parameters is not None:
            self._parameters = parameters
        self._logger = CustomLogger().logger('test', self.TAG)
        self._save_result = save_result

    def get_parameters(self) -> dict:
        return self._parameters

    def run(self):
        try:
            result = self.handle()
            self.debug('success')
            self.debug('result:' + str(result))
            self.info(str(result))
            if self._save_result:
                self._save_json(result)
        except (Exception,):
            self.error('Fail:')
            self.error('ERROR:')
            self.error(traceback.print_exc())

    def __console(self, level, msg):
        now = datetime.now()
        now.strftime('%Y-%m-%d %H:%M:%S,%f')
        print(self.output_format.format(datetime=now, name=self.TAG, level=level, message=msg))

    def info(self, msg: str):
        self._logger.info(msg)
        self.__console('INFO', msg)

    def debug(self, msg: str):
        self._logger.debug(msg)
        self.__console('DEBUG', msg)

    def warning(self, msg):
        self._logger.warning(msg)
        self.__console('WARNING', msg)

    def error(self, msg):
        self._logger.error(msg)
        self.__console('ERROR', msg)

    def _save_json(self, result):
        result_path = PROTOTYPE_PATH + '/results/'
        if not exists(result_path):
            os.mkdir(result_path)
        with open(result_path + self.TAG + '.json', 'w+', encoding='utf-8') as f:
            if isinstance(result, str):
                f.write(result)
            elif isinstance(result, Jsonable):
                f.write(result.to_json())
            elif isinstance(result, object):
                f.write(object_to_json(result))
            else:
                f.write(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))

    @abstractmethod
    def handle(self):
        pass
