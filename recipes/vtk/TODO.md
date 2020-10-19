

TODO:
1. Upper case VTK package name
2. Debug "_d" the same as VTK default
3. Move libraries sorting to separate method
4. Enable libraries sorting only for gcc
5. Implement "cmake_find_package_multi"
6. Add 2 more defines when building with Qt
7. What default_options should be? (aligned with VTK or conan or fastest build etc?)
8. Do/Why we need "FindVTK.cmake" file?
9. Verify if there should be "vtk-9.0" or "vtk-9.0.1" in "FindVTK.cmake" file
10. Should be:
        exports = ["CMakeLists.txt", "FindVTK.cmake", "patches/**"]
    or
        exports_sources = ["CMakeLists.txt", "FindVTK.cmake", "patches/**"]
11. Do we need to extend library paths?
        self.run("DYLD_LIBRARY_PATH=%s %s" % (os.environ.get('DYLD_LIBRARY_PATH', ''), bin_path), run_environment=True)
        self.run("LD_LIBRARY_PATH=%s %s" % (os.environ.get('LD_LIBRARY_PATH', ''), bin_path), run_environment=True)





NOTES:
1. Oryginal CMakeLists.txt was repalced by zlib/1.2.11/CMakeLists.txt and modified
2. vtknetcdf_snprintf.diff => vtknetcdf_snprintf.patch, vtktiff_mangle.diff => vtktiff_mangle.patch
3. Progress:
    - first round: all necessary files copied and adopted to conan-center structure
    - Didn't try to build package yet!


USEFUL LINKS AND COMMANDS:
https://github.com/conan-io/conan-center-index/blob/master/docs/how_to_add_packages.md

conan config install https://github.com/conan-io/hooks.git -sf hooks -tf hooks
conan config set hooks.conan-center

conan create . vtk/9.0.1@
--- is equivalent to --vv--
$ conan export .
$ conan install vtk/9.0.1@ --build=vtk
# package is created now, use test to test it
$ conan test test_package vtk/9.0.1@


