.. _dev_ocean_global_ocean:

global_ocean
============

The ``global_ocean`` test group
(:py:class:`compass.ocean.tests.global_ocean.GlobalOcean`)
creates meshes and initial conditions, and performs testing and dynamic
adjustment for global, realistic ocean domains. It includes 9 test cases on 5
meshes, with the expectation that more meshes from :ref:`legacy_compass` will
be added in the near future.

.. _dev_ocean_global_ocean_framework:

Framework
---------

The shared config options for the ``global_ocean`` test group
are described in :ref:`ocean_global_ocean` in the User's Guide.

Additionally, the test group has several shared namelist and streams files,
some for shared parameters and streams for forward runs (``namelist.forward``
and ``streams.forward``), one specific to meshes with ice-shelf cavities
(``namelist.wisc``), and some related to simulations with biogeochemistry
(``namelist.bgc`` and ``streams.bgc``).

.. _dev_ocean_global_ocean_metadata:

metadata
~~~~~~~~

The module ``compass.ocean.tests.global_ocean.metadata`` determines the values
of a set of metadata related to the E3SM mesh name, initial condition, conda
environment, etc. that are added to nearly all ``global_ocean`` NetCDF output.
See :ref:`global_ocean_metadata` in the User's Guide for more details on
what the metadata looks like.

The values of some of the metadata are given in config options:

.. code-block:: cfg

    # options for global ocean testcases
    [global_ocean]

    ...

    ## metadata related to the mesh
    # whether to add metadata to output files
    add_metadata = True
    # the prefix (e.g. QU, EC, WC, SO)
    prefix = PREFIX
    # a description of the mesh
    mesh_description = <<<Missing>>>
    # a description of the bathymetry
    bathy_description = <<<Missing>>>
    # a description of the mesh with ice-shelf cavities
    init_description = <<<Missing>>>
    # E3SM version that the mesh is intended for
    e3sm_version = 3
    # The revision number of the mesh, which should be incremented each time the
    # mesh is revised
    mesh_revision = <<Missing>>
    # the minimum (finest) resolution in the mesh
    min_res = <<<Missing>>>
    # the maximum (coarsest) resolution in the mesh, can be the same as min_res
    max_res = <<<Missing>>>
    # the maximum depth of the ocean, always detected automatically
    max_depth = autodetect
    # the number of vertical levels, always detected automatically
    levels = autodetect

    # the date the mesh was created as YYMMDD, typically detected automatically
    creation_date = autodetect
    # The following options are detected from .gitconfig if not explicitly entered
    author = autodetect
    email = autodetect
    # The URL of the pull request documenting the creation of the mesh
    pull_request = <<<Missing>>>

Each mesh should define a number of these config options, e.g. ``EC30to60``
defines:

.. code-block:: cfg

    # options for global ocean testcases
    [global_ocean]

    ...

    ## metadata related to the mesh
    # the prefix (e.g. QU, EC, WC, SO)
    prefix = EC
    # a description of the mesh and initial condition
    mesh_description = MPAS Eddy Closure mesh for E3SM version ${e3sm_version} with
                       enhanced resolution around the equator (30 km), South pole
                       (35 km), Greenland (${min_res} km), ${max_res}-km resolution
                       at mid latitudes, and <<<levels>>> vertical levels
    # E3SM version that the mesh is intended for
    e3sm_version = 2
    # The revision number of the mesh, which should be incremented each time the
    # mesh is revised
    mesh_revision = 3
    # the minimum (finest) resolution in the mesh
    min_res = 30
    # the maximum (coarsest) resolution in the mesh, can be the same as min_res
    max_res = 60
    # The URL of the pull request documenting the creation of the mesh
    pull_request = <<<Missing>>>

Note that ``<<<levels>>>`` is a custom placeholder for the number of vertical
levels, since this isn't known until runtime.  There are similar placeholders
for ``<<<creation_date>>>`` and ``<<<bottom_depth>>>`` for similar reasons.

In this particular case, the ``pull_request`` has not yet been defined.  Each
time the mesh is revised, the ``mesh_revision`` should be updated and the
associated pull request to https://github.com/MPAS-Dev/compass/ should be
added here.

The function :py:func:`compass.ocean.tests.global_ocean.metadata.get_e3sm_mesh_names()`
is used to construct the "short" and "long" names of the mesh using a
standard naming convention for E3SM:

.. code-block:: python

    short_mesh_name = f'{mesh_prefix}{res}E{e3sm_version}r{mesh_revision}'
    long_mesh_name = \
        f'{mesh_prefix}{res}kmL{levels}E3SMv{e3sm_version}r{mesh_revision}'

For example, the ``QU240`` mesh has the E3SM short name ``QU240E2r1`` and
long name ``QU240kmL16E3SMv2r1``.

.. _dev_ocean_global_ocean_tasks:

tasks
~~~~~

The function :py:func:`compass.ocean.tests.global_ocean.tasks.get_ntasks_from_cell_count()`
can be used to compute a good number of MPI tasks (both the target and the
minimum) for MPAS-Ocean to use based on the ``goal_cells_per_core`` and
``max_cells_per_core`` config options as well as the number of cells in a mesh.
The idea is that we want to run MPAS-Ocean with about 200 cells per core
(the default value of ``goal_cells_per_core``) but that we would be okay
with as many as 2000 cells per core (the default ``max_cells_per_core``).

A complication of using this function is that the number of cells in a mesh
is not known at setup time, but we do need to know how many cores and nodes
we will use at that time.  So the meshes in ``global_ocean`` have a config
option ``approx_cell_count`` that is used to estimate the number of cells in
the mesh during setup.  Then, the actual number of cells is used at runtime,
when it can be known, to determine the core and node counts for MPAS-Ocean runs
on various meshes.  Some test cases still specify the number of MPI tasks
explicitly because it is part of their testing protocol.



.. _dev_ocean_global_ocean_forward_test:

forward test case
~~~~~~~~~~~~~~~~~

The parent class for test cases in ``global_ocean`` that include running
MPAS-Ocean forward in time is
:py:class:`compass.ocean.tests.global_ocean.forward.ForwardTestCase`.  This
class has attributes ``self.mesh`` and ``self.init`` to keep track of the
:ref:`dev_ocean_global_ocean_mesh` and :ref:`dev_ocean_global_ocean_init` made
the mesh and initial condition that this test case will use.  It also has an
attribute ``self.time_integrator`` to determine whether ``split-explicit`` or
``RK4`` time integration will be used.

