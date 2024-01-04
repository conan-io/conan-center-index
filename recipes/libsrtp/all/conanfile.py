from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, replace_in_file, save, rmdir
from conan.tools.scm import Version
import textwrap
import os

required_conan_version = ">=1.53.0"


class LibsrtpRecipe(ConanFile):
    name = "libsrtp"
    description = (
        "This package provides an implementation of the Secure Real-time Transport"
        "Protocol (SRTP), the Universal Security Transform (UST), and a supporting"
        "cryptographic kernel."
    )
    topics = ("srtp",)
    homepage = "https://github.com/cisco/libsrtp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "with_nss": [True, False],
        "with_mbedtls": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": False,
        "with_nss": False,
        "with_mbedtls": False
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

        if self.options.with_nss:
            self.requires("nss3")
            self.requires("nspr")

        if self.options.with_mbedtls:
            self.requires("mbedtls")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_OPENSSL"] = self.options.with_openssl
        tc.variables["TEST_APPS"] = False
        if Version(self.version) < "2.4.0":
            # Relocatable shared libs on Macos
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        if Version(self.version) < "2.5.0":
            replace_in_file(
                self, os.path.join(self.source_folder, "CMakeLists.txt"),
                "install(TARGETS srtp2 DESTINATION lib)",
                (
                    "include(GNUInstallDirs)\n"
                    "install(TARGETS srtp2\n"
                    "RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}\n"
                    "LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}\n"
                    "ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})"
                ),
            )
        else:
            replace_in_file(
                self, os.path.join(self.source_folder, "CMakeLists.txt"),
                "install(TARGETS srtp2 DESTINATION lib\n  EXPORT libSRTPTargets\n)",
                (
                    "include(GNUInstallDirs)\n"
                    "install(TARGETS srtp2\n"
                    "EXPORT libSRTPTargets\n"
                    "RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}\n"
                    "LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}\n"
                    "ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})"
                ),
            )

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

        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_vars_file)
        )

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent("""\
            set(libsrtp_FOUND ${libsrtp_FOUND})
            if(DEFINED libsrtp_INCLUDE_DIR)
                set(libsrtp_INCLUDE_DIR ${libsrtp_INCLUDE_DIR})
            endif()
            if(DEFINED libsrtp_LIBRARIES)
                set(libsrtp_LIBRARIES ${libsrtp_LIBRARIES})
            endif()
        """)
        save(self, module_file, content)

    @property
    def _module_vars_file(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    @property
    def _module_target_file(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", f"libsrtp{Version(self.version).major}")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "libsrtp")
        self.cpp_info.set_property("cmake_target_name", "libsrtp")
        self.cpp_info.set_property("cmake_target_aliases", ["srtp2"])
        self.cpp_info.set_property("cmake_build_modules", [self._module_vars_file])

        self.cpp_info.names["cmake_find_package"] = "libsrtp"
        self.cpp_info.names["cmake_find_package_multi"] = "libsrtp"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_vars_file]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_target_file]

        self.cpp_info.libs = collect_libs(self)

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
