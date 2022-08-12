import functools
import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class OpenSubdivConan(ConanFile):
    name = "opensubdiv"
    license = "LicenseRef-LICENSE.txt"
    homepage = "https://github.com/PixarAnimationStudios/OpenSubdiv"
    url = "https://github.com/conan-io/conan-center-index"
    description = "An Open-Source subdivision surface library"
    topics = ("cgi", "vfx", "animation", "subdivision surface")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "with_tbb": [True, False],
        "with_opengl": [True, False],
        "with_omp": [True, False],
        "with_cuda": [True, False],
        "with_clew": [True, False],
        "with_opencl": [True, False],
        "with_dx": [True, False],
        "with_metal": [True, False],
    }
    default_options = {
        "shared": False,
        "with_tbb": False,
        "with_opengl": False,
        "with_omp": False,
        "with_cuda": False,
        "with_clew": False,
        "with_opencl": False,
        "with_dx": False,
        "with_metal": False,
    }

    short_paths = True
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _minimum_cpp_standard(self):
        if self.options.get_safe("with_metal"):
            return 14
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "11",
            "apple-clang": "11.0",
        }

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def config_options(self):
        if self.settings.os != "Windows":
            del self.options.with_dx
        if self.settings.os != "Macos":
            del self.options.with_metal

    def configure(self):
        if self.settings.os == "Windows":
            del self.options.shared

    def requirements(self):
        if self.options.with_tbb:
            self.requires("onetbb/2020.3")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++{} support. The current compiler {} {} does not support it.".format(self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version)
                )

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    @property
    def _osd_gpu_enabled(self):
        return any(
            [
                self.options.with_opengl,
                self.options.with_opencl,
                self.options.with_cuda,
                self.options.get_safe("with_dx"),
                self.options.get_safe("with_metal"),
            ]
        )

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["NO_TBB"] = not self.options.with_tbb
        cmake.definitions["NO_OPENGL"] = not self.options.with_opengl
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.get_safe("shared")
        cmake.definitions["NO_OMP"] = not self.options.with_omp
        cmake.definitions["NO_CUDA"] = not self.options.with_cuda
        cmake.definitions["NO_DX"] = not self.options.get_safe("with_dx")
        cmake.definitions["NO_METAL"] = not self.options.get_safe("with_metal")
        cmake.definitions["NO_CLEW"] = not self.options.with_clew
        cmake.definitions["NO_OPENCL"] = not self.options.with_opencl
        cmake.definitions["NO_PTEX"] = True  # Note: PTEX is for examples only, but we skip them..
        cmake.definitions["NO_DOC"] = True
        cmake.definitions["NO_EXAMPLES"] = True
        cmake.definitions["NO_TUTORIALS"] = True
        cmake.definitions["NO_REGRESSION"] = True
        cmake.definitions["NO_TESTS"] = True
        cmake.definitions["NO_GLTESTS"] = True

        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def build(self):
        if self.settings.os == "Macos":
            path = os.path.join(self._source_subfolder, "opensubdiv", "CMakeLists.txt")
            tools.replace_in_file(path, "${CMAKE_SOURCE_DIR}/opensubdiv", "${CMAKE_SOURCE_DIR}/source_subfolder/opensubdiv")
            if not self._osd_gpu_enabled:
                tools.replace_in_file(path, "$<TARGET_OBJECTS:osd_gpu_obj>", "")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenSubdiv")

        self.cpp_info.names["cmake_find_package"] = "OpenSubdiv"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenSubdiv"

        self.cpp_info.components["osdcpu"].libs = ["osdCPU"]
        self.cpp_info.components["osdcpu"].set_property("cmake_target_name", "OpenSubdiv::osdcpu")

        if self.options.with_tbb:
            self.cpp_info.components["osdcpu"].requires = ["onetbb::onetbb"]

        if self._osd_gpu_enabled:
            self.cpp_info.components["osdgpu"].libs = ["osdGPU"]
            self.cpp_info.components["osdgpu"].set_property("cmake_target_name", "OpenSubdiv::osdgpu")
            dl_required = self.options.with_opengl or self.options.with_opencl
            if self.settings.os in ["Linux", "FreeBSD"] and dl_required:
                self.cpp_info.components["osdgpu"].system_libs = ["dl"]
