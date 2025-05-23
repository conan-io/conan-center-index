import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    collect_libs,
    copy,
    export_conandata_patches,
    get,
    rename,
    rm,
    rmdir,
    save,
)
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc, msvc_runtime_flag
from conan.tools.scm import Version


required_conan_version = ">=2.0"


class FastDDSConan(ConanFile):
    name = "fast-dds"
    license = "Apache-2.0"
    homepage = "https://fast-dds.docs.eprosima.com/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The most complete OSS DDS implementation for embedded systems."
    topics = ("dds", "middleware", "ipc")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": False,
    }

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "15",
            "apple-clang": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.options["fast-cdr"].shared = self.options.shared
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("asio/[>=1.31.0 <2]")
        self.requires("fast-cdr/2.3.0", transitive_headers=True, transitive_libs=True)
        self.requires("foonathan-memory/0.7.3")
        if self.options.with_ssl:
            self.requires("openssl/[>=1.1 <4]")
        self.requires("tinyxml2/[>=6 <12]")


    def validate(self):
        # fast-dds requires C++11
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, "192")
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

        if self.options.shared and is_msvc(self) and "MT" in msvc_runtime_flag(self):
            # This combination leads to an fast-dds error when linking
            # linking dynamic '*.dll' and static MT runtime
            raise ConanInvalidConfiguration("Mixing a dll {} library with a static runtime is not supported".format(self.name))

    def build_requirements(self):
        if Version(self.version) >= "2.7.0":
            self.tool_requires("cmake/[>=3.16.3 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_MEMORY_TOOLS"] = False
        tc.variables["NO_TLS"] = not self.options.with_ssl
        tc.variables["SECURITY"] = self.options.with_ssl
        tc.variables["EPROSIMA_INSTALLER_MINION"] = False
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rename(
            self,
            os.path.join(self.package_folder, "tools"),
            os.path.join(os.path.join(self.package_folder, "bin", "tools")),
        )
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fastdds")

        self.cpp_info.set_property("cmake_target_aliases", ["fastdds"])
        self.cpp_info.libs = collect_libs(self)

        if self.settings.os in ["Linux", "FreeBSD", "Neutrino"]:
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["rt", "dl", "atomic", "m"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["iphlpapi", "shlwapi", "mswsock", "ws2_32"])
            if self.options.shared:
                self.cpp_info.defines.append("FASTRTPS_DYN_LINK")
