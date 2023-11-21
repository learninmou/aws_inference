import time
import logging

logger = logging.getLogger(__name__)

_last_time = time.time()
_config_dict = {}
def lazy_readconfig(file_path : str):
    global _last_time, _config_dict
    cur_time = time.time()
    if file_path not in _config_dict or cur_time - _last_time > 30:
        # TODO check coroutine safe
        _last_time = cur_time
        cadidate_config = []

        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        cadidate_config.append(line)
        except Exception as e:
            logger.error(f'read config file error, {e}')
            pass

        if cadidate_config and _config_dict.get(file_path) != cadidate_config:
            logger.info(f'update config, config={cadidate_config}')
            _config_dict[file_path] = cadidate_config

    return _config_dict[file_path]
