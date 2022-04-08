
from pyMCDS_cells import pyMCDS_cells

mcds=pyMCDS_cells("output00000049.xml")

print(mcds.get_time())
#49.0

print(mcds.data['discrete_cells']['cell_ID'])
#[0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 1. 1. 1. 1. 1. 1. 1. 1. 2. 2. 2. 2. 2. 2.
# 2. 2. 2. 0. 0. 0. 0. 0. 0. 0. 0. 0. 1. 1. 1. 1. 1. 1. 1. 1. 2. 2. 2. 2.
# 2. 2. 2. 2.]
