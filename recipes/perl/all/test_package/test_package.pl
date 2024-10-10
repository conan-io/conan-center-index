# Basic test to ensure standard library modules are loadable

use File::Basename;

my $dirname = dirname("hello_conan/goodbye_conan");

print($dirname)
