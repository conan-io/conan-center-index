project('test_package', 'cpp')
package_dep = dependency('foobar')
executable('test_package',
            sources : ['../test_package/test_package.cpp'],
            dependencies : [package_dep],
            bindir: "bin")
