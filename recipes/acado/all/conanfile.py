import os
import glob

from conans import ConanFile, CMake, tools


class AcadoConan(ConanFile):
    name = "acado"
    description = "ACADO Toolkit is a software environment and algorithm collection for automatic control and dynamic optimization."
    license = "LGPL-3.0"
    topics = ("conan", "acado", "control", "optimization", "mpc")
    homepage = "https://github.com/acado/acado"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "cmake/qpoases.cmake", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "codegen_only": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "codegen_only": True,
    }

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("acado-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["ACADO_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["ACADO_BUILD_STATIC"] = not self.options.shared

        self._cmake.definitions["ACADO_WITH_EXAMPLES"] = False
        self._cmake.definitions["ACADO_WITH_TESTING"] = False
        self._cmake.definitions["ACADO_DEVELOPER"] = False
        self._cmake.definitions["ACADO_INTERNAL"] = False
        self._cmake.definitions["ACADO_BUILD_CGT_ONLY"] = self.options.codegen_only

        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    @property
    def _qpoases_sources(self):
        return os.path.join("lib", "cmake", "qpoases")

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("*", src="lib", dst="lib")
        self.copy("qpoases.cmake", src="cmake", dst="lib/cmake")
        qpoases_sources_from = os.path.join(self.package_folder, "share", "acado", "external_packages", "qpoases")
        self.copy("*", src=qpoases_sources_from, dst=self._qpoases_sources)

        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["acado_toolkit", "acado_casadi"]

        self.cpp_info.names["cmake_find_package"] = "ACADO"
        self.cpp_info.names["cmake_find_package_multi"] = "ACADO"

        self.cpp_info.builddirs.append("cmake")
        self.cpp_info.build_modules.append(os.path.join("lib", "cmake", "qpoases.cmake"))

        self.cpp_info.includedirs.append(os.path.join("include", "acado"))
        self.cpp_info.includedirs.append(self._qpoases_sources)
        self.cpp_info.includedirs.append(os.path.join(self._qpoases_sources, "INCLUDE"))
        self.cpp_info.includedirs.append(os.path.join(self._qpoases_sources, "SRC"))
