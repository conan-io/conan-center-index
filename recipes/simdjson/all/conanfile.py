from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.2 <1.51.0 || >=1.51.2"


class SimdjsonConan(ConanFile):
    name = "simdjson"
    description = "Parsing gigabytes of JSON per second"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lemire/simdjson"
    topics = ("json", "parser", "simd", "format")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threads": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threads": True,
    }

    @property
    def _compilers_minimum_version(self):
        return {
            # In simdjson/2.0.1, several AVX-512 instructions are not support by GCC < 9.0
            "gcc": "8" if Version(self.version) != "2.0.1" else "9",
            "Visual Studio": "16",
            "clang": "6",
            "apple-clang": "9.4",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, "17")

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))
        elif loose_lt_semver(str(self.info.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not fully support.".format(self.name))

        if Version(self.version) >= "2.0.0" and \
            self.info.settings.compiler == "gcc" and \
            Version(self.info.settings.compiler.version).major == "9":
            if self.settings.compiler.get_safe("libcxx") == "libstdc++11":
                raise ConanInvalidConfiguration("{}/{} doesn't support GCC 9 with libstdc++11.".format(self.name, self.version))
            if self.info.settings.build_type == "Debug":
                raise ConanInvalidConfiguration("{}/{} doesn't support GCC 9 with Debug build type.".format(self.name, self.version))

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SIMDJSON_ENABLE_THREADS"] = self.options.threads
        if Version(self.version) < "1.0.0":
            tc.variables["SIMDJSON_BUILD_STATIC"] = not self.options.shared
            tc.variables["SIMDJSON_SANITIZE"] = False
            tc.variables["SIMDJSON_JUST_LIBRARY"] = True
        else:
            tc.variables["SIMDJSON_DEVELOPER_MODE"] = False
        tc.generate()

    def _patch_sources(self):
        if Version(self.version) < "1.0.0":
            simd_flags_file = os.path.join(self.source_folder, "cmake", "simdjson-flags.cmake")
            # Those flags are not set in >=1.0.0 since we disable SIMDJSON_DEVELOPER_MODE
            replace_in_file(self, simd_flags_file, "target_compile_options(simdjson-internal-flags INTERFACE -fPIC)", "")
            replace_in_file(self, simd_flags_file, "-Werror", "")
            replace_in_file(self, simd_flags_file, "/WX", "")
            # Relocatable shared lib on macOS
            replace_in_file(self, simd_flags_file, "set(CMAKE_MACOSX_RPATH OFF)", "")
        else:
            developer_options = os.path.join(self.source_folder, "cmake", "developer-options.cmake")
            # Relocatable shared lib on macOS
            replace_in_file(self, developer_options, "set(CMAKE_MACOSX_RPATH OFF)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "simdjson")
        self.cpp_info.set_property("cmake_target_name", "simdjson::simdjson")
        self.cpp_info.libs = ["simdjson"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        if self.options.threads:
            self.cpp_info.defines = ["SIMDJSON_THREADS_ENABLED=1"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("pthread")
        if self.options.shared:
            self.cpp_info.defines.append("SIMDJSON_USING_LIBRARY=1")
            if is_msvc(self):
                self.cpp_info.defines.append("SIMDJSON_USING_WINDOWS_DYNAMIC_LIBRARY=1")
