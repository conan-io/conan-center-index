project('test_package', 'c')
package_dep = dependency('numpy')
py = import('python').find_installation(pure: false)
py.extension_module(
    'test_package',
    sources : ['test_package.c'],
    dependencies : [package_dep],
)
