project('test_package', 'c')
package_dep = dependency('wlroots')
executable('test_package',
            sources : ['test_package.c'],
            dependencies : [package_dep],
            c_args: ['-DWLR_USE_UNSTABLE=1'])
