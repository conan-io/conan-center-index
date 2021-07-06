from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class VcConan(ConanFile):
    name = "vc"
    description = "SIMD Vector Classes for C++."
    license = "BSD-3-Clause"
    topics = ("vc", "simd", "vectorization", "parallel", "sse", "avx", "neon")
    homepage = "https://github.com/VcDevel/Vc"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmakelists, "CMAKE_SOURCE_DIR", "CMAKE_CURRENT_SOURCE_DIR")
        tools.replace_in_file(cmakelists, "AddCompilerFlag(\"-fPIC\" CXX_FLAGS libvc_compile_flags)", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Vc"
        self.cpp_info.names["cmake_find_package_multi"] = "Vc"
        self.cpp_info.libs = ["Vc"]
