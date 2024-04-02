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


required_conan_version = ">=1.53.0"


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
            "gcc": "10",
            "clang": "3.9",
            "apple-clang": "8",
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
        self.requires("tinyxml2/10.0.0")
        self.requires("asio/1.29.0")  # This is now a package_type = header
        # Fast-DDS < 2.12 uses Fast-CDR 1.x
        if Version(self.version) < "2.12.0":
            self.requires("fast-cdr/1.1.0", transitive_headers=True, transitive_libs=True)
        else:
            self.requires("fast-cdr/2.1.0", transitive_headers=True, transitive_libs=True)
        self.requires("foonathan-memory/0.7.3")
        if self.options.with_ssl:
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
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
            raise ConanInvalidConfiguration("Mixing a dll {} library with a static runtime is a bad idea".format(self.name))

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
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"fastrtps": "fastdds::fastrtps"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fastdds")

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
        self.cpp_info.components["fast-discovery-server"].set_property("cmake_target_name", "fastdds::fast-discovery-server")
        self.cpp_info.components["fast-discovery-server"].bindirs = ["bin"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "fastdds"
        self.cpp_info.names["cmake_find_package_multi"] = "fastdds"
        self.cpp_info.components["fastrtps"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["fastrtps"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["fast-discovery-server"].names["cmake_find_package"] = "fast-discovery-server"
        self.cpp_info.components["fast-discovery-server"].names["cmake_find_package_multi"] = "fast-discovery-server"
