project('test_package', 'c')
package_dep = dependency('numpy')
shared_library('test_package',
               sources : ['test_package.c'],
               dependencies : [package_dep],
               name_prefix: '')
