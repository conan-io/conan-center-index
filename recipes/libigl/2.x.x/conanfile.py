import os
from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, rm, rmdir, patch
from conan.tools.scm import Version
from conan.tools.apple import is_apple_os
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class LibiglConan(ConanFile):
    name = "libigl"
    description = "Simple C++ geometry processing library"
    topics = ("libigl", "geometry", "matrices", "algorithms")
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    homepage = "https://libigl.github.io/"
    license = "MPL-2.0"
    settings = "os", "arch", "compiler", "build_type"
    options = {"header_only": [True, False], "fPIC": [True, False]}
    default_options = {"header_only": True, "fPIC": True}
    generators = "cmake", "cmake_find_package"
    requires = "eigen/3.3.7"
    build_requires = ["cmake/3.24.1"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "6",
            "clang": "3.4",
            "apple-clang": "5.1",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn(
                "{} recipe lacks information about the {} compiler support.".format(
                    self.name, self.settings.compiler
                )
            )
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++{} support. The current compiler {} {} does not support it.".format(
                        self.name,
                        self._minimum_cpp_standard,
                        self.settings.compiler,
                        self.settings.compiler.version,
                    )
                )
        if (
            self.settings.compiler == "Visual Studio"
            and "MT" in self.settings.compiler.runtime
            and not self.options.header_only
        ):
            raise ConanInvalidConfiguration(
                "Visual Studio build with MT runtime is not supported"
            )
        if ("arm" in self.settings.arch or "x86" is self.settings.arch) and (
            Version(self.version) < "2.4.0" or not is_apple_os(self)
        ):
            raise ConanInvalidConfiguration(
                "Not available for arm. Requested arch: {}, os: {}".format(
                    self.settings.arch, self.settings.os
                )
            )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            del self.options.fPIC

    def _patch_sources(self):
        for current_patch in self.conan_data.get("patches", {}).get(self.version, []):
            patch(self, **current_patch)

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder
        )

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self, parallel=False)

            self._cmake.definitions[
                "LIBIGL_USE_STATIC_LIBRARY"
            ] = not self.options.header_only
            self._cmake.definitions["LIBIGL_BUILD_TUTORIALS"] = "OFF"
            self._cmake.definitions["LIBIGL_BUILD_TESTS"] = "OFF"

            if Version(self.version) < "2.4.0":
                self._cmake.definitions["LIBIGL_EXPORT_TARGETS"] = True

                # All these dependencies are needed to build the examples or the tests
                self._cmake.definitions["LIBIGL_BUILD_PYTHON"] = "OFF"

                self._cmake.definitions["LIBIGL_WITH_CGAL"] = False
                self._cmake.definitions["LIBIGL_WITH_COMISO"] = False
                self._cmake.definitions["LIBIGL_WITH_CORK"] = False
                self._cmake.definitions["LIBIGL_WITH_EMBREE"] = False
                self._cmake.definitions["LIBIGL_WITH_MATLAB"] = False
                self._cmake.definitions["LIBIGL_WITH_MOSEK"] = False
                self._cmake.definitions["LIBIGL_WITH_OPENGL"] = False
                self._cmake.definitions["LIBIGL_WITH_OPENGL_GLFW"] = False
                self._cmake.definitions["LIBIGL_WITH_OPENGL_GLFW_IMGUI"] = False
                self._cmake.definitions["LIBIGL_WITH_PNG"] = False
                self._cmake.definitions["LIBIGL_WITH_TETGEN"] = False
                self._cmake.definitions["LIBIGL_WITH_TRIANGLE"] = False
                self._cmake.definitions["LIBIGL_WITH_XML"] = False
                self._cmake.definitions["LIBIGL_WITH_PYTHON"] = "OFF"
                self._cmake.definitions["LIBIGL_WITH_PREDICATES"] = False

            else:
                self._cmake.definitions["LIBIGL_INSTALL"] = True

                self._cmake.definitions["LIBIGL_COPYLEFT_CGAL"] = False
                self._cmake.definitions["LIBIGL_COPYLEFT_COMISO"] = False
                self._cmake.definitions["LIBIGL_EMBREE"] = False
                self._cmake.definitions["LIBIGL_RESTRICTED_MATLAB"] = False
                self._cmake.definitions["LIBIGL_RESTRICTED_MOSEK"] = False
                self._cmake.definitions["LIBIGL_OPENGL"] = False
                self._cmake.definitions["LIBIGL_GLFW"] = False
                self._cmake.definitions["LIBIGL_IMGUI"] = False
                self._cmake.definitions["LIBIGL_PNG"] = False
                self._cmake.definitions["LIBIGL_COPYLEFT_TETGEN"] = False
                self._cmake.definitions["LIBIGL_RESTRICTED_TRIANGLE"] = False
                self._cmake.definitions["LIBIGL_WITH_XML"] = False
                self._cmake.definitions["LIBIGL_PREDICATES"] = False

        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.GPL", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE.MPL2", dst="licenses", src=self._source_subfolder)

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if not self.options.header_only:
            rm(self, "*.c", self.package_folder, recursive=True)
            rm(self, "*.cpp", self.package_folder, recursive=True)

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "libigl"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libigl"
        self.cpp_info.names["cmake_find_package"] = "igl"
        self.cpp_info.names["cmake_find_package_multi"] = "igl"

        self.cpp_info.components["igl_common"].names["cmake_find_package"] = "common"
        self.cpp_info.components["igl_common"].names[
            "cmake_find_package_multi"
        ] = "common"
        self.cpp_info.components["igl_common"].libs = []
        self.cpp_info.components["igl_common"].requires = ["eigen::eigen"]
        if self.settings.os == "Linux":
            self.cpp_info.components["igl_common"].system_libs = ["pthread"]

        self.cpp_info.components["igl_core"].names["cmake_find_package"] = "core"
        self.cpp_info.components["igl_core"].names["cmake_find_package_multi"] = "core"
        self.cpp_info.components["igl_core"].requires = ["igl_common"]
        if not self.options.header_only:
            self.cpp_info.components["igl_core"].libs = ["igl"]
            self.cpp_info.components["igl_core"].defines.append("IGL_STATIC_LIBRARY")
