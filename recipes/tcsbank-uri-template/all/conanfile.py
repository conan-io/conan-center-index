import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class TCSBankUriTemplateConan(ConanFile):
    name = "tcsbank-uri-template"
    description = "URI Templates expansion and reverse-matching for C++"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/TinkoffCreditSystems/uri-template"
    topics = ("uri-template", "url-template", "rfc-6570")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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

    def validate(self):
        compiler_name = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version)

        # Exclude compiler.cppstd < 17
        min_req_cppstd = "17"
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, min_req_cppstd)

        # Exclude unsupported compilers
        compilers_required = {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "7.3",
            "clang": "6.0",
            "apple-clang": "10.0",
        }
        if compiler_name in compilers_required and compiler_version < compilers_required[compiler_name]:
            raise ConanInvalidConfiguration(
                f"{self.name} requires a compiler that supports at least C++{min_req_cppstd}. "
                f"{compiler_name} {compiler_version} is not supported."
            )

        # Check stdlib ABI compatibility
        if compiler_name == "gcc" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration(
                f'Using {self.name} with GCC requires "compiler.libcxx=libstdc++11"'
            )
        elif compiler_name == "clang" and self.settings.compiler.libcxx not in ["libstdc++11", "libc++"]:
            raise ConanInvalidConfiguration(
                f'Using {self.name} with Clang requires either "compiler.libcxx=libstdc++11" or "compiler.libcxx=libc++"'
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["URITEMPLATE_BUILD_TESTING"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "uri-template")
        self.cpp_info.set_property("cmake_target_name", "uri-template::uri-template")
        self.cpp_info.set_property("pkg_config_name", "uri-template")
        self.cpp_info.libs = collect_libs(self)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "uri-template"
        self.cpp_info.names["cmake_find_package_multi"] = "uri-template"
