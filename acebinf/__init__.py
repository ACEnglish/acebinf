"""
Sets up package
"""
from acebinf.cmd_exe import (
    cmd_exe
)

from acebinf.log import (
    setup_logging
)

from acebinf.math_utils import (
    percentile,
    phi,
    p_obs
)

from acebinf.multiprocess_utils import (
    Consumer,
    ConsumerPool
)

from acebinf.pedigree import (
    Pedigree
)

from acebinf.vcf_utils import (
    add_format,
    add_info,
    edit_format
)
