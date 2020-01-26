import pathlib
import yaml
from typing import Dict, List
from . import CTBLogging
from Util.Helper import check_attribute
# load config from home directory

logger = CTBLogging.getLogger('Config')
config: Dict

try:
    home = str(pathlib.Path.home())
    config = yaml.load(open(f'{home}/.ctb/config.yaml'), Loader=yaml.FullLoader)

    # test attributes
    attributes = [
        'ForwardList',   # directed graph contains forward relationships
        'Driver',        # configs for each driver
        'DataRoot',      # file root for images
        'CommandStart',  # command hint format, e.g. "/" for /start, /stop type of commands
    ]
    check_attribute(config, attributes, logger)

except FileNotFoundError:
    logger.error(f'config.yaml not found under "{home}/.ctb/"!')
    exit(-1)

