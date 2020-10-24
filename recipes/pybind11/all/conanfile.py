from conans import ConanFile, tools, CMake
import os


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

        # Use pybind11's CMakeLists.txt directly. Otherwise,
        # PYBIND11_MASTER_PROJECT is set to FALSE and the installation does not
        # generate pybind11Targets.cmake. Without that the generated package
        # config cannot be used successfully. We want to use the generated
        # package config as this starting in version 2.6.0 onwards defines the
        # pybind11::headers target that is required to make full use of all
        # installed cmake files.
        self._cmake.configure(source_dir=os.path.join(
            self.source_folder, self._source_subfolder))
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        lib_folder = os.path.join(
            self.package_folder, "lib", "cmake", "pybind11")
        os.rename(
            os.path.join(lib_folder, "pybind11Config.cmake"),
            os.path.join(lib_folder, "pybind11Install.cmake"))
        os.unlink(os.path.join(lib_folder, "pybind11ConfigVersion.cmake"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join(
            self.package_folder, "include", "pybind11"))

        cmake_base_path = os.path.join("lib", "cmake", "pybind11")
        self.cpp_info.builddirs = [cmake_base_path]

        def get_path(filename):
            return os.path.join(cmake_base_path, filename)
        self.cpp_info.build_modules = [get_path("FindPythonLibsNew.cmake"),
                                       get_path("pybind11Install.cmake")]
