from compass.testcase import TestCase
from compass.ocean.tests.hurricane.mesh.dequ120at30cr10rr2 \
    import DEQU120at30cr10rr2BaseMesh
from compass.ocean.tests.hurricane.configure import configure_hurricane
from compass.ocean.mesh.cull import CullMeshStep


class Mesh(TestCase):
    """
    A test case for creating a global MPAS-Ocean mesh
    """
    def __init__(self, test_group, mesh_name):
        """
        Create test case for creating a global MPAS-Ocean mesh

        Parameters
        ----------
        test_group : compass.ocean.tests.hurricane.Hurricane
            The test group that this test case belongs to

        mesh_name : str
            The name of the mesh
        """
        self.mesh_name = mesh_name
        name = 'mesh'
        subdir = '{}/{}'.format(mesh_name, name)
        super().__init__(test_group=test_group, name=name, subdir=subdir)

        name = 'base_mesh'
        if mesh_name == 'DEQU120at30cr10rr2':
            base_mesh_step = DEQU120at30cr10rr2BaseMesh(
                self, name=name, preserve_floodplain=False)
            mesh_lower = 'dequ120at30cr10rr2'
        elif mesh_name == 'DEQU120at30cr10rr2WD':
            base_mesh_step = DEQU120at30cr10rr2BaseMesh(
                self, name=name, preserve_floodplain=True)
            mesh_lower = 'dequ120at30cr10rr2'
        else:
            raise ValueError(f'Unexpected mesh name {mesh_name}')

        self.package = f'compass.ocean.tests.hurricane.mesh.{mesh_lower}'
        self.mesh_config_filename = f'{mesh_lower}.cfg'

        self.add_step(base_mesh_step)

        self.add_step(CullMeshStep(
            test_case=self, base_mesh_step=base_mesh_step,
            with_ice_shelf_cavities=False, do_inject_bathymetry=True,
            preserve_floodplain=True))

    def configure(self):
        """
        Modify the configuration options for this test case
        """
        configure_hurricane(test_case=self, mesh=self)
