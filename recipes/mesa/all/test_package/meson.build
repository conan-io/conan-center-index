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
    if get_option('glvnd').disabled()
        egl_dep = dependency('egl')
    else
        egl_dep = dependency('mesa-egl')
    endif
    dependencies += egl_dep
endif

if get_option('opengl').enabled()
    defines += '-DMESA_TEST_PACKAGE_HAS_OPENGL'
    opengl_dep = dependency('opengl')
    dependencies += opengl_dep
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
