from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
import os


required_conan_version = ">=1.54.0"


class LibSSHRecipe(ConanFile):
    name = "libssh"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libssh.org/"
    description = "multiplatform C library implementing the SSHv2 protocol on client and server side"
    topics = ("ssh", "shell", "ssh2", "connection")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "crypto_backend": ["openssl", "gcrypt", "mbedtls"],
        "with_symbol_versioning": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "crypto_backend": "openssl",
        "with_symbol_versioning": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_symbol_versioning

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.crypto_backend =="openssl":
            self.requires("openssl/[>=1.1 <4]")
        elif self.options.crypto_backend == "gcrypt":
            self.requires("libgcrypt/1.8.4")
        elif self.options.crypto_backend == "mbedtls":
            self.requires("mbedtls/3.6.0")

    def validate(self):
        if self.options.crypto_backend == "mbedtls" and not self.dependencies["mbedtls"].options.enable_threading:
            raise ConanInvalidConfiguration(f"{self.ref} requires '-o mbedtls/*:enable_threading=True' when using '-o libssh/*:crypto_backend=mbedtls'")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CLIENT_TESTING"] = False
        tc.variables["SERVER_TESTING"] = False
        tc.variables["WITH_EXAMPLES"] = False
        tc.variables["WITH_GCRYPT"] = self.options.crypto_backend == "gcrypt"
        tc.variables["WITH_GSSAPI"] = False
        tc.variables["WITH_MBEDTLS"] = self.options.crypto_backend == "mbedtls"
        tc.variables["WITH_NACL"] = False
        tc.variables["WITH_SYMBOL_VERSIONING"] = self.options.get_safe("with_symbol_versioning", True)
        tc.variables["WITH_ZLIB"] = self.options.with_zlib
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.cache_variables["CMAKE_TRY_COMPILE_CONFIGURATION"] = str(self.settings.build_type)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["ssh"]
        if not self.options.shared:
            self.cpp_info.defines.append("LIBSSH_STATIC=ON")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "iphlpapi"])

        self.cpp_info.set_property("cmake_file_name", "libssh")
        # target and alias names defined at:
        # ssh         https://git.libssh.org/projects/libssh.git/tree/src/CMakeLists.txt?h=libssh-0.10.6#n351
        # ssh::ssh    https://git.libssh.org/projects/libssh.git/tree/src/CMakeLists.txt?h=libssh-0.10.6#n371
        # ssh-static  https://git.libssh.org/projects/libssh.git/tree/src/CMakeLists.txt?h=libssh-0.10.6#n413
        # ssh::static https://git.libssh.org/projects/libssh.git/tree/src/CMakeLists.txt?h=libssh-0.10.6#n428
        self.cpp_info.set_property("cmake_target_name", "ssh::ssh")
        self.cpp_info.set_property(
            "cmake_target_aliases",
            ["ssh"] if self.options.shared else ["ssh", "ssh-static", "ssh::static"],
        )
        # pkg-config defined at https://git.libssh.org/projects/libssh.git/tree/CMakeLists.txt?h=libssh-0.10.6#n124
        self.cpp_info.set_property("pkg_config_name", "libssh")

