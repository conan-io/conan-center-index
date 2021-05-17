from conans import ConanFile, tools, CMake
import os

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

    _source_subfolder = "source_subfolder"

    _cmake = None

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version),
                  self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PYBIND11_INSTALL"] = True
        self._cmake.definitions["PYBIND11_TEST"] = False
        self._cmake.definitions["PYBIND11_CMAKECONFIG_INSTALL_DIR"] = "lib/cmake/pybind11"
        self._cmake.configure()
        return self._cmake

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
