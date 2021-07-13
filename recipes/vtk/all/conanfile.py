from conans import ConanFile, CMake, tools
import os
import json

class VtkConan(ConanFile):
    name = "vtk"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://vtk.org/"
    description = "VTK is an open-source software system for" \
        "image processing, 3D graphics, volume rendering and visualization."
    topics = ("conan", "vtk", "geometry", "algorithms")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "vtk_smp_implementation": ["Sequential", "OpenMP", "TBB", "STDThread"],
               "vtk_wrap_python": [True, False],
               "vtk_use_cuda": [True, False],
               "vtk_use_mpi": [True, False],
               "vtk_group_enable_qt": ["YES", "WANT", "DONT_WANT", "NO", "DEFAULT"],
               "vtk_group_enable_rendering": ["YES", "WANT", "DONT_WANT", "NO", "DEFAULT"],
               "vtk_group_enable_mpi": ["YES", "WANT", "DONT_WANT", "NO", "DEFAULT"],
               "vtk_group_enable_standalone": ["YES", "WANT", "DONT_WANT", "NO", "DEFAULT"],
               "vtk_group_enable_views": ["YES", "WANT", "DONT_WANT", "NO", "DEFAULT"],
               "vtk_group_enable_web": ["YES", "WANT", "DONT_WANT", "NO", "DEFAULT"],
               "vtk_group_enable_imaging": ["YES", "WANT", "DONT_WANT", "NO", "DEFAULT"],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "vtk_smp_implementation": "Sequential",
                       "vtk_wrap_python": False,
                       "vtk_use_cuda": False,
                       "vtk_use_mpi": False,
                       "vtk_group_enable_imaging": "DEFAULT",
                       "vtk_group_enable_qt": "DEFAULT",
                       "vtk_group_enable_rendering": "WANT",
                       "vtk_group_enable_mpi": "DONT_WANT",
                       "vtk_group_enable_standalone": "WANT",
                       "vtk_group_enable_views": "DEFAULT",
                       "vtk_group_enable_web": "DEFAULT",
                       "fPIC": True}
    generators = "cmake"
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
            self._cmake.definitions["BUILD_TESTING"] = "OFF"
            self._cmake.definitions["VTK_SMP_IMPLEMENTATION_TYPE"] = self.options.vtk_smp_implementation
            self._cmake.definitions["VTK_WRAP_PYTHON"] = self.options.vtk_wrap_python
            self._cmake.definitions["VTK_USE_CUDA"] = self.options.vtk_use_cuda
            self._cmake.definitions["VTK_GROUP_ENABLE_Imaging"] = self.options.vtk_group_enable_imaging
            self._cmake.definitions["VTK_GROUP_ENABLE_Qt"] = self.options.vtk_group_enable_qt
            self._cmake.definitions["VTK_GROUP_ENABLE_Rendering"] = self.options.vtk_group_enable_rendering
            self._cmake.definitions["VTK_GROUP_ENABLE_MPI"] = self.options.vtk_group_enable_mpi
            self._cmake.definitions["VTK_GROUP_ENABLE_StandAlone"] = self.options.vtk_group_enable_standalone
            self._cmake.definitions["VTK_GROUP_ENABLE_Views"] = self.options.vtk_group_enable_views
            self._cmake.definitions["VTK_GROUP_ENABLE_Web"] = self.options.vtk_group_enable_web
            self._cmake.configure(source_folder=self._source_subfolder)

        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def requirements(self):

        if self.options.vtk_group_enable_qt in ["YES", "WANT"]:
            self.requires("qt/5.15.2")

        if self.options.vtk_smp_implementation == "TBB":
            self.requires("TBB")

        if self.options.vtk_use_mpi:
            self.requires("openmpi")

    def package(self):
        self.copy("Copyright.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "vtk"))
        self.copy("modules.json", dst="bin", src=self.build_folder)
    
    def filter_dep(self, dependencies, enabled_pkg):
        ls_dep = []
        for dep in dependencies:
            if dep in enabled_pkg.keys():
                ls_dep.append(enabled_pkg[dep]['alias'])
        return ls_dep

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "VTK"
        self.cpp_info.names["cmake_find_package_multi"] = "VTK"
        lib = [i.split('-')[0] for i in tools.collect_libs(self)]

        pkg_ver = [int(i) for i in self.version.split('.')]
        base_include_dir = os.path.join('include','vtk-%d.%d' % (pkg_ver[0], pkg_ver[1]))

        with open(os.path.join(self.package_folder, "bin", "modules.json")) as reader:
            vtk_modules = json.load(reader)
        
        enabled_pkg = {}
        for name, content in vtk_modules["modules"].items():
            lib_name = content["library_name"]
            if content["enabled"] and lib_name in lib:
                alias = name.split("::")[1]
                enabled_pkg[name] = {"libname": lib_name, 'alias' : alias}
        
        for name, info in enabled_pkg.items():
            content = vtk_modules["modules"][name]
            alias = info['alias']
            lib_name = info['libname']

            self.cpp_info.components[alias].names["cmake_find_package"]  = alias
            self.cpp_info.components[alias].names["cmake_find_package_multi"] = alias
            self.cpp_info.components[alias].libs = ['%s-%d.%d' % ( lib_name, pkg_ver[0], pkg_ver[1])]
            dep = self.filter_dep(content['depends'], enabled_pkg)
            opt_dep = self.filter_dep(content['private_depends'], enabled_pkg)
            self.cpp_info.components[alias].requires.extend(dep)
            self.cpp_info.components[alias].requires.extend(opt_dep)

            incl_dir = {base_include_dir}
            for incl_f in content['headers']:
                p = os.path.dirname(incl_f)
                if len(p) > 1:
                    incl_dir.add(os.path.join(base_include_dir, p))

            if len(incl_dir) != 0:
                for d in incl_dir:
                    self.cpp_info.components[alias].includedirs.append(d)
