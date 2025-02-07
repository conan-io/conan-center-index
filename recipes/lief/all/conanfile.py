from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

import os

required_conan_version = ">=2.0"

class LiefConan(ConanFile):
    name = "lief"
    description = "Library to Instrument Executable Formats"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lief-project/LIEF"
    topics = ("executable", "elf", "pe", "mach-o")
    package_type = "library"
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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("mbedtls/3.2.1")

        if Version(self.version) >= "0.15.1":
            self.requires("utfcpp/4.0.5")
        else:
            self.requires("utfcpp/3.2.3")
        # lief doesn't supprot spdlog/1.11.0 with fmt/9.x yet.
        self.requires("spdlog/1.10.0")
        self.requires("boost/1.81.0", transitive_headers=True)
        self.requires("tcb-span/cci.20220616", transitive_headers=True)
        if self.options.with_json:
            self.requires("nlohmann_json/3.11.2")
        if self.options.with_frozen:
            self.requires("frozen/1.1.1")
        if Version(self.version) >= "0.15.1":
            self.requires("tl-expected/1.1.0", transitive_headers=True)

    def validate(self):
        skip_ci_reason = self.conf.get("user.conancenter:skip_ci_build", check_type=str)
        if skip_ci_reason:
            # lief/0.13.1 fails with fmt 8.x and specific versions of msvc 193
            # https://developercommunity.visualstudio.com/t/Internal-compiler-error-compiler-file-m/10376323
            raise ConanInvalidConfiguration(skip_ci_reason)
        if Version(self.version) >= "0.15.1":
            min_cppstd ="17"
        else:
            min_cppstd = "14" if self.options.with_frozen else "11"
        check_min_cppstd(self, min_cppstd)

        if self.settings.compiler.get_safe("libcxx") == "libstdc++":
            raise ConanInvalidConfiguration("libstdc++ is only supported with the C++11 ABI enabled - try with compiler.cppstd=libstdc++11")

    def build_requirements(self):
        if Version(self.version) >= "0.15.1":
            self.tool_requires("cmake/[>=3.24 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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

        tc.variables["LIEF_USE_CCACHE"] = False
        tc.variables["LIEF_OPT_MBEDTLS_EXTERNAL"] = True
        tc.variables["LIEF_OPT_NLOHMANN_JSON_EXTERNAL"] = True
        tc.variables["LIEF_OPT_FROZEN_EXTERNAL"] = True
        tc.variables["LIEF_OPT_UTFCPP_EXTERNAL"] = True
        tc.variables["LIEF_EXTERNAL_SPDLOG"] = True
        tc.variables["LIEF_OPT_EXTERNAL_LEAF"] = True
        tc.variables["LIEF_OPT_EXTERNAL_SPAN"] = True

        tc.variables["LIEF_INSTALL"] = True
        tc.variables["LIEF_EXTERNAL_SPAN_DIR"] = self.dependencies["tcb-span"].cpp_info.includedirs[0].replace("\\", "/")
        tc.variables["LIEF_EXTERNAL_LEAF_DIR"] = self.dependencies["boost"].cpp_info.includedirs[0].replace("\\", "/")

        if Version(self.version) >= "0.15.1":
            tc.cache_variables["LIEF_OPT_EXTERNAL_EXPECTED"] = True

        tc.generate()

        deps = CMakeDeps(self)
        if Version(self.version) >= "0.16.1":
            deps.set_property("utfcpp", "cmake_target_name", "utf8cpp::utf8cpp")
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
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
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

