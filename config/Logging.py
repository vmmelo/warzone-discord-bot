import logging


def saveLog(filename, content, log_type='info'):
    logging.basicConfig(handlers=[logging.FileHandler('logs/' + filename, 'w+', 'utf-8')], level=20)
    logging.getLogger().addHandler(logging.StreamHandler())
    if log_type == 'error':
        logging.error(content)
    elif log_type == 'warning':
        logging.warning(content)
    else:
        logging.info(content)
