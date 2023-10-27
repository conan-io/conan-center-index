import os
import shutil
import textwrap

from conan import ConanFile
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, export_conandata_patches, get, replace_in_file, rmdir, save, download, load
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class CryptoPPPEMConan(ConanFile):
    name = "cryptopp-pem"
    description = ("The PEM Pack is a partial implementation of message encryption "
                   "which allows you to read and write PEM encoded keys and parameters, "
                   "including encrypted private keys.")
    # TODO: Fix license syntax, this is not proper spdx terminology
    license = "DocumentRef-README.md:LicenseRef-Cryptopp-Pem-PublicDomain"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.cryptopp.com/wiki/PEM_Pack"
    topics = ("cryptopp", "crypto", "cryptographic", "security", "PEM")

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

    def requirements(self):
        self.requires(f"cryptopp/{self.version}", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} does not support shared library on Windows.")
            # look at https://github.com/conan-io/conan-center-index/pull/18863#issuecomment-1779940892

    def source(self):
        suffix = f"CRYPTOPP_{self.version.replace('.', '_')}"

        # Get sources
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)

        # Get CMakeLists
        get(self, **self.conan_data["sources"][self.version]["cmake"])
        src_folder = os.path.join(self.source_folder, "cryptopp-cmake-" + suffix)
        shutil.move(os.path.join(src_folder, "CMakeLists.txt"), os.path.join(self.source_folder, "CMakeLists.txt"))
        shutil.move(os.path.join(src_folder, "cryptopp-config.cmake"), os.path.join(self.source_folder, "cryptopp-config.cmake"))
        rmdir(self, src_folder)
        # LICENSE not packaged with release tar
        download(self, "https://raw.githubusercontent.com/noloader/cryptopp-pem/0cfc1a8590f2395cd5b976be0e95e10de9a15a92/README.md",
                 os.path.join(self.source_folder, "LICENSE"),
                 sha256="efa5140027e396a3844f9f48d65e014c9a710939ac02e22d32c33a51e1750eef")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.variables["BUILD_SHARED"] = self.options.shared
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_DOCUMENTATION"] = False
        tc.variables["USE_INTERMEDIATE_OBJECTS_TARGET"] = False
        tc.variables["DISABLE_ASM"] = True
        if self.settings.os == "Android":
            tc.variables["CRYPTOPP_NATIVE_ARCH"] = True
        if is_apple_os(self) and self.settings.arch == "armv8" and Version(self.version) <= "8.4.0":
            tc.variables["CMAKE_CXX_FLAGS"] = "-march=armv8-a"
        tc.generate()

        # cryptopp-pem expects cryptopp headers to be without a cryptopp/ prefix
        cryptopp_info = self.dependencies["cryptopp"].cpp_info.components["libcryptopp"]
        cryptopp_info.includedirs.append(os.path.join(self.dependencies["cryptopp"].package_folder, "include", "cryptopp"))
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        if self.settings.os == "Android" and "ANDROID_NDK_HOME" in os.environ:
            shutil.copyfile(
                os.path.join(os.environ.get("ANDROID_NDK_HOME"), "sources", "android", "cpufeatures", "cpu-features.h"),
                os.path.join(self.source_folder, "cpu-features.h"))
        apply_conandata_patches(self)
        # Honor fPIC option
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "SET(CMAKE_POSITION_INDEPENDENT_CODE 1)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _extract_license(self):
        readme = load(self, os.path.join(self.source_folder, "LICENSE"),)
        return readme[readme.find("## License"):]

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "cryptopp-pem-shared": "cryptopp-pem::cryptopp-pem-shared",
                "cryptopp-pem-static": "cryptopp-pem::cryptopp-pem-static"
            }
        )
        fix_apple_shared_install_name(self)

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        cmake_target = "cryptopp-pem-shared" if self.options.shared else "cryptopp-pem-static"
        self.cpp_info.set_property("cmake_target_aliases", [cmake_target])
        self.cpp_info.set_property("pkg_config_name", "libcryptopp-pem")

        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["libcryptopp-pem"].libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libcryptopp-pem"].system_libs = ["pthread", "m"]
        elif self.settings.os == "SunOS":
            self.cpp_info.components["libcryptopp-pem"].system_libs = ["nsl", "socket"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["libcryptopp-pem"].system_libs = ["ws2_32"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.components["libcryptopp-pem"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["libcryptopp-pem"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["libcryptopp-pem"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["libcryptopp-pem"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["libcryptopp-pem"].set_property("cmake_target_name", cmake_target)
        self.cpp_info.components["libcryptopp-pem"].set_property("pkg_config_name", "libcryptopp-pem")

        self.cpp_info.components["libcryptopp-pem"].requires = ["cryptopp::cryptopp"]