In its ``configure()`` method, ``ForwardTestCase`` takes care of config options
by calling :py:meth:`compass.ocean.tests.global_ocean.init.Init.configure()`
to also pick up config options (e.g. metadata) related to the mesh and
initial condition.

In its ``run()`` method, it sets the number of target and minimum number of
cores as well as the number of threads based on config options.  Then, it calls
the base class' ``run()`` method to run its steps.

.. _dev_ocean_global_ocean_forward_step:

forward step
~~~~~~~~~~~~

The parent class for steps in ``global_ocean`` that run MPAS-Ocean forward in
time is :py:class:`compass.ocean.tests.global_ocean.forward.ForwardStep`.
The constructor for ``ForwardStep`` takes several arguments.  At a minimum,
the parent test case and the test cases for the mesh and initial-condition
that will be used for the forward model run are needed, along with the
time integrator (``split-explicit`` or ``RK4``).  Here is an example from the
:ref:`dev_ocean_global_ocean_performance_test`:

.. code-block:: python

    class PerformanceTest(ForwardTestCase):
        """
        A test case for performing a short forward run with an MPAS-Ocean global
        initial condition assess performance and compare with previous results
        """

        def __init__(self, test_group, mesh, init, time_integrator):
            """
            Create test case

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
            super().__init__(test_group=test_group, mesh=mesh, init=init,
                             time_integrator=time_integrator,
                             name='performance_test')

            step = ForwardStep(test_case=self, mesh=mesh, init=init,
                               time_integrator=time_integrator)
            if mesh.with_ice_shelf_cavities:
                module = self.__module__
                step.add_namelist_file(module, 'namelist.wisc')
                step.add_streams_file(module, 'streams.wisc')
                step.add_output_file(filename='land_ice_fluxes.nc')
            self.add_step(step)

As in the example above, these are typically passed along from the arguments
to the the test case's own constructor.

Performance-related parameters---``ntasks``, ``min_tasks``, and
``openmp_threads``---can be passed as optional arguments, but they are more
typically read from the corresponding ``forward_<param>`` config options in the
``global_ocean`` section of the config file.  This lets users update these
values as appropriate if the machine and/or mesh defaults aren't quite right
for them.

There is also a parameter ``get_dt_from_min_res`` that allows the time step
for a given mesh to be determined automatically based on the finest
resolution of the mesh and the ``dt_per_km`` or ``btr_dt_per_km`` config
options.  Unless this parameter is explicitly set to ``False`` (e.g. in
restart tests or dynamic adjustment), the time step will be the product of
the minimum resolution and ``dt_per_km`` for split-explicit runs, and
the barotropic or 4th-order Runge-Kutta time step will be  product of
the minimum resolution and ``btr_dt_per_km``.

During init, the ``forward``, ``wisc`` and ``bgc`` namelist replacements and
streams files are added as appropriate based on whether the mesh includes
ice-shelf cavities and the initial condition includes biogeochemistry. Further
namelist replacements and streams files can be added in the test case
before adding the step, as in the example above.

The MPAS model is linked in as in input to the step in the ``setup()`` method,
which also updates the ``self.ntasks``, ``self.min_tasks`` and
``self.openmp_threads`` attributes from config options if they have not been
set explicitly in the constructor.  Then, in the ``run()`` method, it runs
MPAS-Ocean (including updating PIO namelist options and generating a graph
partition), then :ref:`global_ocean_metadata` is added to the output NetCDF
files.

.. _dev_ocean_global_ocean_testcases:

Test cases
----------

There are 9 ``global_ocean`` test cases.  First, ``mesh`` must be run to
generate and cull the mesh, then one of the variants of ``init`` must be run
to create an initial condition on that mesh.  After that, any of the
regression-focused test cases (``performance_test``, ``restart_test``,
``decomp_test``, ``threads_test``, ``analysis_test``, or ``daily_output_test``)
can be run in any order and as desired.  If an initial condition for E3SM is
desired, the user (or test suite) should first run ``dynamic_adjustment`` and
then ``files_for_e3sm``.

.. _dev_ocean_global_ocean_mesh:

mesh test case
~~~~~~~~~~~~~~

This test case generates an MPAS horizontal mesh, then culls out the land cells
to improve model efficiency.

A :py:class:`compass.ocean.tests.global_ocean.mesh.Mesh` object is constructed
with the ``mesh_name`` as one of its arguments.  Based on this argument, it
determines the appropriate child class of
:py:class:`compass.mesh.spherical.SphericalBaseStep` to create the base mesh
and adds a :py:class:`compass.ocean.mesh.cull.CullMeshStep`.

This class also stores attributes:

``self.mesh_name``
    the name of the mesh

``self.with_ice_shelf_cavities``
    whether the mesh should include ice-shelf cavities

``self.package``
    the module (package) where the config options, namelist and streams files
    specific to the mesh can be found

``self.mesh_config_filename``
    the name of the config file with mesh-specific config options

.. _dev_ocean_global_ocean_meshes:

meshes
^^^^^^

``global_ocean`` currently defines 5 meshes, with more to come.

.. _dev_ocean_global_ocean_qu240:

QU240 and QUwISC240
+++++++++++++++++++

The ``QU240`` mesh is a quasi-uniform mesh with 240-km resolution. The
``QUwISC240`` mesh is identical except that it includes the cavities below ice
shelves in the ocean domain. The mesh is defined by
:py:class:`compass.mesh.QuasiUniformSphericalMeshStep`.  The
``compass.ocean.tests.global_ocean.mesh.qu240`` module includes namelist
options appropriate for forward simulations with both RK4 and split-explicit
time integration on these meshes.  These set the time step and default run
duration for short runs with these meshes.

The default config options for these meshes are:

.. code-block:: cfg

    # Options related to the vertical grid
    [vertical_grid]

    # the type of vertical grid
    grid_type = tanh_dz

    # Number of vertical levels
    vert_levels = 16

    # Depth of the bottom of the ocean
    bottom_depth = 3000.0

    # The minimum layer thickness
    min_layer_thickness = 3.0

    # The maximum layer thickness
    max_layer_thickness = 500.0


    # options for spherical meshes
    [spherical_mesh]

    ## config options related to the step for culling land from the mesh
    # number of cores to use
    cull_mesh_cpus_per_task = 18
    # minimum of cores, below which the step fails
    cull_mesh_min_cpus_per_task = 1
    # maximum memory usage allowed (in MB)
    cull_mesh_max_memory = 1000


    # options for global ocean testcases
    [global_ocean]

    ## config options related to the initial_state step
    # number of cores to use
    init_ntasks = 4
    # minimum of cores, below which the step fails
    init_min_tasks = 1

    # the approximate number of cells in the mesh
    approx_cell_count = 7400

    ## metadata related to the mesh
    # the prefix (e.g. QU, EC, WC, SO)
    prefix = QU
    # a description of the mesh
    mesh_description = MPAS quasi-uniform mesh for E3SM version ${e3sm_version} at
                       ${min_res}-km global resolution with <<<levels>>> vertical
                       level

    # E3SM version that the mesh is intended for
    e3sm_version = 3
    # The revision number of the mesh, which should be incremented each time the
    # mesh is revised
    mesh_revision = 1
    # the minimum (finest) resolution in the mesh
    min_res = 240
    # the maximum (coarsest) resolution in the mesh, can be the same as min_res
    max_res = 240
    # The URL of the pull request documenting the creation of the mesh
    pull_request = <<<Missing>>>

The vertical grid is a ``tanh_dz`` profile (see :ref:`dev_ocean_framework_vertical`)
with 16 vertical levels ranging in thickness from 3 to 500 m.

.. _dev_ocean_global_ocean_isco240:

Icos240 and IcoswISC240
+++++++++++++++++++++++

The ``Icos240`` mesh is a subdivided icosahedral mesh with 240-km resolution
using the :py:class:`compass.mesh.IcosahedralMeshStep` class. The
``IcoswISC240`` mesh is identical except that it includes the cavities below
ice shelves in the ocean domain. Aside from the base mesh, these are identical
to :ref:`dev_ocean_global_ocean_qu240`.

.. _dev_ocean_global_ocean_qu_icos:

QU, QUwISC, Icos and IcoswISC
+++++++++++++++++++++++++++++

The generalized ``QU`` and ``Icos`` meshes are quasi-uniform meshes with
user-defined resolutions (120 km by default). The ``QUwISC`` and ``IcoswISC``
meshes are identical except that they include the cavities below ice shelves in
the ocean domain. The classes
:py:class:`compass.ocean.tests.global_ocean.mesh.qu.QUMeshFromConfigStep` and
:py:class:`compass.ocean.tests.global_ocean.mesh.qu.IcosMeshFromConfigStep`
create the ``QU`` and ``Icos`` base meshes, respectively (with or without
ice-shelf cavities). The ``compass.ocean.tests.global_ocean.mesh.qu``
module includes config and namelist options appropriate for initialization and
forward simulations with split-explicit (but not RK4) time integration on these
meshes.  The number of target and minimum number of MPI tasks, and also the
baroclinic and barotropic time steps are set algorithmically based on the
number of cells in the mesh and its resolution.

The default config options for these meshes are:

.. code-block:: cfg

    # Options related to the vertical grid
    [vertical_grid]

    # the type of vertical grid
    grid_type = index_tanh_dz

    # Number of vertical levels
    vert_levels = 64

    # Depth of the bottom of the ocean
    bottom_depth = 5500.0

    # The minimum layer thickness
    min_layer_thickness = 10.0

    # The maximum layer thickness
    max_layer_thickness = 250.0

    # The characteristic number of levels over which the transition between
    # the min and max occurs
    transition_levels = 28


    # options for global ocean testcases
    [global_ocean]

    ## metadata related to the mesh
    # the prefix (e.g. QU, EC, WC, SO)
    prefix = QU

    # a description of the mesh
    mesh_description = MPAS quasi-uniform mesh for E3SM version ${e3sm_version} at
                       ${min_res}-km global resolution with <<<levels>>> vertical
                       level

    # E3SM version that the mesh is intended for
    e3sm_version = 3
    # The revision number of the mesh, which should be incremented each time the
    # mesh is revised
    mesh_revision = <<<Missing>>>
    # the minimum (finest) resolution in the mesh
    min_res = ${qu_resolution}
    # the maximum (coarsest) resolution in the mesh, can be the same as min_res
    max_res = ${qu_resolution}
    # The URL of the pull request documenting the creation of the mesh
    pull_request = <<<Missing>>>

    # the resolution of the QU or Icos mesh in km
    qu_resolution = 120

The Icos and IcoswISC meshes have these config options that replace the
corresponding QU config options above:

.. code-block:: cfg

    # options for global ocean testcases
    [global_ocean]

    ## metadata related to the mesh
    # the prefix (e.g. QU, EC, WC, SO)
    prefix = Icos

    # a description of the mesh
    mesh_description = MPAS subdivided icosahedral mesh for E3SM version
                       ${e3sm_version} at ${min_res}-km global resolution with
                       <<<levels>>> vertical level

The vertical grid is an ``index_tanh_dz`` profile (see
:ref:`dev_ocean_framework_vertical`) with 64 vertical levels ranging in
thickness from 10 to 250 m.

The resolution of the mesh is controlled by ``qu_resolution``.

.. _dev_ocean_global_ocean_ec30to60:

EC30to60 and ECwISC30to60
+++++++++++++++++++++++++

The ``EC30to60`` mesh is an "eddy-closure" mesh with 30-km resolution at the
equator, 60-km resolution at mid latitudes, and 35-km resolution at the poles.
The mesh resolution is purely a function of latitude. The ``ECwISC30to60`` mesh
is identical except that it includes the cavities below ice shelves in the
ocean domain.

The class
:py:class:`compass.ocean.tests.global_ocean.mesh.ec30to60.EC30to60BaseMesh` defines
the resolution for both meshes. The ``compass.ocean.tests.global_ocean.mesh.ec30to60``
module includes  namelist options appropriate for forward simulations with
split-explicit (but not RK4) time integration on these meshes.  These set the time
step and default run duration for short runs with these meshes.

The default config options for these meshes are:

.. code-block:: cfg

    # Options related to the vertical grid
    [vertical_grid]

    # the type of vertical grid
    grid_type = index_tanh_dz

    # Number of vertical levels
    vert_levels = 64

    # Depth of the bottom of the ocean
    bottom_depth = 5500.0

    # The minimum layer thickness
    min_layer_thickness = 10.0

    # The maximum layer thickness
    max_layer_thickness = 250.0

    # The characteristic number of levels over which the transition between
    # the min and max occurs
    transition_levels = 28


    # options for global ocean testcases
    [global_ocean]

    # the approximate number of cells in the mesh
    approx_cell_count = 240000

    ## metadata related to the mesh
    # the prefix (e.g. QU, EC, WC, SO)
    prefix = EC
    # a description of the mesh and initial condition
    mesh_description = MPAS Eddy Closure mesh for E3SM version ${e3sm_version} with
                       enhanced resolution around the equator (30 km), South pole
                       (35 km), Greenland (${min_res} km), ${max_res}-km resolution
                       at mid latitudes, and <<<levels>>> vertical levels
    # E3SM version that the mesh is intended for
    e3sm_version = 3
    # The revision number of the mesh, which should be incremented each time the
    # mesh is revised
    mesh_revision = 1
    # the minimum (finest) resolution in the mesh
    min_res = 30
    # the maximum (coarsest) resolution in the mesh, can be the same as min_res
    max_res = 60
    # The URL of the pull request documenting the creation of the mesh
    pull_request = <<<Missing>>>

The vertical grid is an ``index_tanh_dz`` profile (see
:ref:`dev_ocean_framework_vertical`) with 64 vertical levels ranging in
thickness from 10 to 250 m.

.. _dev_ocean_global_ocean_kuroshio:

Kuroshio8to60 and Kuroshio12to60
++++++++++++++++++++++++++++++++

The ``Kuroshio8to60`` and ``Kuroshio12to60`` mehses are designed to explore
dynamics of the Western Boundary Current (WBC) in the North Pacific Ocean,
the Kuroshio.

The class
:py:class:`compass.ocean.tests.global_ocean.mesh.kuroshio.KuroshioBaseMesh`
defines the resolution for the meshes, where the finest resolution comes from
the ``min_res`` config option in the ``[global_ocean]`` section of the config
file.

The ``compass.ocean.tests.global_ocean.mesh.kuroshio8to60`` and
``compass.ocean.tests.global_ocean.mesh.kuroshio12to60`` modules include
namelist options appropriate for forward simulations with split-explicit (but
not RK4) time integration on these meshes.  These set the time step and default
run duration for short runs with these meshes.

Except for ``min_res``, default config options for these meshes come from a
shared config file in the ``compass.ocean.tests.global_ocean.mesh.kuroshio``
module:

.. code-block:: cfg

    # options related to the vertical grid
    [vertical_grid]

    # the type of vertical grid
    grid_type = 60layerPHC

    # options for global ocean testcases
    [global_ocean]

    ## metadata related to the mesh
    # the prefix (e.g. QU, EC, WC, SO, Kuroshio)
    prefix = Kuroshio
    # a description of the mesh and initial condition
    mesh_description = MPAS Kuroshio regionally refined mesh for E3SM version
                       ${e3sm_version} with enhanced resolution (${min_res} km) in
                       Kuroshio-Oyashio Extension, 45-km resolution in the mid latitudes,
                       30-km resolution in a 15-degree band around the equator, 60-km
                       resolution in northern mid latitudes, 30 km in the north
                       Atlantic and 35 km in the Arctic.  This mesh has <<<levels>>>
                       vertical levels.
    # E3SM version that the mesh is intended for
    e3sm_version = 3
    # The revision number of the mesh, which should be incremented each time the
    # mesh is revised
    mesh_revision = 1
    # the maximum (coarsest) resolution in the mesh, can be the same as min_res
    max_res = 60
    # the URL of the pull request documenting the creation of the mesh
    pull_request = https://github.com/MPAS-Dev/compass/pull/525

The vertical grid is a ``60layerPHC`` profile (see
:ref:`dev_ocean_framework_vertical`) with 60 vertical levels ranging in
thickness from 10 to 250 m.

.. _dev_ocean_global_ocean_sowisc12to60:

SO12to60 and SOwISC12to60
+++++++++++++++++++++++++

The ``SO12to60`` and ``SOwISC12to60`` meshes are Southern Ocean regionally
refined meshes with 12-km resolution around the Southern Ocean and Antarctica,
45-km at southern mid-latitudes, 30-km at the equator and in the North
Atlantic, 60-km resolution in the North Pacific, and 35-km resolution in the
Arctic.

The class
:py:class:`compass.ocean.tests.global_ocean.mesh.so12to60.SO12to60BaseMesh` defines
the resolution for the meshes. The ``compass.ocean.tests.global_ocean.mesh.so12to60``
module includes namelist options appropriate for forward simulations with
split-explicit (but not RK4) time integration on these meshes.  These set the time
step and default run duration for short runs with these meshes.

The default config options for these meshes are:

.. code-block:: cfg

    # Options related to the vertical grid
    [vertical_grid]

    # the type of vertical grid
    grid_type = index_tanh_dz

    # Number of vertical levels
    vert_levels = 64

    # Depth of the bottom of the ocean
    bottom_depth = 5500.0

    # The minimum layer thickness
    min_layer_thickness = 10.0

    # The maximum layer thickness
    max_layer_thickness = 250.0

    # The characteristic number of levels over which the transition between
    # the min and max occurs
    transition_levels = 28


    # options for global ocean testcases
    [global_ocean]

    # the approximate number of cells in the mesh
    approx_cell_count = 570000

    ## metadata related to the mesh
    # the prefix (e.g. QU, EC, WC, SO)
    prefix = SO
    # a description of the mesh and initial condition
    mesh_description = MPAS Southern Ocean regionally refined mesh for E3SM version
                       ${e3sm_version} with enhanced resolution (${min_res} km) around
                       Antarctica, 45-km resolution in the mid southern latitudes,
                       30-km resolution in a 15-degree band around the equator, 60-km
                       resolution in northern mid latitudes, 30 km in the north
                       Atlantic and 35 km in the Arctic.  This mesh has <<<levels>>>
                       vertical levels and includes cavities under the ice shelves
                       around Antarctica.
    # E3SM version that the mesh is intended for
    e3sm_version = 3
    # The revision number of the mesh, which should be incremented each time the
    # mesh is revised
    mesh_revision = 1
    # the minimum (finest) resolution in the mesh
    min_res = 12
    # the maximum (coarsest) resolution in the mesh, can be the same as min_res
    max_res = 60
    # The URL of the pull request documenting the creation of the mesh
    pull_request = https://github.com/MPAS-Dev/compass/pull/460


    # config options related to initial condition and diagnostics support files
    # for E3SM
    [files_for_e3sm]

    # CMIP6 grid resolution
    cmip6_grid_res = 180x360

The vertical grid is an ``index_tanh_dz`` profile (see
:ref:`dev_ocean_framework_vertical`) with 64 vertical levels ranging in
thickness from 10 to 250 m.

.. _dev_ocean_global_ocean_wc14:

WC14 and WCwISC14
+++++++++++++++++

The ``WC14`` and ``WCwISC14`` meshes are the Water Cycle regionally refined
meshes for E3SM v3.  It has higher resolution (~14-km) around the continental
US, the Arctic Ocean, and a section of the North Atlantic containing the Gulf
Stream. The resolution elsewhere varies between 35 km at the South Pole to 60
km at mid latitudes, with a band of 30-km resolution around the equator.

The class :py:class:`compass.ocean.tests.global_ocean.mesh.wc14.WC14BaseMesh`
defines the resolution for the meshes. The
``compass.ocean.tests.global_ocean.mesh.wc14`` module includes namelist options
appropriate for forward simulations with split-explicit (but not RK4) time
integration on these meshes.  These set the time step and default run duration for
short runs with these meshes.

The default config options for these meshes are:

.. code-block:: cfg

    # Options related to the vertical grid
    [vertical_grid]

    # the type of vertical grid
    grid_type = index_tanh_dz

    # Number of vertical levels
    vert_levels = 64

    # Depth of the bottom of the ocean
    bottom_depth = 5500.0

    # The minimum layer thickness
    min_layer_thickness = 10.0

    # The maximum layer thickness
    max_layer_thickness = 250.0

    # The characteristic number of levels over which the transition between
    # the min and max occurs
    transition_levels = 28


    # options for global ocean testcases
    [global_ocean]

    # the approximate number of cells in the mesh
    approx_cell_count = 410000

    ## metadata related to the mesh
    # the prefix (e.g. QU, EC, WC, SO)
    prefix = WC
    # a description of the mesh and initial condition
    mesh_description = MPAS North America and Arctic Focused Water Cycle mesh for E3SM version
                       ${e3sm_version}, with a focused ${min_res}-km resolution
                       around North America and <<<levels>>> vertical levels

    # E3SM version that the mesh is intended for
    e3sm_version = 3
    # The revision number of the mesh, which should be incremented each time the
    # mesh is revised
    mesh_revision = 1
    # the minimum (finest) resolution in the mesh
    min_res = 14
    # the maximum (coarsest) resolution in the mesh, can be the same as min_res
    max_res = 60
    # The URL of the pull request documenting the creation of the mesh
    pull_request = https://github.com/MPAS-Dev/MPAS-Model/pull/628


    # config options related to initial condition and diagnostics support files
    # for E3SM
    [files_for_e3sm]

    # CMIP6 grid resolution
    cmip6_grid_res = 180x360

The vertical grid is an ``index_tanh_dz`` profile (see
:ref:`dev_ocean_framework_vertical`) with 64 vertical levels ranging in
thickness from 10 to 250 m.

.. _dev_ocean_global_ocean_init:

init test case
~~~~~~~~~~~~~~

The class :py:class:`compass.ocean.tests.global_ocean.init.Init` defines a test
case for creating a global initial condition using MPAS-Ocean's init mode.
Currently there are 3 choices for the potential temperature and salinity
fields used for initialization:

  * the World Ocean Atlas 2023
    (`WOA23 <https://www.ncei.noaa.gov/products/world-ocean-atlas>`_)
    climatology from 1991-2020

  * the Polar science center Hydrographic Climatology
    (`PHC <http://psc.apl.washington.edu/nonwp_projects/PHC/Climatology.html>`_)

  * the UK MetOffice's EN4 estimated climatology for the year 1900
    (`EN4_1900 <https://www.metoffice.gov.uk/hadobs/en4/download-en4-2-0.html>`_).

In its ``configure()`` method, ``Init`` brings in config options related to
the mesh (e.g. metadata) by calling
:py:meth:`compass.ocean.tests.global_ocean.mesh.Mesh.configure()`.

The test case includes 5 namelist replacement files and 3 streams files.
``namelist.init`` and ``streams.init`` modify the namelist options and set up
the streams needed for the test case, regardless of the particular
test group.  ``namelist.woa23``, ``namelist.phc`` and ``namelist.en4_1900`` set
namelist options specific to those 3 sets of input files.  ``namelist.wisc``
and ``streams.wisc`` configure the test case for meshes that include
:ref:`global_ocean_ice_shelf_cavities`, while ``namelist.bgc`` and
``streams.bgc`` are used to configure the test case when
:ref:`global_ocean_bgc` is included.

The class :py:class:`compass.ocean.tests.global_ocean.init.initial_state.InitialState`
defines the step for creating the initial state, including defining the
topography, wind stress, shortwave, potential temperature, salinity, and
ecosystem input data files.

The class :py:class:`compass.ocean.tests.global_ocean.init.ssh_adjustment.SshAdjustment`
defines a step to adjust the ``landIcePressure`` variable to be in closer to
dynamical balance with the sea-surface height (SSH) in configurations with
:ref:`dev_ocean_framework_iceshelf`.

If the test case is being compared with a baseline, the potential temperature,
salinity, and layerThickness are compared with those in the baseline initial
condition to make sure they are identical.  In runs with BGC, a large number
of ecosystem tracers are compared, and in simulations with ice-shelf cavities,
the SSH and land-ice pressure are compared against the baseline.

.. _dev_ocean_global_ocean_performance_test:

performance_test test case
~~~~~~~~~~~~~~~~~~~~~~~~~~

The class :py:class:`compass.ocean.tests.global_ocean.performance_test.PerformanceTest`
defines a test case for performing a short MPAS-Ocean simulation as a "smoke
test" to make sure nothing is clearly wrong with the configuration.

The module includes ``namelist.wisc`` and ``streams.wisc``, which enable melt
fluxes below ice shelves and write out related fields if the mesh includes
:ref:`dev_ocean_framework_iceshelf`.

If a baseline is provided, prognostic variables as well as ecosystem tracers
(if BGC is active) and ice-shelf melt fluxes (if ice-shelf cavities are
included in the mesh) are compared with a baseline, and the
``time integration`` timer is compared with that of the baseline.

.. _dev_ocean_global_ocean_restart_test:

restart_test test case
~~~~~~~~~~~~~~~~~~~~~~

The class :py:class:`compass.ocean.tests.global_ocean.restart_test.RestartTest`
defines a test case for comparing a ``full_run`` of a longer duration with a
``restart_run`` that is made up of two segments if half the duration with a
restart in between. The length of the full and restart runs depends on the time
integrator.  For the ``split-explicit`` integrator, an 8-hour full run is
compared with two 4-hour segments in the restart run.  For the ``RK4``
integrator, the full run is 20 minutes long, while the restart segments are
each 10 minutes.  The test case ensures that the main prognostic
variables---``temperature``, ``salinity``, ``layerThickness`` and
``normalVelocity``---are identical at the end of the two runs (as well as with
a baseline if one is provided when calling :ref:`dev_compass_setup`).

The various steps and time integrators are configured with
``namelist.<time_integrator>.<step>`` and ``streams.<time_integrator>.<step>``
namelist replacements and streams files.

.. _dev_ocean_global_ocean_decomp_test:

decomp_test test case
~~~~~~~~~~~~~~~~~~~~~

The class :py:class:`compass.ocean.tests.global_ocean.decomp_test.DecompTest`
defines a test case that performs a short run once on 4 cores and once on 8
cores.  It ensures that ``temperature``, ``salinity``, ``layerThickness`` and
``normalVelocity`` are identical at the end of the two runs (as well as with a
baseline if one is provided when calling :ref:`dev_compass_setup`).

The duration of the run depends on the mesh and time integrator.  For the
:ref:`dev_ocean_global_ocean_qu240` meshes (the only meshes that this test case
is currently being generated for), the duration is 6 hours for the
``split-explicit`` integrator and 10 minutes for ``RK4``.

.. _dev_ocean_global_ocean_threads_test:

threads_test test case
~~~~~~~~~~~~~~~~~~~~~~

The class :py:class:`compass.ocean.tests.global_ocean.threads_test.ThreadsTest`
defines a test case that performs a short run once on 4 cores, each with 1
thread and once on 4 cores, each with 2 threads.  It ensures that
``temperature``, ``salinity``, ``layerThickness`` and ``normalVelocity`` are
identical at the end of the two runs (as well as with a baseline if one is
provided when calling :ref:`dev_compass_setup`).

The duration of the run depends on the mesh and time integrator.  For the
:ref:`dev_ocean_global_ocean_qu240` meshes (the only meshes that this test case
is currently being generated for), the duration is 6 hours for the
``split-explicit`` integrator and 10 minutes for ``RK4``.

.. _dev_ocean_global_ocean_analysis_test:

analysis_test test case
~~~~~~~~~~~~~~~~~~~~~~~

The class :py:class:`compass.ocean.tests.global_ocean.analysis_test.AnalysisTest`
defines a test case that performs a short run with 14 analysis members (see
:ref:`global_ocean_analysis_test` in the User's Guide). The ``namelist.forward``
and ``streams.forward`` files ensure that the analysis members are enabled and
that the appropriate output is written out.  The test ensures that the
prognostic variables as well as a few variables from each analysis member are
identical to those from the baseline if one is provided when calling
:ref:`dev_compass_setup`.

The duration of the run depends on the mesh and time integrator.  For the
:ref:`dev_ocean_global_ocean_qu240` meshes (the only meshes that this test case
is currently being generated for), the duration is 6 hours for the
``split-explicit`` integrator and 10 minutes for ``RK4``.

.. _dev_ocean_global_ocean_daily_output_test:

daily_output_test test case
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The class :py:class:`compass.ocean.tests.global_ocean.daily_output_test.DailyOutputTest`
defines a test case that performs a 1-day run with the ``timeSeriesStatsDaily``
analysis members (see :ref:`global_ocean_daily_output_test` in the User's
Guide). The ``namelist.forward`` and ``streams.forward`` files ensure that the
analysis member are enabled and that the appropriate output (the E3SM defaults
for the ``timeSeriesStatsMonthly`` analysis member) is written out.  The test
ensures that the time average of the prognostic variables as well as the
sea-surface height are identical to those from the baseline if one is provided
when calling :ref:`dev_compass_setup`.

.. _dev_ocean_global_ocean_dynamic_adjustment:

dynamic_adjustment test case
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The parent class
:py:class:`compass.ocean.tests.global_ocean.dynamic_adjustment.DynamicAdjustment`
descends from :ref:`dev_ocean_global_ocean_forward_test` and defines a test
case for performing a series of forward model runs in sequence to allow the
ocean model to dynamically adjust to the initial condition.  This process
involves a rapid increase in ocean velocity. the dissipation of fast-moving
waves, and adjustment of the sea-surface height to be in balance with the
dynamic pressure (see :ref:`global_ocean_dynamic_adjustment` in the User's
Guide). This process typically require smaller times steps and artificial
friction.

The ``restart_filenames`` attribute keeps track of a sequence of restart files
used in each step of the adjustment process.  The final restart file is used
in the :ref:`dev_ocean_global_ocean_files_for_e3sm`.

The test case also takes care of validating the output from the final
``simulation`` step, comparing ``temperature``, ``salinity``,
``layerThickness``, and ``normalVelocity`` with a baseline if one is provided.

child classes
^^^^^^^^^^^^^

The modules ``compass.ocean.tests.global_ocean.mesh.<mesh_name>.dynamic_adjustment``
define child classes of ``DynamicAdjustment``. Each of the
:ref`global_ocean_meshes` has its own adjustment step, since the needs
(duration of each step, amount of damping, time step, etc.) may be different
between meshes.

Each module includes ``streams.template``, a Jinja2 template for defining
streams (see :ref:`dev_step_add_streams_file_template`):

.. code-block:: xml

    <streams>

    <stream name="output"
            output_interval="{{ output_interval }}"/>
    <immutable_stream name="restart"
                      filename_template="../restarts/rst.$Y-$M-$D_$h.$m.$s.nc"
                      output_interval="{{ restart_interval }}"/>

    </streams>

QU240 and QUwISC240
^^^^^^^^^^^^^^^^^^^

The class :py:class:`compass.ocean.tests.global_ocean.mesh.qu240.dynamic_adjustment.QU240DynamicAdjustment`
defines a test case for performing dynamical adjustment on the mesh.  In the
``damped_adjustment_1`` step, the model is run for 1 day with strong Rayleigh
friction (``1e-4`` 1/s) to damp the velocity field.  In the
``simulation`` step, the model runs for an additional 1 day without Rayleigh
friction.  The dynamic adjustment test case takes advantage of Jinja templating
for streams files to use the same streams template for each step in the test
case, see :ref:`dev_step_add_streams_file_template`.


EC30to60 and ECwISC30to60
^^^^^^^^^^^^^^^^^^^^^^^^^

The class :py:class:`compass.ocean.tests.global_ocean.mesh.ec30to60.dynamic_adjustment.EC30to60DynamicAdjustment`
defines a test case for performing dynamical adjustment on the mesh.  In the
``damped_adjustment_1`` step, the model is run for 10 days with strong Rayleigh
friction (``1e-4`` 1/s) to damp the velocity field.  In the
``simulation`` step, the model runs for an additional 10 days without Rayleigh
friction.  The dynamic adjustment test case takes advantage of Jinja templating
for streams files to use the same streams template for each step in the test
case, see :ref:`dev_step_add_streams_file_template`.

SO12to60 and SOwISC12to60
^^^^^^^^^^^^^^^^^^^^^^^^^

The class :py:class:`compass.ocean.tests.global_ocean.mesh.so12to60.dynamic_adjustment.SO12to60DynamicAdjustment`
defines a test case for performing dynamical adjustment on the mesh.  In the
``damped_adjustment_1`` through ``damped_adjustment_3`` steps, the model is run for
2, 4 and 4 days with gradually weakening Rayleigh friction (``1e-4``, ``4e-5``,
and ``1e-5`` 1/s) to damp the velocity field.  In the ``simulation`` step, the
model runs for an additional 10 days without Rayleigh friction.  The
dynamic adjustment test case takes advantage of Jinja templating for streams
files to use the same streams template for each step in the test case, see
:ref:`dev_step_add_streams_file_template`.

WC14 and WCwISC14
^^^^^^^^^^^^^^^^^

The class :py:class:`compass.ocean.tests.global_ocean.mesh.wc14.dynamic_adjustment.WC14DynamicAdjustment`
defines a test case for performing dynamical adjustment on the mesh.  In the
``damped_adjustment_1`` through ``damped_adjustment_6`` steps, the model is run
for durations ranging from 6 hours to 3 days with gradually increasing time
step and gradually weakening Rayleigh friction (from ``1e-3`` 1/s to ``0``) to
damp the velocity field.  In the ``simulation`` step, the model runs for an
additional 24 days without Rayleigh friction.  The dynamic adjustment test case
takes advantage of Jinja templating for streams files to use the same streams
template for each step in the test case, see
:ref:`dev_step_add_streams_file_template`.

.. _dev_ocean_global_ocean_files_for_e3sm:

files_for_e3sm test case
~~~~~~~~~~~~~~~~~~~~~~~~

After running a :ref:`dev_ocean_global_ocean_dynamic_adjustment`, files can be
prepared for use as E3SM ocean and sea-ice initial conditions using the test
case defined in
:py:class:`compass.ocean.tests.global_ocean.files_for_e3sm.FilesForE3SM`.
Output files from the test case are symlinked in a directory within the test
case called ``assembled_files``. See :ref:`global_ocean_files_for_e3sm` in the
User's Guide for more details.  Output file names involve the "mesh short
name", see :ref:`dev_ocean_global_ocean_metadata`.

The test case is constructed with an argument ``restart_filename``. the final
restart file produced by the :ref:`dev_ocean_global_ocean_dynamic_adjustment`
for the given mesh.

The test case is made up of 10 steps:

:py:class:`compass.ocean.tests.global_ocean.files_for_e3sm.ocean_mesh.OceanMesh`
    uses variables from the ocean initial condition and computes others to
    create an ocean mesh file (with both horizontal and vertical coordinate
    information), creating a symlink
    at ``assembled_files/inputdata/share/meshes/mpas/ocean/<mesh_short_name>.<datestamp>.nc``

:py:class:`compass.ocean.tests.global_ocean.files_for_e3sm.ocean_initial_condition.OceanInitialCondition`
    takes out the ``xtime`` variable from the restart file, creating a symlink
    at ``assembled_files/inputdata/ocn/mpas-o/<mesh_short_name>/mpaso.<mesh_short_name>.<datestamp>.nc``

:py:class:`compass.ocean.tests.global_ocean.files_for_e3sm.ocean_graph_partition.OceanGraphPartition`
    computes graph partitions (see :ref:`dev_model`) appropriate for a wide
    range of core counts between ``min_graph_size = int(nCells / 30000)`` and
    ``max_graph_size = int(nCells / 2)``.  About 400 different processor counts
    are produced for each mesh (keeping only counts with small prime factors).
    Symlinks to the graph files are placed at
    ``assembled_files/inputdata/ocn/mpas-o/<mesh_short_name>/partitions/mpas-o.graph.info.<datestamp>.part.<core_count>``

:py:class:`compass.ocean.tests.global_ocean.files_for_e3sm.seaice_mesh.SeaiceMesh`
    uses variables from the ocean initial condition to create a sea-ice mesh
    file (with horizontal coordinate information), creating a symlink
    at ``assembled_files/inputdata/share/meshes/mpas/sea-ice/<mesh_short_name>.<datestamp>.nc``

:py:class:`compass.ocean.tests.global_ocean.files_for_e3sm.seaice_initial_condition.SeaiceInitialCondition`
    extracts the following variables from the restart file:

    .. code-block:: python

        keep_vars = ['areaCell', 'cellsOnCell', 'edgesOnCell', 'fCell',
                     'indexToCellID', 'latCell', 'lonCell', 'meshDensity',
                     'nEdgesOnCell', 'verticesOnCell', 'xCell', 'yCell', 'zCell',
                     'angleEdge', 'cellsOnEdge', 'dcEdge', 'dvEdge', 'edgesOnEdge',
                     'fEdge', 'indexToEdgeID', 'latEdge', 'lonEdge',
                     'nEdgesOnCell', 'nEdgesOnEdge', 'verticesOnEdge',
                     'weightsOnEdge', 'xEdge', 'yEdge', 'zEdge', 'areaTriangle',
                     'cellsOnVertex', 'edgesOnVertex', 'fVertex',
                     'indexToVertexID', 'kiteAreasOnVertex', 'latVertex',
                     'lonVertex', 'xVertex', 'yVertex', 'zVertex']

        if with_ice_shelf_cavities:
           keep_vars.append('landIceMask')

    A symlink to the resulting file is placed at
    ``assembled_files/inputdata/ocn/mpas-seaice/<mesh_short_name>/mpassi.<mesh_short_name>.<datestamp>.nc``

:py:class:`compass.ocean.tests.global_ocean.files_for_e3sm.seaice_graph_partition.SeaiceGraphPartition`
    computes graph partitions (see :ref:`dev_model`) appropriate for a wide
    range of core counts between ``min_graph_size = int(nCells / 30000)`` and
    ``max_graph_size = int(nCells / 2)``.  The sea-ice graph partitions
    include cells for each processor in both polar and equatorial regions for
    better load balancing.  See `Graph partitioning <http://mpas-dev.github.io/MPAS-Tools/stable/seaice/partition.html>`_
    from the MPAS-Tools documentation for details.  About 400 different
    processor counts are produced for each mesh (keeping only counts with small
    prime factors). Symlinks to the graph files are placed at
    ``assembled_files/inputdata/ice/mpas-seaice/<mesh_short_name>/partitions/mpas-seaice.graph.info.<datestamp>.part.<core_count>``

:py:class:`compass.ocean.tests.global_ocean.files_for_e3sm.scrip.Scrip`
    generates a SCRIP file (see :ref:`global_ocean_files_for_e3sm` in the
    User's guide) describing the MPAS-Ocean mesh.  If ice-shelf cavities are
    included, the step also generates a SCRIP file without the ice-shelf
    cavities for use in coupling components that do not interact with ice-shelf
    cavities (atmosphere, land and sea-ice components).

    Symlinks are placed in ``assembled_files/inputdata/ocn/mpas-o/<mesh_short_name>``
    If ice-shelf cavities are present, the two symlinks are named
    ``ocean.<mesh_short_name>.nomask.scrip.<creation_date>.nc``
    and
    ``ocean.<mesh_short_name>.mask.scrip.<creation_date>.nc``.
    Otherwise, only one file is symlinked, and it is named
    ``ocean.<mesh_short_name>.scrip.<creation_date>.nc``


:py:class:`compass.ocean.tests.global_ocean.files_for_e3sm.e3sm_to_cmip_maps.E3smToCmipMaps`
    creates mapping files for
    `e3sm_to_cmip <https://e3sm-to-cmip.readthedocs.io/en/latest/>`_.

    Mapping files are created from the MPAS-Ocean and -Seaice mesh to a
    standard 1-degree latitude-longitude grid using three methods: `aave`
    (conservative), `mono` (monotonic) and `nco` (NCO's conservative
    algorithm). The mapping files are symlinked in the directory
    ``assembled_files/diagnostics/maps/``.

:py:class:`compass.ocean.tests.global_ocean.files_for_e3sm.diagnostic_maps.DiagnosticMaps`
    creates mapping files for
    `MPAS-Analysis <https://mpas-dev.github.io/MPAS-Analysis/stable/>`_.

    Mapping files are created from the MPAS-Ocean and -Seaice mesh to 7
    standard comparison grids. Mapping files are created from both cells and
    vertices on the MPAS mesh. The vertex maps are needed for quantities like
    the barotropic streamfunction in MPAS-Ocean and ice speed in MPAS-Seaice.
    The mapping files are symlinked in the directory
    ``assembled_files/diagnostics/mpas_analysis/maps/``.

:py:class:`compass.ocean.tests.global_ocean.files_for_e3sm.diagnostic_masks.DiagnosticMasks`
    creates regions masks for E3SM analysis members and
    `MPAS-Analysis <https://mpas-dev.github.io/MPAS-Analysis/stable/>`_.

    Region masks are created using
    :py:func:`geometric_features.aggregation.get_aggregator_by_name()` for
    the following region groups:

    .. code-block:: python

        region_groups = ['Antarctic Regions', 'Arctic Ocean Regions',
                         'Arctic Sea Ice Regions', 'Ocean Basins',
                         'Ocean Subbasins', 'ISMIP6 Regions',
                         'Transport Transects']

    If ice-shelf cavities are present in the mesh, the ``Ice Shelves``
    regions are also included.
    The resulting region masks are symlinked in the directory
    ``assembled_files/diagnostics/mpas_analysis/region_masks/``
    and named ``<mesh_short_name>_<region_group><ref_date>.nc``

    Masks are also created for the meridional overturning circulation (MOC)
    basins and the transects representing their southern boundaries.
    The resulting region mask is in the same directory as above, and named
    ``<mesh_short_name>_moc_masks_and_transects.nc``

files_for_e3sm for an existing mesh
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The test case ``ocean/global_ocean/files_for_e3sm`` can be used to create all the
same files as in :ref:`dev_ocean_global_ocean_files_for_e3sm` but for an
existing mesh.  To point to the existing mesh and associated graph file, the
following config options must be specified (typically by editing
``files_for_e3sm.cfg`` after setting up the test case):

.. code-block:: ini

    # config options related to initial condition and diagnostics support files
    # for E3SM
    [files_for_e3sm]

    # the absolute path or relative path with respect to the test case's work
    # directory of an ocean restart file on the given mesh
    ocean_restart_filename = autodetect

    # the absolute path or relative path with respect to the test case's work
    # directory of a graph file that corresponds to the mesh
    graph_filename = autodetect

The following will be detected from the metadata in the ocean restart file if
present but can be set if needed:

.. code-block:: ini

    # config options related to initial condition and diagnostics support files
    # for E3SM
    [files_for_e3sm]

    # the E3SM short name of the mesh or "autodetect" to use the
    # MPAS_Mesh_Short_Name attribute of the mesh file
    mesh_short_name = autodetect

    # whether the mesh has ice-shelf cavities
    with_ice_shelf_cavities = autodetect
