from compass.mesh.spherical import (
    IcosahedralMeshStep,
    QuasiUniformSphericalMeshStep,
)
from compass.ocean.mesh.cull import CullMeshStep
from compass.ocean.mesh.remap_topography import RemapTopography
from compass.ocean.tests.global_ocean.mesh.arrm10to60 import ARRM10to60BaseMesh
from compass.ocean.tests.global_ocean.mesh.ec30to60 import EC30to60BaseMesh
from compass.ocean.tests.global_ocean.mesh.kuroshio import KuroshioBaseMesh
from compass.ocean.tests.global_ocean.mesh.qu import (
    IcosMeshFromConfigStep,
    QUMeshFromConfigStep,
)
from compass.ocean.tests.global_ocean.mesh.so12to60 import SO12to60BaseMesh
from compass.ocean.tests.global_ocean.mesh.wc14 import WC14BaseMesh
from compass.ocean.tests.global_ocean.metadata import (
    get_author_and_email_from_git,
)
from compass.testcase import TestCase
from compass.validate import compare_variables


class Mesh(TestCase):
    """
    A test case for creating a global MPAS-Ocean mesh

    Attributes
    ----------
    package : str
        The python package for the mesh

    mesh_config_filename : str
        The name of the mesh config file

    with_ice_shelf_cavities : bool
        Whether the mesh includes ice-shelf cavities
    """
    def __init__(self, test_group, mesh_name, remap_topography):
        """
        Create test case for creating a global MPAS-Ocean mesh

        Parameters
        ----------
        test_group : compass.ocean.tests.global_ocean.GlobalOcean
            The global ocean test group that this test case belongs to

        mesh_name : str
            The name of the mesh

        remap_topography : bool
            Whether to remap topography as a separate step (as opposed to in
            MPAS-Ocean init mode)
        """
        name = 'mesh'
        subdir = f'{mesh_name}/{name}'
        super().__init__(test_group=test_group, name=name, subdir=subdir)

        with_ice_shelf_cavities = 'wISC' in mesh_name
        mesh_lower = mesh_name.lower()
        if with_ice_shelf_cavities:
            mesh_lower = mesh_lower.replace('wisc', '')
        if 'icos' in mesh_lower:
            mesh_lower = mesh_lower.replace('icos', 'qu')

        self.package = f'compass.ocean.tests.global_ocean.mesh.{mesh_lower}'
        self.mesh_config_filename = f'{mesh_lower}.cfg'

        self.mesh_name = mesh_name
        self.with_ice_shelf_cavities = with_ice_shelf_cavities

        name = 'base_mesh'
        subdir = None
        if mesh_name in ['Icos240', 'IcoswISC240']:
            base_mesh_step = IcosahedralMeshStep(
                self, name=name, subdir=subdir, cell_width=240)
        elif mesh_name in ['QU240', 'QUwISC240']:
            base_mesh_step = QuasiUniformSphericalMeshStep(
                self, name=name, subdir=subdir, cell_width=240)
        elif mesh_name in ['Icos', 'IcoswISC']:
            base_mesh_step = IcosMeshFromConfigStep(
                self, name=name, subdir=subdir)
        elif mesh_name in ['QU', 'QUwISC']:
            base_mesh_step = QUMeshFromConfigStep(
                self, name=name, subdir=subdir)
        elif mesh_name in ['EC30to60', 'ECwISC30to60']:
            base_mesh_step = EC30to60BaseMesh(self, name=name, subdir=subdir)
        elif mesh_name in ['ARRM10to60', 'ARRMwISC10to60']:
            base_mesh_step = ARRM10to60BaseMesh(self, name=name, subdir=subdir)
        elif mesh_name in ['SO12to60', 'SOwISC12to60']:
            base_mesh_step = SO12to60BaseMesh(self, name=name, subdir=subdir)
        elif mesh_name.startswith('Kuroshio'):
            base_mesh_step = KuroshioBaseMesh(self, name=name, subdir=subdir)
        elif mesh_name in ['WC14', 'WCwISC14']:
            base_mesh_step = WC14BaseMesh(self, name=name, subdir=subdir)
        else:
            raise ValueError(f'Unknown mesh name {mesh_name}')

        self.add_step(base_mesh_step)

        if remap_topography:
            remap_step = RemapTopography(test_case=self,
                                         base_mesh_step=base_mesh_step,
                                         mesh_name=mesh_name)
            self.add_step(remap_step)
        else:
            remap_step = None

        self.add_step(CullMeshStep(
            test_case=self, base_mesh_step=base_mesh_step,
            with_ice_shelf_cavities=self.with_ice_shelf_cavities,
            remap_topography=remap_step))

    def configure(self, config=None):
        """
        Modify the configuration options for this test case

        config : compass.config.CompassConfigParser, optional
            Configuration options to update if not those for this test case
        """
        if config is None:
            config = self.config
        config.add_from_package('compass.mesh', 'mesh.cfg', exception=True)
        # a description of the bathymetry
        if 'remap_topography' in self.steps:
            config.add_from_package('compass.ocean.mesh',
                                    'remap_topography.cfg', exception=True)

        if self.mesh_name.startswith('Kuroshio'):
            # add the config options for all kuroshio meshes
            config.add_from_package(
                'compass.ocean.tests.global_ocean.mesh.kuroshio',
                'kuroshio.cfg', exception=True)
        config.add_from_package(self.package, self.mesh_config_filename,
                                exception=True)
        if self.mesh_name in ['Icos', 'IcoswISC']:
            # add the config options for all kuroshio meshes
            config.add_from_package(
                'compass.ocean.tests.global_ocean.mesh.qu',
                'icos.cfg', exception=True)

        if self.mesh_name in ['QU', 'QUwISC', 'Icos', 'IcoswISC']:
            res = config.getfloat('global_ocean', 'qu_resolution')
            # roughly area of the ocean divided by the area of a cell
            approx_cell_count = int(4e8 / res**2)
            config.set('global_ocean', 'approx_cell_count',
                       f'{approx_cell_count}')

        config.set('spherical_mesh', 'add_mesh_density', 'True')
        config.set('spherical_mesh', 'plot_cell_width', 'True')
        if self.with_ice_shelf_cavities:
            prefix = config.get('global_ocean', 'prefix')
            config.set('global_ocean', 'prefix', f'{prefix}wISC')
            config.set('global_ocean', 'wisc_description',
                       'Includes cavities under the ice shelves around '
                       'Antarctica')

        # a description of the bathymetry
        if 'remap_topography' in self.steps:
            description = config.get('remap_topography', 'description')
        else:
            description = 'Bathymetry is from GEBCO 2022, combined with ' \
                          'BedMachine Antarctica v3 around Antarctica.'

        config.set('global_ocean', 'bathy_description', description)

        get_author_and_email_from_git(config)

    def validate(self):
        """
        Test cases can override this method to perform validation of variables
        and timers
        """
        variables = ['xCell', 'yCell', 'zCell']
        compare_variables(test_case=self, variables=variables,
                          filename1='cull_mesh/culled_mesh.nc')

    def get_cull_mesh_path(self):
        """
        Get the path of the cull mesh step (for input files)
        Returns
        -------
        cull_mesh_path : str
            The path to the work directory of the cull mesh step.
        """
        return self.steps['cull_mesh'].path
