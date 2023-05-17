from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, load, rmdir
from conan.tools.scm import Version
import os
import re

required_conan_version = ">=1.53.0"


class OneTBBConan(ConanFile):
    name = "onetbb"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oneapi-src/oneTBB"
    description = (
        "oneAPI Threading Building Blocks (oneTBB) lets you easily write parallel C++"
        " programs that take full advantage of multicore performance, that are portable, composable"
        " and have future-proof scalability.")
    topics = ("tbb", "threading", "parallelism", "tbbmalloc")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tbbmalloc": [True, False],
        "tbbproxy": [True, False],
        "interprocedural_optimization": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "tbbmalloc": False,
        "tbbproxy": False,
        "interprocedural_optimization": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not (Version(self.version) >= "2021.6.0" and self.options.shared and self.settings.os != "Android"):
            del self.options.interprocedural_optimization
        if Version(self.version) < "2021.2.0":
            del self.options.shared
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.get_safe("shared", True):
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if Version(self.version) < "2021.6.0":
            del self.info.options.tbbmalloc
            del self.info.options.tbbproxy

    def validate(self):
        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "11.0":
            raise ConanInvalidConfiguration(f"{self.ref} couldn't be built by apple-clang < 11.0")
        if not self.options.get_safe("shared", True):
            if Version(self.version) >= "2021.6.0":
                raise ConanInvalidConfiguration(
                    "Building oneTBB as a static library is highly discouraged and not supported "
                    "to avoid unforeseen issues like https://github.com/oneapi-src/oneTBB/issues/920. "
                    "Please consider fixing at least the aforementioned issue in upstream."
                )
            self.output.warning("oneTBB strongly discourages usage of static linkage")
        if self.options.tbbproxy and not (self.options.tbbmalloc and self.options.get_safe("shared", True)):
            raise ConanInvalidConfiguration("tbbproxy needs tbbmalloc and shared options")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["TBB_TEST"] = False
        toolchain.variables["TBB_STRICT"] = False
        if Version(self.version) >= "2021.6.0":
            toolchain.variables["TBBMALLOC_BUILD"] = self.options.tbbmalloc
            toolchain.variables["TBBMALLOC_PROXY_BUILD"] = self.options.tbbproxy
            toolchain.variables["TBB_ENABLE_IPO"] = self.options.get_safe("interprocedural_optimization", False)
        toolchain.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TBB")
        self.cpp_info.set_property("pkg_config_name", "tbb")

        def lib_name(name):
            if self.settings.build_type == "Debug":
                return name + "_debug"
            return name

        # tbb
        tbb = self.cpp_info.components["libtbb"]

        tbb.set_property("cmake_target_name", "TBB::tbb")
        tbb.libs = [lib_name("tbb")]
        if self.settings.os == "Windows":
            version_info = load(self,
                os.path.join(self.package_folder, "include", "oneapi", "tbb",
                             "version.h"))
            binary_version = re.sub(
                r".*" + re.escape("#define __TBB_BINARY_VERSION ") +
                r"(\d+).*",
                r"\1",
                version_info,
                flags=re.MULTILINE | re.DOTALL,
            )
            tbb.libs.append(lib_name(f"tbb{binary_version}"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            tbb.system_libs = ["m", "dl", "rt", "pthread"]

        # tbbmalloc
        if self.options.tbbmalloc:
            tbbmalloc = self.cpp_info.components["tbbmalloc"]

            tbbmalloc.set_property("cmake_target_name", "TBB::tbbmalloc")
            tbbmalloc.libs = [lib_name("tbbmalloc")]
            if self.settings.os in ["Linux", "FreeBSD"]:
                tbbmalloc.system_libs = ["dl", "pthread"]

            # tbbmalloc_proxy
            if self.options.tbbproxy:
                tbbproxy = self.cpp_info.components["tbbmalloc_proxy"]

                tbbproxy.set_property("cmake_target_name", "TBB::tbbmalloc_proxy")
                tbbproxy.libs = [lib_name("tbbmalloc_proxy")]
                tbbproxy.requires = ["tbbmalloc"]
                if self.settings.os in ["Linux", "FreeBSD"]:
                    tbbproxy.system_libs = ["m", "dl", "pthread"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "TBB"
        self.cpp_info.names["cmake_find_package_multi"] = "TBB"
        self.cpp_info.names["pkg_config"] = "tbb"
        tbb.names["cmake_find_package"] = "tbb"
        tbb.names["cmake_find_package_multi"] = "tbb"
