project('test_package', 'c')
pipewire_dep = dependency('libpipewire-' + get_option('libpipewire-api-version'))
executable('test_package',
            sources : ['test_package.c'],
            dependencies : [pipewire_dep])
