import os
import glob

from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration


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
        tools.files.get(self, **self.conan_data["sources"][self.version])
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

        # ACADO logs 170.000 lines of warnings, so we disable them
        self._cmake.definitions["CMAKE_C_FLAGS"] = "-w"
        self._cmake.definitions["CMAKE_CXX_FLAGS"] = "-w"

        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.files.patch(self, **patch)

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

        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(self.package_folder, "*.pdb")

    def package_info(self):
        acado_template_paths = os.path.join(self.package_folder, "include", "acado", "code_generation", "templates")
        self.output.info("Setting ACADO_TEMPLATE_PATHS environment variable: {}".format(acado_template_paths))
        self.env_info.ACADO_TEMPLATE_PATHS = acado_template_paths

        if self.options.shared:
            self.cpp_info.libs = ["acado_toolkit_s", "acado_casadi"]
        else:
            self.cpp_info.libs = ["acado_toolkit", "acado_casadi"]

        self.cpp_info.names["cmake_find_package"] = "ACADO"
        self.cpp_info.names["cmake_find_package_multi"] = "ACADO"

        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.build_modules.append(os.path.join("lib", "cmake", "qpoases.cmake"))

        self.cpp_info.includedirs.append(os.path.join("include", "acado"))
        self.cpp_info.includedirs.append(self._qpoases_sources)
        self.cpp_info.includedirs.append(os.path.join(self._qpoases_sources, "INCLUDE"))
        self.cpp_info.includedirs.append(os.path.join(self._qpoases_sources, "SRC"))

    def validate(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            # https://github.com/acado/acado/blob/b4e28f3131f79cadfd1a001e9fff061f361d3a0f/CMakeLists.txt#L77-L80
            raise ConanInvalidConfiguration("Acado does not support shared builds on Windows.")
        if self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration("apple-clang not supported")
        if self.settings.compiler == "clang" and self.settings.compiler.version == "9":
            raise ConanInvalidConfiguration("acado can not be built by Clang 9.")

        # acado requires libstdc++11 for shared builds
        # https://github.com/conan-io/conan-center-index/pull/3967#issuecomment-752985640
        if self.options.shared and self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration("libstdc++11 required")
        if self.options.shared and self.settings.compiler == "gcc" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration("libstdc++11 required")
