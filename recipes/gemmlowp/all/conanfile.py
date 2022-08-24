from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.43.0"


class GemmlowpConan(ConanFile):
    name = "gemmlowp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/gemmlowp"
    description = "Low-precision matrix multiplication"
    topics = ("gemm", "matrix")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, {}):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "gemmlowp")
        self.cpp_info.set_property("cmake_target_name", "gemmlowp::gemmlowp")

        self.cpp_info.components["eight_bit_int_gemm"].set_property("cmake_target_name", "gemmlowp::eight_bit_int_gemm")
        self.cpp_info.components["eight_bit_int_gemm"].includedirs.append(os.path.join("include", "gemmlowp"))
        self.cpp_info.components["eight_bit_int_gemm"].libs = ["eight_bit_int_gemm"]
        if self._is_msvc:
            self.cpp_info.components["eight_bit_int_gemm"].defines = ["NOMINMAX"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["eight_bit_int_gemm"].system_libs.extend(["pthread"])
