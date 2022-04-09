This will always pull the latest version from the github stable branch,
it is up to you, the package maker, to decide what version to stamp on it.

This also supports the package in "editable" mode,
see 'hack notes' in conanfile.py, def package_info(self)
copied here:

# The next two self.cpp_info lines help 'editable packages' work correctly,
# but, only if you build in a folder called "build"
# I'm not sure how to make this better according to conan design...
# mkdir build
# cd build
# conan install ..
# conan source ..
# conan build ..
# conan editable add .. libsodium/VERSION@USER/CHANNEL
# (where you, the user, choose what version, user, and channel to call it
#
# Then to test the editable package:
# cd .. # back to the recipe folder
# conan test test_package/ libsodium/VERSION@USER/CHANNEL
# --> should show OK
#
