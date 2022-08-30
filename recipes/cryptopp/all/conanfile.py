from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get, rename, replace_in_file, rmdir, save
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os
import textwrap

required_conan_version = ">=1.47.0"


class CryptoPPConan(ConanFile):
    name = "cryptopp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://cryptopp.com"
    license = "BSL-1.0"
    description = "Crypto++ Library is a free C++ class library of cryptographic schemes."
    topics = ("cryptopp", "crypto", "cryptographic", "security")

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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        if Version(self.version) >= "8.7.0":
            self.tool_requires("cmake/3.21.0")

    def validate(self):
        if self.options.shared and Version(self.version) >= "8.7.0":
            raise ConanInvalidConfiguration("cryptopp 8.7.0 and higher do not support shared builds")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        # Get cryptopp sources
        get(self, **self.conan_data["sources"][self.version]["source"],
            destination=self.source_folder, strip_root=True)

        if Version(self.version) < "8.7.0":
            # Get CMakeLists
            base_source_dir = os.path.join(self.source_folder, os.pardir)
            get(self, **self.conan_data["sources"][self.version]["cmake"], destination=base_source_dir)
            src_folder = os.path.join(
                base_source_dir,
                f"cryptopp-cmake-CRYPTOPP_{self.version.replace('.', '_')}",
            )
            for file in ("CMakeLists.txt", "cryptopp-config.cmake"):
                rename(self, src=os.path.join(src_folder, file), dst=os.path.join(self.source_folder, file))
            rmdir(self, src_folder)
        else:
            # Get cryptopp-cmake sources
            get(self, **self.conan_data["sources"][self.version]["cmake"],
                destination=os.path.join(self.source_folder, "cryptopp-cmake"), strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "8.7.0":
            tc.variables["BUILD_STATIC"] = not self.options.shared
            tc.variables["BUILD_SHARED"] = self.options.shared
            tc.variables["BUILD_TESTING"] = False
            tc.variables["BUILD_DOCUMENTATION"] = False
            tc.variables["USE_INTERMEDIATE_OBJECTS_TARGET"] = False
            if self.settings.os == "Android":
                tc.variables["CRYPTOPP_NATIVE_ARCH"] = True
            if self.settings.os == "Macos" and self.settings.arch == "armv8" and Version(self.version) <= "8.4.0":
                tc.variables["CMAKE_CXX_FLAGS"] = "-march=armv8-a"
            # For msvc shared
            tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
            # Relocatable shared libs on macOS
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        else:
            tc.cache_variables["CRYPTOPP_SOURCES"] = self.source_folder
            tc.cache_variables["CRYPTOPP_BUILD_TESTING"] = False
            tc.cache_variables["CRYPTOPP_BUILD_DOCUMENTATION"] = False
            tc.cache_variables["CRYPTOPP_USE_INTERMEDIATE_OBJECTS_TARGET"] = False
            if self.settings.os == "Android":
                tc.cache_variables["CRYPTOPP_NATIVE_ARCH"] = True
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Use cpu-features.h from Android NDK
        if self.settings.os == "Android":
            android_ndk_home = tools_legacy.get_env("ANDROID_NDK_HOME")
            if android_ndk_home:
                copy(
                    self,
                    "cpu-features.h",
                    src=os.path.join(android_ndk_home, "sources", "android", "cpufeatures"),
                    dst=self.source_folder,
                )
        # Honor fPIC option
        if Version(self.version) < "8.7.0":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                                "SET(CMAKE_POSITION_INDEPENDENT_CODE 1)", "")
        else:
            replace_in_file(self, os.path.join(self.source_folder, "cryptopp-cmake", "cryptopp", "CMakeLists.txt"),
                                "set(CMAKE_POSITION_INDEPENDENT_CODE 1)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        if Version(self.version) < "8.7.0":
            cmake.configure()
        else:
            cmake.configure(build_script_folder="cryptopp-cmake")
        cmake.build()

    def package(self):
        copy(self, "License.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if Version(self.version) >= "8.7.0":
            copy(self, "LICENSE", src=os.path.join(self.source_folder, "cryptopp-cmake"),
                dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "cryptopp-shared": "cryptopp::cryptopp-shared",
                "cryptopp-static": "cryptopp::cryptopp-static"
            }
        )

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
        cmake_target = "cryptopp-shared" if self.options.shared else "cryptopp-static"
        self.cpp_info.set_property("cmake_file_name", "cryptopp")
        self.cpp_info.set_property("cmake_target_name", cmake_target)
        self.cpp_info.set_property("pkg_config_name", "libcryptopp")

        # TODO: back to global scope once cmake_find_package* generators removed
        self.cpp_info.components["libcryptopp"].libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libcryptopp"].system_libs = ["pthread", "m"]
        elif self.settings.os == "SunOS":
            self.cpp_info.components["libcryptopp"].system_libs = ["nsl", "socket"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["libcryptopp"].system_libs = ["ws2_32"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["pkg_config"] = "libcryptopp"
        self.cpp_info.components["libcryptopp"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["libcryptopp"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["libcryptopp"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["libcryptopp"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["libcryptopp"].set_property("cmake_target_name", cmake_target)
        self.cpp_info.components["libcryptopp"].set_property("pkg_config_name", "libcryptopp")
