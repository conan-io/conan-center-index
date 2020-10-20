

TODO:
=============
1. Upper case VTK package name
2. DONE: Debug "_d" the same as VTK default
3. DONE: Move libraries sorting to separate method
4. DONE: Enable libraries sorting only for gcc
5. Implement "cmake_find_package_multi"
6. Add 2 more defines when building with Qt
7. What default_options should be? (aligned with VTK or conan or fastest build etc?)
8. DONE: Do/Why we need "FindVTK.cmake" file? We do not need it
9. DONE: Verify if there should be "vtk-9.0" or "vtk-9.0.1" in "FindVTK.cmake" file
10. DONE: Which is correct?
        exports = ["CMakeLists.txt", "patches/**"]
    or
        exports_sources = ["CMakeLists.txt", "patches/**"]
11. Do we need to extend library paths?
        self.run("DYLD_LIBRARY_PATH=%s %s" % (os.environ.get('DYLD_LIBRARY_PATH', ''), bin_path), run_environment=True)
        self.run("LD_LIBRARY_PATH=%s %s" % (os.environ.get('LD_LIBRARY_PATH', ''), bin_path), run_environment=True)
12. A lot of *.h files are in double and tripple nested subfolders. Should it be like this?
        Using like "#include <afsf/sfdsf/sdfdsfds/sfds/*.h>" wil be highly inconvinient.
        If they are public headers maybe they should be added to self.cpp_info.includedirs?
13. DONE: Licenses are in "c:\.conan\08a57b\1\share\licenses\conanvtk\" while musbe be in "c:\.conan\08a57b\1\licenses\"
14. DONE: Verify Win Release
15. DONE: Verify Win Debug
16. DONE: Shouldn't "exports = ["CMakeLists.txt", "patches/**"]" contain also other files?
17. In recipe there is "self.requires("qt/5.15.1@bincrafters/stable")".
        Shouldn't be range there? (e.g. "self.requires("qt/5.15.*@bincrafters/stable")")




NOTES:
=============
1. Oryginal CMakeLists.txt was repalced by zlib/1.2.11/CMakeLists.txt and modified
2. vtknetcdf_snprintf.diff => vtknetcdf_snprintf.patch, vtktiff_mangle.diff => vtktiff_mangle.patch
4. Include path is "Path is "c:\.conan\08a57b\1\include\vtk-9.0\octree\"
5. Folders from package removed
    - "c:\.conan\08a57b\1\lib\vtk\"    - hierarchy\conanvtk\ a lot of *.txt files. I belive they are not needed
    - "c:\.conan\08a57b\1\lib\cmake\"  -  a lot of *.cmake files - HOOK report errors
5. Progress:
    - Win local Release and Debug Successful including test_package and no errors from conan-center HOOKs


USEFUL LINKS AND COMMANDS:
================================
https://github.com/conan-io/conan-center-index/blob/master/docs/how_to_add_packages.md

conan config install https://github.com/conan-io/hooks.git -sf hooks -tf hooks
conan config set hooks.conan-center

conan create . vtk/9.0.1@
--- is equivalent to --vv--
$ conan export .
$ conan install vtk/9.0.1@ --build=vtk -s build_type=Debug
# package is created now, use test to test it
$ conan test test_package vtk/9.0.1@ -s build_type=Debug


