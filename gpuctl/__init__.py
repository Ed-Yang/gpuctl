#!/usr/bin/env python3

import os
import sys
import logging

logger = logging.getLogger(__name__)
DRYRUN = bool(os.environ.get('DRYRUN', False))

logging.basicConfig(stream=sys.stdout,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

__all__ = []

from . utils import *
__all__ += utils.__all__

from . gpu_dev import *
__all__ += gpu_dev.__all__

from . gpu_amd import *
__all__ += gpu_amd.__all__

from . gpu_nv import *
__all__ += gpu_nv.__all__

from . gpu_mock import *
__all__ += gpu_mock.__all__

from . gpu_ctl import *
__all__ += gpu_ctl.__all__

from . eth_ctl import *
__all__ += gpu_ctl.__all__

from . version import *
__all__ += gpu_ctl.__all__

