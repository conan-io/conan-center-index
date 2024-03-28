project('test_package', 'c')

weston_dep = dependency('libweston-' + get_option('weston_version'))
executable('test_package',
            sources : ['test_package.c'],
            dependencies : [weston_dep])
