"""
Get probe from library
----------------------

`probeinterface` provides a library of probes from several manufacturers on the GitHub platform:
https://github.com/SpikeInterface/probeinterface_library

Users and manufacturers are welcome to contribute to it.

The Python module provide a function to download and cache files locally
in the `probeinterface` json-based format.
"""

##############################################################################
from pprint import pprint

import numpy as np
import matplotlib.pyplot as plt

from probeinterface import Probe, get_probe
from probeinterface.plotting import plot_probe
from probeinterface import write_probeinterface, read_probeinterface
from probeinterface import write_prb, read_prb

##############################################################################
#  Download one probe:

manufacturer = 'cambridgeneurotech'
probe_name = 'ASSY-158-H6'

probe = get_probe(manufacturer, probe_name)
print(probe)

##############################################################################
# Files from the library also contain annotations specific to manufacturers.
# We can see here that Neuronexus probes have contact indices starting at "1" (one-based)

pprint(probe.annotations)

##############################################################################
# When plotting, the channel indices are automatically displayed with
# one-based notation (even if internally everything is still zero based):

plot_probe(probe, with_channel_index=True)

##############################################################################

plt.show()
