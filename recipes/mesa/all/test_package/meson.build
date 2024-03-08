project('test_package', 'c')

defines = []
dependencies = []

if get_option('gbm').enabled()
    defines += '-DMESA_TEST_PACKAGE_HAS_GBM'
    gbm_dep = dependency('gbm')
    dependencies += gbm_dep
endif

if get_option('egl').enabled()
    defines += '-DMESA_TEST_PACKAGE_HAS_EGL'
    egl_dep = dependency('mesa-egl')
    dependencies += egl_dep
endif

if get_option('osmesa').enabled()
    defines += '-DMESA_TEST_PACKAGE_HAS_OSMESA'
    osmesa_dep = dependency('osmesa')
    dependencies += osmesa_dep
endif

if host_machine.system() == 'windows'
    opengl32_dep = dependency('mesa-opengl32')
    dependencies += opengl32_dep
endif

executable('test_package',
            c_args : defines,
            sources : ['test_package.c'],
            dependencies : dependencies)
