from conans import CMake, ConanFile, tools
import glob
import os
import shutil


class SundialsConan(ConanFile):
    name = "sundials"
    license = "BSD-3-Clause"
    description = ("SUNDIALS is a family of software packages implemented"
                   " with the goal of providing robust time integrators "
                   "and nonlinear solvers that can easily be incorporated"
                   "into existing simulation codes.")
    topics = ("sundials", "integrators", "ode", "non-linear solvers")
    homepage = "https://github.com/LLNL/sundials"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "build_arkode": [True, False],
               "build_cvode": [True, False],
               "build_cvodes": [True, False],
               "build_ida": [True, False],
               "build_idas": [True, False],
               "build_kinsol": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "build_arkode": True,
                       "build_cvode": True,
                       "build_cvodes": True,
                       "build_ida": True,
                       "build_idas": True,
                       "build_kinsol": True}
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    short_paths = True
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        self._cmake.definitions["BUILD_ARKODE"] = self.options.build_arkode
        self._cmake.definitions["BUILD_CVODE"] = self.options.build_cvode
        self._cmake.definitions["BUILD_CVODES"] = self.options.build_cvodes
        self._cmake.definitions["BUILD_IDA"] = self.options.build_ida
        self._cmake.definitions["BUILD_IDAS"] = self.options.build_idas
        self._cmake.definitions["BUILD_KINSOL"] = self.options.build_kinsol
        self._cmake.definitions["EXAMPLES_ENABLE_C"] = False
        self._cmake.definitions["EXAMPLES_INSTALL"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        if self.settings.os == "Windows" and self.options.shared:
            tools.mkdir(os.path.join(self.package_folder, "bin"))
            for dll_path in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
                shutil.move(dll_path, os.path.join(self.package_folder, "bin", os.path.basename(dll_path)))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
