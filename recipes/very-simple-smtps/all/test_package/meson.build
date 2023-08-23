project('test_package', 'cpp')

base_cpp_args = [
  '-std=c++17',
  '-Werror',
  '-Wall',
  '-Wextra',
]

package_dep = dependency('very-simple-smtps')
executable('test_package',
            sources : ['test_package.cpp'],
            dependencies : [package_dep],
            cpp_args : base_cpp_args)
