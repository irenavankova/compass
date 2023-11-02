import os
import shutil
import time

import numpy as np
import xarray

from compass.model import run_model
from compass.ocean.tests.isomip_plus.evap import update_evaporation_flux
from compass.ocean.tests.isomip_plus.viz.plot import MoviePlotter
from compass.step import Step

work_dir = '/lcrc/group/e3sm/ac.vankova/compass/sg_tests/sg_00/ocean/isomip_plus/planar/5km/z-star/Ocean0/sim_sgr0'
mesh_array = f'{work_dir}/init.nc'
output_array = f'{work_dir}/restarts/restart.0001-02-01_00.00.00.nc'
experiment = 'Ocean0'
# plot a few fields
plot_folder = f'{work_dir}/plots'

dsMesh = xarray.open_dataset(mesh_array)
ds = xarray.open_dataset(output_array)

section_y = float(40000)
# show progress only if we're not writing to a log file
#show_progress = self.log_filename is None
plotter = MoviePlotter(inFolder=work_dir,
                       streamfunctionFolder=work_dir,
                       outFolder=plot_folder, sectionY=section_y,
                       dsMesh=dsMesh, ds=ds, expt=experiment,
                       showProgress=False)

plotter.plot_horiz_series(ds.ssh, 'ssh', 'ssh',
                          True, vmin=-700, vmax=0)
plotter.plot_3d_field_top_bot_section(
    ds.temperature, nameInTitle='temperature', prefix='temp',
    units='C', vmin=-2., vmax=1., cmap='cmo.thermal')

plotter.plot_3d_field_top_bot_section(
    ds.salinity, nameInTitle='salinity', prefix='salin',
    units='PSU', vmin=33.8, vmax=34.7, cmap='cmo.haline')


