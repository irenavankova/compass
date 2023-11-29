#!/usr/bin/env python3
import os
import shutil
import time

import numpy as np
import xarray

from compass.model import run_model
from compass.ocean.tests.isomip_plus.evap import update_evaporation_flux
from compass.ocean.tests.isomip_plus.viz.plot import MoviePlotter
from compass.step import Step

# get the current working directory
current_working_directory = os.getcwd()
# print output to the console
print(current_working_directory)
work_dir = current_working_directory

mesh_array = f'{work_dir}/init.nc'
experiment = 'Ocean0'

for yr in range(1):
    yy = f'{yr+1}'.zfill(2)
    for k in range(12):
        #Get snapshots from restart files
        mm = f'{k}'.zfill(2)
        output_array = f'{work_dir}/restarts/restart.00{yy}-{mm}-01_00.00.00.nc'
        if os.path.exists(output_array):

            # plot a few fields
            plot_folder = f'{work_dir}/plots_rest'

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

            #plotter.plot_horiz_series(ds.ssh, 'ssh', 'ssh',
            #                          True, vmin=-700, vmax=0)
            plotter.plot_3d_field_top_bot_section(
                ds.temperature, nameInTitle='temperature', prefix='temp', suffix=f'{yy}-{mm}',
                units='C', vmin=-2., vmax=1., cmap='cmo.thermal')

            #plotter.plot_3d_field_top_bot_section(
            #    ds.salinity, nameInTitle='salinity', prefix='salin',
            #    units='PSU', vmin=33.8, vmax=34.7, cmap='cmo.haline')


