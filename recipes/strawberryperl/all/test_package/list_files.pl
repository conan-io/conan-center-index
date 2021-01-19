use strict;
use warnings;

use Path::Tiny;

my $dir = path('.');
my $iter = $dir->iterator;
print "Hello Conan!\n";
while (my $file = $iter->()) {
    next if $file->is_dir();
    print "$file\n";
}