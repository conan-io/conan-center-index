import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
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
)
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc, msvc_runtime_flag
from conan.tools.scm import Version


required_conan_version = ">=2.0.9"


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
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("tinyxml2/10.0.0")
        self.requires("asio/1.29.0")  # This is now a package_type = header
        self.requires("fast-cdr/2.3.0", transitive_headers=True, transitive_libs=True)
        self.requires("foonathan-memory/0.7.3")
        if self.options.with_ssl:
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        check_min_cppstd(self, 11)
        check_min_vs(self, "192")
        if self.options.shared != self.dependencies["fast-cdr"].options.shared:
            raise ConanInvalidConfiguration(f"{self.name} and fast-cdr should be compiled with same 'shared' option.")
        if self.options.shared and is_msvc(self) and "MT" in msvc_runtime_flag(self):
            # This combination leads to an fast-dds error when linking
            # linking dynamic '*.dll' and static MT runtime
            raise ConanInvalidConfiguration("Mixing a dll {} library with a static runtime is not supported".format(self.name))

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16.3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_MEMORY_TOOLS"] = False
        tc.variables["NO_TLS"] = not self.options.with_ssl
        tc.variables["SECURITY"] = self.options.with_ssl
        tc.variables["EPROSIMA_INSTALLER_MINION"] = False
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.cache_variables["TINYXML2_LIBRARY"] = "tinyxml2::tinyxml2"
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("asio", "cmake_file_name", "Asio")
        deps.set_property("asio", "cmake_target_name", "Asio")
        deps.set_property("tinyxml2", "cmake_file_name", "TinyXML2")
        deps.generate()

    def build(self):
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

        if Version(self.version) < "3.0.0":
            # component fastrtps
            self.cpp_info.components["fastrtps"].set_property("cmake_target_name", "fastrtps")
            self.cpp_info.components["fastrtps"].set_property("cmake_target_aliases", ["fastdds::fastrtps"])
            self.cpp_info.components["fastrtps"].libs = collect_libs(self)
            self.cpp_info.components["fastrtps"].requires = [
                "fast-cdr::fast-cdr",
                "asio::asio",
                "tinyxml2::tinyxml2",
                "foonathan-memory::foonathan-memory",
            ]
            if self.settings.os in ["Linux", "FreeBSD", "Neutrino"]:
                self.cpp_info.components["fastrtps"].system_libs.append("pthread")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["fastrtps"].system_libs.extend(["rt", "dl", "atomic", "m"])
            elif self.settings.os == "Windows":
                self.cpp_info.components["fastrtps"].system_libs.extend(["iphlpapi", "shlwapi", "mswsock", "ws2_32"])
                if self.options.shared:
                    self.cpp_info.components["fastrtps"].defines.append("FASTRTPS_DYN_LINK")
            if self.options.with_ssl:
                self.cpp_info.components["fastrtps"].requires.append("openssl::openssl")

            # component fast-discovery
            # FIXME: actually conan generators don't know how to create an executable imported target
            # TODO: remove this component by the time fastdds v2 is deprecated as it is not needed
            self.cpp_info.components["fast-discovery-server"].set_property("cmake_target_name", "fastdds::fast-discovery-server")
            self.cpp_info.components["fast-discovery-server"].bindirs = ["bin"]
        else:
            self.cpp_info.set_property("cmake_target_name", "fastdds")
            if self.settings.compiler == "msvc":
                version = Version(self.version)
                self.cpp_info.libs = [f"fastdds{'d' if self.settings.build_type == 'Debug' else ''}-{version.major}.{version.minor}"]
            else:
                self.cpp_info.libs = ["fastdds"]

            if self.settings.os in ["Linux", "FreeBSD", "Neutrino"]:
                self.cpp_info.system_libs.append("pthread")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.extend(["rt", "dl", "atomic", "m"])
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs.extend(["iphlpapi", "shlwapi", "mswsock", "ws2_32"])
                if self.options.shared:
                    self.cpp_info.defines.append("FASTRTPS_DYN_LINK")
            elif is_apple_os(self):
                self.cpp_info.frameworks.extend(["CoreFoundation", "IOKit"])

