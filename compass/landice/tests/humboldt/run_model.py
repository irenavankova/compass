from compass.model import run_model, make_graph_file
from compass.step import Step


class RunModel(Step):
    """
    A step for performing forward MALI runs as part of Humboldt test cases.

    Attributes
    ----------
    mesh_type : str
        The resolution or mesh type of the test case

    velo_solver : str
        The velocity solver used for the test case

    calving_law : str
        The calving law used for the test case

    suffixes : list of str, optional
        a list of suffixes for namelist and streams files produced
        for this step.  Most steps most runs will just have a
        ``namelist.landice`` and a ``streams.landice`` (the default) but
        the ``restart_run`` step of the ``restart_test`` runs the model
        twice, the second time with ``namelist.landice.rst`` and
        ``streams.landice.rst``

    mesh_file : str
        The name of the mesh file being used

    forcing_file : str
        The name of the forcing file being used

    """
    def __init__(self, test_case, velo_solver, mesh_type,
                 name='run_model',
                 calving_law=None,
                 damage=None,
                 face_melt=False,
                 subdir=None, ntasks=1,
                 min_tasks=None, openmp_threads=1, suffixes=None):
        """
        Create a new test case

        Parameters
        ----------
        test_case : compass.TestCase
            The test case this step belongs to

        velo_solver : {'sia', 'FO', 'none'}
            The velocity solver setting to use for this test case

        calving_law: str, optional
            The calving law setting to use for this test case. If not
            specified, set to 'none'. Valid values are: 'none',
            'floating', 'eigencalving', 'specified_calving_velocity',
            'von_Mises_stress', 'damagecalving', 'ismip6_retreat'

        damage : str
            The damage method used for the test case

        face_melt : bool
            Whether to include face melting

        mesh_type : {'1km', '3km'}
            The resolution or mesh type of the test case

        name : str, optional
            the name of the test case

        subdir : str, optional
            the subdirectory for the step.  The default is ``name``

        ntasks : int, optional
            the number of tasks the step would ideally use.  If fewer tasks
            are available on the system, the step will run on all available
            tasks as long as this is not below ``min_tasks``

        min_tasks : int, optional
            the number of tasks the step requires.  If the system has fewer
            than this number of tasks, the step will fail

        openmp_threads : int, optional
            the number of OpenMP threads the step will use

        suffixes : list of str, optional
            a list of suffixes for namelist and streams files produced
            for this step.  Most steps most runs will just have a
            ``namelist.landice`` and a ``streams.landice`` (the default) but
            the ``restart_run`` step of the ``restart_test`` runs the model
            twice, the second time with ``namelist.landice.rst`` and
            ``streams.landice.rst``
        """
        self.mesh_type = mesh_type
        self.velo_solver = velo_solver
        assert self.velo_solver in {'sia', 'FO', 'none'}, \
            "Value of velo_solver must be one of {'sia', 'FO', 'none'}"
        if calving_law:
            self.calving_law = calving_law
        else:
            self.calving_law = 'none'
        assert self.calving_law in {'none', 'floating', 'eigencalving',
                                    'specified_calving_velocity',
                                    'von_Mises_stress',
                                    'damagecalving', 'ismip6_retreat'}, \
            "Value of calving_law must be one of {'none', 'floating', " \
            "'eigencalving', 'specified_calving_velocity', " \
            "'von_Mises_stress', 'damagecalving', 'ismip6_retreat'}"
        if damage is not None:
            assert damage in {'threshold', }, \
                "Value of damage must be one of {'threshold', }."

        if suffixes is None:
            suffixes = ['landice']
        self.suffixes = suffixes
        if min_tasks is None:
            min_tasks = ntasks
        super().__init__(test_case=test_case, name=name, subdir=subdir,
                         ntasks=ntasks, min_tasks=min_tasks,
                         openmp_threads=openmp_threads)

        # download and link one of the premade meshes and forcing files
        if self.mesh_type == '1km':
            self.mesh_file = 'Humboldt_1to10km_r04_20210615.nc'
            self.forcing_file = 'Humboldt_1to10km_MIROC5-rcp85_ismip-gis.nc'
        elif self.mesh_type == '3km':
            self.mesh_file = 'Humboldt_3to30km_r04_20210615.nc'
            self.forcing_file = 'Humboldt_3to30km_MIROC5-rcp85_ismip6-gis.nc'
        self.add_input_file(filename=self.mesh_file, target=self.mesh_file,
                            database='')
        self.add_input_file(filename=self.forcing_file,
                            target=self.forcing_file,
                            database='')

        if velo_solver == 'FO':
            self.add_input_file(filename='albany_input.yaml',
                                package='compass.landice.tests.humboldt',
                                copy=True)

        self.add_model_as_input()

        self.add_output_file(filename='output.nc')

        for suffix in suffixes:
            self.add_namelist_file(
                'compass.landice.tests.humboldt', 'namelist.landice',
                out_name='namelist.{}'.format(suffix))
            options = {'config_velocity_solver': "'{}'".format(velo_solver),
                       'config_calving': "'{}'".format(calving_law)}
            # optionally add damage and facemelt options if included
            if damage == 'threshold':
                options['config_calculate_damage'] = '.true.'
                options['config_damage_calving_method'] = "'threshold'"
                options['config_damage_calving_threshold'] = '0.5'
            if face_melt is True:
                options['config_front_mass_bal_grounded'] = "'ismip6'"
                # Assuming that if have this on, this is a 'full physics'
                # run and we want to keep it cheaper to allow it to be run in
                # the full integration suite, so we increase the dt if a
                # 3km run.
                # NOTE: This could lead to confusion!
                if self.mesh_type == '3km':
                    options['config_dt'] = "'0000-06-00_00:00:00'"
            # now add accumulated options to namelist
            self.add_namelist_options(options=options,
                                      out_name='namelist.{}'.format(suffix))

            stream_replacements = {'HUMBOLDT_INPUT_FILE': self.mesh_file,
                                   'HUMBOLDT_FORCING_FILE': self.forcing_file}
            self.add_streams_file(
                'compass.landice.tests.humboldt', 'streams.landice.template',
                out_name='streams.{}'.format(suffix),
                template_replacements=stream_replacements)

    # no setup() is needed

    def run(self):
        """
        Run this step of the test case
        """
        make_graph_file(mesh_filename=self.mesh_file,
                        graph_filename='graph.info')
        for suffix in self.suffixes:
            run_model(step=self, namelist='namelist.{}'.format(suffix),
                      streams='streams.{}'.format(suffix))
