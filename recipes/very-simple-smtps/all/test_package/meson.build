project('test_package', 'cpp')

base_cpp_args = [
  '-std=c++17',
  '-Werror',
  '-Wall',
  '-Wextra',
  '-fsanitize=address',
]

base_linker_args = [
  '-fsanitize=address',
]

package_dep = dependency('very-simple-smtps')
executable('test_package',
            sources : ['test_package.cpp'],
            dependencies : [package_dep],
            cpp_args : base_cpp_args,
            link_args: base_linker_args)
