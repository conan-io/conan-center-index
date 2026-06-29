from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import re

required_conan_version = ">=2.0"


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
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "tbbmalloc": [True, False],
        "tbbproxy": [True, False],
        "tbbbind": [True, False],
        "interprocedural_optimization": [True, False],
        "build_apple_frameworks": [True, False],
    }
    default_options = {
        "tbbmalloc": True,
        "tbbproxy": True,
        "tbbbind": True,
        "interprocedural_optimization": True,
        "build_apple_frameworks": False,
    }

    def config_options(self):
        if self.settings.os == "Windows" and self.settings.arch == "armv8":
            del self.options.tbbproxy

        tbbbind_supported = self.settings.os != "Macos"
        if not tbbbind_supported:
            del self.options.tbbbind
        if self.settings.os == "Android":
            del self.options.interprocedural_optimization
        if not is_apple_os(self):
            del self.options.build_apple_frameworks

    def configure(self):
        if not self.options.tbbmalloc:
            self.options.rm_safe("tbbproxy")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("tbbbind"):
            self.requires("hwloc/2.12.2", options={'shared': True})

    def validate(self):
        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "11.0":
            raise ConanInvalidConfiguration(f"{self.ref} couldn't be built by apple-clang < 11.0")

        if "hwloc" in self.dependencies.direct_host and self.dependencies["hwloc"].package_type != "shared-library":
            raise ConanInvalidConfiguration(f"ontbb requires option hwloc/*:shared=True to be built.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.get_safe("tbbbind"):
            tc.cache_variables["CMAKE_PROJECT_TBB_INCLUDE"] = os.path.join(self.build_folder, "find_hwloc.cmake")
        tc.cache_variables["TBB_TEST"] = False
        tc.cache_variables["TBB_STRICT"] = False
        tc.cache_variables["TBBMALLOC_BUILD"] = self.options.tbbmalloc
        if self.options.get_safe("interprocedural_optimization") is not None:
            tc.cache_variables["TBB_ENABLE_IPO"] = self.options.interprocedural_optimization
        if self.options.get_safe("tbbmalloc"):
            tc.cache_variables["TBBMALLOC_PROXY_BUILD"] = self.options.get_safe("tbbproxy")
        tc.cache_variables["TBB_DISABLE_HWLOC_AUTOMATIC_SEARCH"] = True
        if self.options.get_safe("build_apple_frameworks"):
            tc.cache_variables["TBB_BUILD_APPLE_FRAMEWORKS"] = True

        if self.package_type == "shared-library":
            # already the default in CMakeLists, just being explicit
            tc.cache_variables["BUILD_SHARED_LIBS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("hwloc", "cmake_target_name", "HWLOC::hwloc_2_5")
        deps.generate()

    def build(self):
        if self.options.get_safe("tbbbind"):
            save(self, os.path.join(self.build_folder, "find_hwloc.cmake"), "find_package(hwloc REQUIRED)")
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
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TBB")
        self.cpp_info.set_property("pkg_config_name", "tbb")
        self.cpp_info.set_property("cmake_config_version_compat", "AnyNewerVersion")

        def lib_name(name):
            if self.settings.build_type == "Debug":
                return name + "_debug"
            return name

        # tbb
        tbb = self.cpp_info.components["libtbb"]

        tbb.set_property("cmake_target_name", "TBB::tbb")
        if self.options.get_safe("build_apple_frameworks"):
            tbb.frameworkdirs.append(os.path.join(self.package_folder, "lib"))
            tbb.frameworks.append("tbb")
        else:
            tbb.libs = [lib_name("tbb12" if is_msvc(self) else "tbb")]
        if self.settings.os in ["Linux", "FreeBSD"]:
            tbb.system_libs = ["m", "dl", "rt", "pthread"]

        # tbbmalloc
        if self.options.get_safe("tbbmalloc"):
            tbbmalloc = self.cpp_info.components["tbbmalloc"]

            tbbmalloc.set_property("cmake_target_name", "TBB::tbbmalloc")

            if self.options.get_safe("build_apple_frameworks"):
                tbbmalloc.frameworkdirs.append(os.path.join(self.package_folder, "lib"))
                tbbmalloc.frameworks.append("tbbmalloc")
            else:
                tbbmalloc.libs = [lib_name("tbbmalloc")]

            if self.settings.os in ["Linux", "FreeBSD"]:
                tbbmalloc.system_libs = ["dl", "pthread"]

            # tbbmalloc_proxy
            if self.options.get_safe("tbbproxy"):
                tbbproxy = self.cpp_info.components["tbbmalloc_proxy"]

                tbbproxy.set_property("cmake_target_name", "TBB::tbbmalloc_proxy")

                if self.options.get_safe("build_apple_frameworks"):
                    tbbproxy.frameworkdirs.append(os.path.join(self.package_folder, "lib"))
                    tbbproxy.frameworks.append("tbbmalloc_proxy")
                else:
                    tbbproxy.libs = [lib_name("tbbmalloc_proxy")]

                tbbproxy.requires = ["tbbmalloc"]
                if self.settings.os in ["Linux", "FreeBSD"]:
                    tbbproxy.system_libs = ["m", "dl", "pthread"]
