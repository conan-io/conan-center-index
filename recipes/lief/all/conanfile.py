from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.53.0"

class LiefConan(ConanFile):
    name = "lief"
    description = "Library to Instrument Executable Formats"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lief-project/LIEF"
    topics = ("executable", "elf", "pe", "mach-o")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_c_api": [True, False],
        "with_frozen": [True, False],
        "with_json": [True, False],
        "with_art": [True, False],
        "with_dex": [True, False],
        "with_elf": [True, False],
        "with_macho": [True, False],
        "with_oat": [True, False],
        "with_pe": [True, False],
        "with_vdex": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_frozen": True,
        "with_json": True,
        "with_c_api": True,
        "with_art": True,
        "with_dex": True,
        "with_elf": True,
        "with_macho": True,
        "with_oat": True,
        "with_pe": True,
        "with_vdex": True,
    }

    @property
    def _minimum_cpp_standard(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)

        if ((self.info.settings.compiler == "Visual Studio" and Version(self.info.settings.compiler.version) <= "14")
            or
            (self.info.settings.compiler == "msvc" and Version(self.info.settings.compiler.version) <= "190")) \
            and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} does not support Visual Studio <= 14 with shared:True")

        if self.info.settings.compiler.get_safe("libcxx") == "libstdc++":
            raise ConanInvalidConfiguration(f"{self.ref} does not support libstdc++")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) < "0.12.2":
            self.requires("rang/3.2")
        self.requires("mbedtls/3.2.1")
        if self.options.with_json:
            self.requires("nlohmann_json/3.11.2")
        if self.options.with_frozen:
            self.requires("frozen/1.1.1")
        if Version(self.version) >= "0.12.2":
            self.requires("utfcpp/3.2.2")
            # lief doesn't supprot spdlog/1.11.0 with fmt/9.x yet.
            self.requires("spdlog/1.10.0")
            self.requires("boost/1.81.0")
            self.requires("tcb-span/cci.20220616")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIEF_ART"] = self.options.with_art
        tc.variables["LIEF_DEX"] = self.options.with_dex
        tc.variables["LIEF_ELF"] = self.options.with_elf
        tc.variables["LIEF_OAT"] = self.options.with_oat
        tc.variables["LIEF_PE"] = self.options.with_pe
        tc.variables["LIEF_VDEX"] = self.options.with_vdex
        tc.variables["LIEF_MACHO"] = self.options.with_macho
        tc.variables["LIEF_ENABLE_JSON"] = self.options.with_json
        tc.variables["LIEF_DISABLE_FROZEN"] = not self.options.with_frozen
        tc.variables["LIEF_C_API"] = self.options.with_c_api
        tc.variables["LIEF_EXAMPLES"] = False
        tc.variables["LIEF_TESTS"] = False
        tc.variables["LIEF_DOC"] = False
        tc.variables["LIEF_LOGGING"] = False
        tc.variables["LIEF_PYTHON_API"] = False
        if Version(self.version) >= "0.12.2":
            tc.variables["LIEF_USE_CCACHE"] = False
            tc.variables["LIEF_OPT_MBEDTLS_EXTERNAL"] = True
            tc.variables["LIEF_OPT_NLOHMANN_JSON_EXTERNAL"] = True
            tc.variables["LIEF_OPT_FROZEN_EXTERNAL"] = True
            tc.variables["LIEF_OPT_UTFCPP_EXTERNAL"] = True
            tc.variables["LIEF_EXTERNAL_SPDLOG"] = True
            tc.variables["LIEF_OPT_EXTERNAL_LEAF"] = True
            tc.variables["LIEF_OPT_EXTERNAL_SPAN"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["LIEF"]

        self.cpp_info.set_property("cmake_file_name", "LIEF")
        self.cpp_info.set_property("cmake_target_name", "LIEF::LIEF")
        self.cpp_info.set_property("pkg_config_name", "LIEF")

        if self.options.shared:
            self.cpp_info.defines.append("LIEF_IMPORT")
        if is_msvc(self):
            self.cpp_info.cxxflags += ["/FIiso646.h"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.system_libs = ["ws2_32"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "LIEF"
        self.cpp_info.filenames["cmake_find_package_multi"] = "LIEF"
        self.cpp_info.names["cmake_find_package"] = "LIEF"
        self.cpp_info.names["cmake_find_package_multi"] = "LIEF"
        self.cpp_info.names["pkg_config"] = "LIEF"
