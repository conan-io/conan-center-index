from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os
import functools


required_conan_version = ">=1.33.0"


class PyBind11Conan(ConanFile):
    name = "pybind11"
    description = "Seamless operability between C++11 and Python"
    topics = "conan", "pybind11", "python", "binding"
    homepage = "https://github.com/pybind/pybind11"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    no_copy_source = True


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def validate(self):
        if self.settings.compiler == "apple-clang" and tools.Version(self.settings.compiler.version) >= "11.0":
            raise ConanInvalidConfiguration("OSX support is bugged. Check https://github.com/pybind/pybind11/issues/3081")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PYBIND11_INSTALL"] = True
        cmake.definitions["PYBIND11_TEST"] = False
        cmake.definitions["PYBIND11_CMAKECONFIG_INSTALL_DIR"] = "lib/cmake/pybind11"
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        for filename in ["pybind11Targets.cmake", "pybind11Config.cmake", "pybind11ConfigVersion.cmake"]:
            try:
                os.unlink(os.path.join(self.package_folder, "lib", "cmake", "pybind11", filename))
            except:
                pass
        if tools.Version(self.version) >= "2.6.0":
            tools.replace_in_file(os.path.join(self.package_folder, "lib", "cmake", "pybind11", "pybind11Common.cmake"),
                                  "if(TARGET pybind11::lto)",
                                  "if(FALSE)")
            tools.replace_in_file(os.path.join(self.package_folder, "lib", "cmake", "pybind11", "pybind11Common.cmake"),
                                  "add_library(",
                                  "# add_library(")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        cmake_base_path = os.path.join("lib", "cmake", "pybind11")
        if tools.Version(self.version) >= "2.6.0":
            self.cpp_info.components["main"].names["cmake_find_package"] = "pybind11"
            self.cpp_info.components["main"].builddirs = [cmake_base_path]
            for generator in ["cmake_find_package", "cmake_find_package_multi"]:
                self.cpp_info.components["main"].build_modules[generator].append(os.path.join(cmake_base_path, "pybind11Common.cmake"))
            self.cpp_info.components["headers"].includedirs = [os.path.join("include", "pybind11")]
            self.cpp_info.components["headers"].requires = ["main"]
            self.cpp_info.components["embed"].requires = ["main"]
            self.cpp_info.components["module"].requires = ["main"]
            self.cpp_info.components["python_link_helper"].requires = ["main"]
            self.cpp_info.components["windows_extras"].requires = ["main"]
            self.cpp_info.components["lto"].requires = ["main"]
            self.cpp_info.components["thin_lto"].requires = ["main"]
            self.cpp_info.components["opt_size"].requires = ["main"]
            self.cpp_info.components["python2_no_register"].requires = ["main"]
        else:
            self.cpp_info.includedirs.append(os.path.join(
                self.package_folder, "include", "pybind11"))

            self.cpp_info.builddirs = [cmake_base_path]

            for generator in ["cmake", "cmake_multi", "cmake_find_package", "cmake_find_package_multi"]:
                self.cpp_info.build_modules[generator] = [os.path.join(cmake_base_path, "FindPythonLibsNew.cmake"),
                                                          os.path.join(cmake_base_path, "pybind11Tools.cmake")]
