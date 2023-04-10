import json
import logging
import colorlog
import time
from repository.local_repo.csv_repo import get_app_settings, log_inference_data_in_csv

from utils.logging.constants import LoggingMode, LoggingPayload, LoggingType
from utils.ml_processor.replicate.constants import ReplicateModel

class AppLogger(logging.Logger):
    def __init__(self, name='app_logger', log_file=None, log_level=logging.DEBUG):
        super().__init__(name, log_level)
        self.log_file = log_file

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(levelname)s:%(name)s:%(message)s',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            reset=True,
            secondary_log_colors={},
            style='%'
        )

        ch.setFormatter(formatter)
        self.addHandler(ch)
        self._configure_logging()

    def _configure_logging(self):
        log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(log_formatter)
            self.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        self.addHandler(console_handler)

        # setting logging mode
        app_settings = get_app_settings()
        if 'online' in app_settings and app_settings['online']:
            self.logging_mode = LoggingMode.OFFLINE.value
        else:
            self.logging_mode = LoggingMode.ONLINE.value

    # TODO: extend this method to send logs to the DB
    def _log_data_in_storage(self, log_payload: LoggingPayload):
        log_inference_data_in_csv(log_payload.data)

    def log(self, log_type: LoggingType, log_payload: LoggingPayload):
        if log_type == LoggingType.DEBUG:
            self.debug(log_payload.message)
        elif log_type == LoggingType.INFO:
            self.info(log_payload.message)
        elif log_type == LoggingType.ERROR:
            self.error(log_payload.message)
        elif log_type in [LoggingType.INFERENCE_CALL, LoggingType.INFERENCE_RESULT]:
            self.info(log_payload.message)
            self._log_data_in_storage(log_payload)

    def log_model_inference(self, model: ReplicateModel, time_taken, **kwargs):
        kwargs_dict = dict(kwargs)

        # removing object like bufferedreader, image_obj ..
        for key, value in dict(kwargs_dict).items():
            if not isinstance(value, (int, str, list, dict)):
                del kwargs_dict[key]

        data_str = json.dumps(kwargs_dict)

        data = {
            'model_name': model.name,
            'model_version': model.version,
            'total_inference_time': time_taken,
            'input_params': data_str,
            'created_on': int(time.time())
        }

        logging_payload = LoggingPayload(message="logging inference data", data=data)

        self.log(LoggingType.INFERENCE_CALL, logging_payload)