project('test_package', 'c')
add_global_arguments('-Wno-unused-variable', language : 'c')
package_dep = dependency('libdicom')
executable('test_package',
            sources : ['test_package.c'],
            dependencies : [package_dep])
