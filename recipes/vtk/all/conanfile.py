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
               "build_testing": ["ON", "OFF", "WANT"],
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
                       "build_testing": "OFF",
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
    version = "9.0.1"

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
        if self.version is None:
            self.version = "9.0.1"
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
            self._cmake.definitions["BUILD_TESTING"] = self.options.build_testing
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
        if self.options.vtk_group_enable_rendering in ["YES", "WANT", "DEFAULT"]:
            self.requires("opengl/system")

        if self.options.vtk_group_enable_qt in ["YES", "WANT", "DEFAULT"]:
            self.requires("qt/5.15.2")

        if self.options.vtk_smp_implementation == "TBB":
            self.requires("TBB/[>2020]")

        if self.options.vtk_use_mpi:
            self.requires("openmpi/[>4]")

    def package(self):
        self.copy("Copyright.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "vtk"))
        self.copy("modules.json", dst="bin", src=self.build_folder)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "VTK"
        self.cpp_info.names["cmake_find_package_multi"] = "VTK"

        libs = tools.collect_libs(self)
        with open(os.path.join(self.package_folder, "bin", "modules.json")) as reader:
            vtk_modules = json.load(reader)

        for name, content in vtk_modules["modules"].items():
            if content["enabled"]:
                lib_name = content["library_name"]
                self.cpp_info.components[name].libs = [lib_name]

                for dep in content['depends']:
                    self.cpp_info.components[name].requires.append(dep)

                for dep in content['private_depends']:
                    self.cpp_info.components[name].requires.append(dep)

                incl_dir = set()
                for incl_f in content['headers']:
                    p = incl_f.split('/')
                    if len(p) > 1:
                        incl_dir.add(os.path.join(*p[0:-1]))

                if len(incl_dir) != 0:
                    for d in incl_dir:
                        self.cpp_info.components[name].includedirs.append(d)
