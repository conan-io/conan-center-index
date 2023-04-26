from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class CycloneDDSConan(ConanFile):
    name = "cyclonedds"
    license = "EPL-2.0"
    homepage = "https://cyclonedds.io/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Eclipse Cyclone DDS - An implementation"\
                  " of the OMG Data Distribution Service (DDS) specification"
    topics = ("dds", "ipc", "ros", "middleware")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False],
        "with_shm" : [True, False],
        "enable_security" : [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": False,
        "with_shm": False,
        "enable_security": False,
    }

    short_paths = True

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "16",
            "msvc": "192",
            "clang": "7",
            "apple-clang": "10",
        }

    def _has_idlc(self, info=False):
        # don't build idlc when it makes little sense or not supported
        host_os = self.info.settings.os if info else self.settings.os
        return host_os not in ["Android", "iOS", "watchOS", "tvOS", "Neutrino"]

    def export_sources(self):
        copy(self, os.path.join("cmake", "CycloneDDS_idlc.cmake"), self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self,src_folder="src")

    def requirements(self):
        if self.options.with_shm:
            self.requires("iceoryx/2.0.2")
        if self.options.with_ssl:
            self.requires("openssl/1.1.1t")

    def validate(self):
        if self.options.enable_security and not self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} currently do not support"\
                                            "static build and security on")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def _cmake_new_enough(self, required_version):
        try:
            import re
            from io import StringIO
            output = StringIO()
            self.run("cmake --version", output=output)
            m = re.search(r"cmake version (\d+\.\d+\.\d+)", output.getvalue())
            return Version(m.group(1)) >= required_version
        except:
            return False

    def build_requirements(self):
        if not self._cmake_new_enough("3.16"):
            self.tool_requires("cmake/3.25.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_IDLC"] = self._has_idlc()
        tc.variables["BUILD_IDLC_TESTING"] = False
        tc.variables["BUILD_DDSPERF"] = False
        tc.variables["BUILD_IDLC_TESTING"] = False
        # variables which effects build
        tc.variables["ENABLE_SSL"] = self.options.with_ssl
        tc.variables["ENABLE_SHM"] = self.options.with_shm
        tc.variables["ENABLE_SECURITY"] = self.options.enable_security
        tc.generate()

        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "CycloneDDS_idlc.cmake",
                   src=os.path.join(self.source_folder, os.pardir, "cmake"),
                   dst=os.path.join(self.package_folder, self._module_path))
        copy(self, "Generate.cmake",
                   src=os.path.join(self.source_folder, "cmake", "Modules"),
                   dst=os.path.join(self.package_folder, self._module_path))
        if self.settings.os == "Windows" and self.options.shared:
            for p in ("*.pdb", "concrt*.dll", "msvcp*.dll", "vcruntime*.dll"):
                rm(self, p, os.path.join(self.package_folder, "bin"))

    @property
    def _module_path(self):
        return os.path.join("lib", "cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CycloneDDS")
        self.cpp_info.set_property("cmake_target_name", "CycloneDDS::ddsc")
        self.cpp_info.set_property("pkg_config_name", "CycloneDDS")
        # TODO: back to global scope in conan v2
        self.cpp_info.components["CycloneDDS"].libs = ["ddsc"]
        requires = []
        if self.options.with_shm:
            requires.append("iceoryx::iceoryx_binding_c")
        if self.options.with_ssl:
            requires.append("openssl::openssl")
        self.cpp_info.components["CycloneDDS"].requires = requires
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["CycloneDDS"].system_libs = ["dl", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["CycloneDDS"].system_libs = [
                "ws2_32",
                "dbghelp",
                "bcrypt",
                "iphlpapi"
            ]

        # Provide CycloneDDS::idlc target
        build_modules = [
            os.path.join(self._module_path, "CycloneDDS_idlc.cmake"),
            os.path.join(self._module_path, "Generate.cmake"),
        ]
        self.cpp_info.set_property("cmake_build_modules", build_modules)

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "CycloneDDS"
        self.cpp_info.names["cmake_find_package_multi"] = "CycloneDDS"
        self.cpp_info.components["CycloneDDS"].names["cmake_find_package"] = "ddsc"
        self.cpp_info.components["CycloneDDS"].names["cmake_find_package_multi"] = "ddsc"
        self.cpp_info.components["CycloneDDS"].set_property("cmake_target_name", "CycloneDDS::ddsc")
        self.cpp_info.components["CycloneDDS"].set_property("pkg_config_name", "CycloneDDS")
        if self._has_idlc():
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
