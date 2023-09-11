from compass.ocean.tests.global_ocean.dynamic_adjustment import (
    DynamicAdjustment,
)
from compass.ocean.tests.global_ocean.forward import ForwardStep


class FRIS01to60DynamicAdjustment(DynamicAdjustment):
    """
    A test case performing dynamic adjustment (dissipating fast-moving waves)
    from an initial condition on the SO12to60 MPAS-Ocean mesh

    Attributes
    ----------
    restart_filenames : list of str
        A list of restart files from each dynamic-adjustment step
    """

    def __init__(self, test_group, mesh, init, time_integrator):
        """
        Create the test case

        Parameters
        ----------
        test_group : compass.ocean.tests.global_ocean.GlobalOcean
            The global ocean test group that this test case belongs to

        mesh : compass.ocean.tests.global_ocean.mesh.Mesh
            The test case that produces the mesh for this run

        init : compass.ocean.tests.global_ocean.init.Init
            The test case that produces the initial condition for this run

        time_integrator : {'split_explicit', 'RK4'}
            The time integrator to use for the forward run
        """
        if time_integrator != 'split_explicit':
            raise ValueError('{} dynamic adjustment not defined for {}'.format(
                mesh.mesh_name, time_integrator))

        restart_times = ['0001-01-11_00:00:00', '0001-01-21_00:00:00', '0001-01-31_00:00:00',
                         '0001-02-10_00:00:00',
                         '0001-03-02_00:00:00',
                         '0001-03-22_00:00:00', '0001-04-01_00:00:00']
        '''
        restart_times = ['0001-01-11_00:00:00', '0001-01-21_00:00:00', '0001-01-31_00:00:00',
                         '0001-02-10_00:00:00', '0001-02-10_09:00:00', '0001-02-11_00:00:00',
                         '0001-02-11_10:00:00', '0001-02-11_10:45:00', '0001-02-11_11:00:00',
                         '0001-02-12_00:00:00', '0001-03-02_00:00:00',
                         '0001-03-22_00:00:00', '0001-04-01_00:00:00']
        '''
        restart_filenames = [
            'restarts/rst.{}.nc'.format(restart_time.replace(':', '.'))
            for restart_time in restart_times]

        super().__init__(test_group=test_group, mesh=mesh, init=init,
                         time_integrator=time_integrator,
                         restart_filenames=restart_filenames)

        module = self.__module__

        shared_options = \
            {'config_AM_globalStats_enable': '.true.',
             'config_AM_globalStats_compute_on_startup': '.true.',
             'config_AM_globalStats_write_on_startup': '.true.',
             'config_use_activeTracers_surface_restoring': '.true.'}

        # first step
        step_name = 'damped_adjustment_1'
        step = ForwardStep(test_case=self, mesh=mesh, init=init,
                           time_integrator=time_integrator, name=step_name,
                           subdir=step_name, get_dt_from_min_res=False)

        namelist_options = {
            'config_run_duration': "'00-00-10_00:00:00'",
            'config_dt': "'00:00:30'",
            'config_btr_dt': "'00:00:0.7'",
            'config_implicit_bottom_drag_type': "'constant_and_rayleigh'",
            'config_Rayleigh_damping_coeff': '1.0e-4'}
        namelist_options.update(shared_options)
        step.add_namelist_options(namelist_options)

        stream_replacements = {
            'output_interval': '00-00-10_00:00:00',
            'restart_interval': '00-00-10_00:00:00'}
        step.add_streams_file(module, 'streams.template',
                              template_replacements=stream_replacements)

        step.add_output_file(filename='../{}'.format(restart_filenames[0]))
        self.add_step(step)

        iref = 0
        # second step
        step_name = 'damped_adjustment_2'
        step = ForwardStep(test_case=self, mesh=mesh, init=init,
                           time_integrator=time_integrator, name=step_name,
                           subdir=step_name, get_dt_from_min_res=False)

        namelist_options = {
            'config_run_duration': "'00-00-10_00:00:00'",
            'config_dt': "'00:00:30'",
            'config_btr_dt': "'00:00:0.7'",
            'config_implicit_bottom_drag_type': "'constant_and_rayleigh'",
            'config_Rayleigh_damping_coeff': '1.0e-5',
            'config_do_restart': '.true.',
            'config_start_time': "'{}'".format(restart_times[iref])}
        namelist_options.update(shared_options)
        step.add_namelist_options(namelist_options)

        stream_replacements = {
            'output_interval': '00-00-10_00:00:00',
            'restart_interval': '00-00-10_00:00:00'}
        step.add_streams_file(module, 'streams.template',
                              template_replacements=stream_replacements)

        step.add_input_file(filename='../{}'.format(restart_filenames[iref]))
        step.add_output_file(filename='../{}'.format(restart_filenames[iref+1]))
        self.add_step(step)

        iref = iref + 1
        # third step
        step_name = 'damped_adjustment_3'
        step = ForwardStep(test_case=self, mesh=mesh, init=init,
                           time_integrator=time_integrator, name=step_name,
                           subdir=step_name, get_dt_from_min_res=False)

        namelist_options = {
            'config_run_duration': "'00-00-10_00:00:00'",
            'config_dt': "'00:00:30'",
            'config_btr_dt': "'00:00:0.7'",
            'config_implicit_bottom_drag_type': "'constant_and_rayleigh'",
            'config_Rayleigh_damping_coeff': '5.0e-6',
            'config_do_restart': '.true.',
            'config_start_time': "'{}'".format(restart_times[iref])}
        namelist_options.update(shared_options)
        step.add_namelist_options(namelist_options)

        stream_replacements = {
            'output_interval': '00-00-10_00:00:00',
            'restart_interval': '00-00-10_00:00:00'}
        step.add_streams_file(module, 'streams.template',
                              template_replacements=stream_replacements)

        step.add_input_file(filename='../{}'.format(restart_filenames[iref]))
        step.add_output_file(filename='../{}'.format(restart_filenames[iref + 1]))
        self.add_step(step)

        iref = iref + 1
        # third step extension
        step_name = 'damped_adjustment_3ext'
        step = ForwardStep(test_case=self, mesh=mesh, init=init,
                           time_integrator=time_integrator, name=step_name,
                           subdir=step_name, get_dt_from_min_res=False)

        namelist_options = {
            'config_run_duration': "'00-00-10_00:00:00'",
            'config_dt': "'00:00:30'",
            'config_btr_dt': "'00:00:0.7'",
            'config_implicit_bottom_drag_type': "'constant_and_rayleigh'",
            'config_Rayleigh_damping_coeff': '5.0e-6',
            'config_do_restart': '.true.',
            'config_start_time': "'{}'".format(restart_times[iref])}
        namelist_options.update(shared_options)
        step.add_namelist_options(namelist_options)

        stream_replacements = {
            'output_interval': '00-00-10_00:00:00',
            'restart_interval': '00-00-10_00:00:00'}
        step.add_streams_file(module, 'streams.template',
                              template_replacements=stream_replacements)

        step.add_input_file(filename='../{}'.format(restart_filenames[iref]))
        step.add_output_file(filename='../{}'.format(restart_filenames[iref + 1]))
        self.add_step(step)

        iref = iref + 1
        # fourth step
        step_name = 'damped_adjustment_4'
        step = ForwardStep(test_case=self, mesh=mesh, init=init,
                           time_integrator=time_integrator, name=step_name,
                           subdir=step_name, get_dt_from_min_res=False)

        namelist_options = {
            'config_run_duration': "'00-00-20_00:00:00'",
            'config_dt': "'00:00:30'",
            'config_btr_dt': "'00:00:0.7'",
            'config_implicit_bottom_drag_type': "'constant_and_rayleigh'",
            'config_Rayleigh_damping_coeff': '1.0e-6',
            'config_do_restart': '.true.',
            'config_start_time': "'{}'".format(restart_times[iref])}
        namelist_options.update(shared_options)
        step.add_namelist_options(namelist_options)

        stream_replacements = {
            'output_interval': '00-00-10_00:00:00',
            'restart_interval': '00-00-10_00:00:00'}
        step.add_streams_file(module, 'streams.template',
                              template_replacements=stream_replacements)

        step.add_input_file(filename='../{}'.format(restart_filenames[iref]))
        step.add_output_file(filename='../{}'.format(restart_filenames[iref+1]))
        self.add_step(step)

        iref = iref+1
        # fifth step
        step_name = 'damped_adjustment_5'
        step = ForwardStep(test_case=self, mesh=mesh, init=init,
                           time_integrator=time_integrator, name=step_name,
                           subdir=step_name, get_dt_from_min_res=False)

        namelist_options = {
            'config_run_duration': "'00-00-20_00:00:00'",
            'config_dt': "'00:00:30'",
            'config_btr_dt': "'00:00:0.7'",
            'config_do_restart': '.true.',
            'config_start_time': "'{}'".format(restart_times[iref])}
        namelist_options.update(shared_options)
        step.add_namelist_options(namelist_options)

        stream_replacements = {
            'output_interval': '00-00-05_00:00:00',
            'restart_interval': '00-00-05_00:00:00'}
        step.add_streams_file(module, 'streams.template',
                              template_replacements=stream_replacements)

        step.add_input_file(filename='../{}'.format(restart_filenames[iref]))
        step.add_output_file(filename='../{}'.format(restart_filenames[iref+1]))
        self.add_step(step)

        iref = iref + 1
        # final step
        step_name = 'simulation'
        step = ForwardStep(test_case=self, mesh=mesh, init=init,
                           time_integrator=time_integrator, name=step_name,
                           subdir=step_name, get_dt_from_min_res=False)

        namelist_options = {
            'config_run_duration': "'00-00-10_00:00:00'",
            'config_dt': "'00:01:00'",
            'config_btr_dt': "'00:00:1.3'",
            'config_do_restart': '.true.',
            'config_start_time': "'{}'".format(restart_times[iref])}
        namelist_options.update(shared_options)
        step.add_namelist_options(namelist_options)

        stream_replacements = {
            'output_interval': '00-00-05_00:00:00',
            'restart_interval': '00-00-05_00:00:00'}
        step.add_streams_file(module, 'streams.template',
                              template_replacements=stream_replacements)

        step.add_input_file(filename='../{}'.format(restart_filenames[iref]))
        step.add_output_file(filename='../{}'.format(restart_filenames[iref+1]))
        step.add_output_file(filename='output.nc')
        self.add_step(step)

        self.restart_filenames = restart_filenames

