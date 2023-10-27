from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import collect_libs, copy, get, replace_in_file, rename, rm
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import glob
import os

required_conan_version = ">=1.53.0"


class AeronConan(ConanFile):
    name = "aeron"
    description = "Efficient reliable UDP unicast, UDP multicast, and IPC message transport"
    topics = ("udp", "messaging", "low-latency")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/real-logic/aeron"
    license = "Apache-2.0"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_aeron_driver": [True, False],
        "build_aeron_archive_api": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_aeron_driver": True,
        "build_aeron_archive_api": True,
    }

    @property
    def _min_cppstd(self):
        return "11"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "5",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("This platform (os=Macos arch=armv8) is not yet supported by this recipe")

    def build_requirements(self):
        self.tool_requires("zulu-openjdk/11.0.19")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_AERON_DRIVER"] = self.options.build_aeron_driver
        tc.cache_variables["BUILD_AERON_ARCHIVE_API"] = self.options.build_aeron_archive_api
        tc.cache_variables["AERON_TESTS"] = False
        tc.cache_variables["AERON_SYSTEM_TESTS"] = False
        tc.cache_variables["AERON_SLOW_SYSTEM_TESTS"] = False
        tc.cache_variables["AERON_BUILD_SAMPLES"] = False
        tc.cache_variables["AERON_BUILD_DOCUMENTATION"] = False
        tc.cache_variables["AERON_INSTALL_TARGETS"] = True
        tc.cache_variables["AERON_ENABLE_NONSTANDARD_OPTIMIZATIONS"] = True
        # The finite-math-only optimization has no effect and can cause linking errors
        # when linked against glibc >= 2.31
        tc.blocks["cmake_flags_init"].template += (
            'string(APPEND CMAKE_CXX_FLAGS_INIT " -fno-finite-math-only")\n'
            'string(APPEND CMAKE_C_FLAGS_INIT " -fno-finite-math-only")\n'
        )
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "/MTd", "")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "/MT", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        archive_resources_dir = os.path.join(self.source_folder, "aeron-archive", "src", "main", "resources")
        copy(self, "*", src=archive_resources_dir, dst=os.path.join(self.package_folder, "res"))

        archive_include_dir = os.path.join(self.source_folder, "aeron-archive", "src", "main", "cpp", "client")
        copy(self, "*.h", src=archive_include_dir, dst=os.path.join(self.package_folder, "include", "aeron-archive"))

        lib_folder = os.path.join(self.package_folder, "lib")
        bin_folder = os.path.join(self.package_folder, "bin")
        for dll in glob.glob(os.path.join(lib_folder, "*.dll")):
            rename(self, dll, os.path.join(bin_folder, os.path.basename(dll)))

        if self.options.shared:
            for lib in glob.glob(os.path.join(lib_folder, "*.a")):
                if not lib.endswith(".dll.a"):
                    os.remove(lib)
            rm(self, "*static.lib", lib_folder)
            rm(self, "aeron_client.lib", lib_folder)
        else:
            rm(self, "*.dll", bin_folder)
            rm(self, "*.so*", lib_folder)
            rm(self, "*.dylib", lib_folder)
            rm(self, "*.dll.a", lib_folder)
            rm(self, "*shared.lib", lib_folder)
            rm(self, "aeron.lib", lib_folder)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if is_msvc(self):
            self.cpp_info.defines.append("_ENABLE_EXTENDED_ALIGNED_STORAGE")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["winmm", "wsock32", "ws2_32", "iphlpapi"]
            self.cpp_info.defines.append("HAVE_WSAPOLL")

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
