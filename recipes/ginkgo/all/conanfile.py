from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    rmdir,
)
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class GinkgoConan(ConanFile):
    name = "ginkgo"
    license = "BSD-3-Clause"
    homepage = "https://github.com/ginkgo-project/ginkgo"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "High-performance linear algebra library for manycore systems, with a "
        "focus on sparse solution of linear systems."
    )
    topics = ("hpc", "linear-algebra")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "openmp": [True, False],
        "cuda": [True, False],
        "half": [True, False],
        "bfloat16": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": False,
        "openmp": False,
        "cuda": False,
        "half": True,
        "bfloat16": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        is_mingw = self.settings.os == "Windows" and self.settings.compiler == "gcc"
        if Version(self.version) < "1.9.0" or is_mingw or is_msvc(self):
            # option was added in 1.9.0
            # option not supported for msvc/mingw (build system forces it to OFF anyway)
            # see https://github.com/ginkgo-project/ginkgo/blob/d7e1450b6ba9ee90dbaa839f4b4b5a5ad59e28cc/CMakeLists.txt#L46-L51
            del self.options.half
            # option was added in 1.10.0
            # same reason to force it of as for half
            del self.options.bfloat16

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        min_cppstd = "17" if Version(self.version) >= "1.9.0" else "14"
        check_min_cppstd(self, min_cppstd)

        if is_msvc(self) and self.options.shared:
            if self.settings.build_type == "Debug" and Version(self.version) >= "1.7.0":
                raise ConanInvalidConfiguration(
                    "Ginkgo >= 1.7.0 cannot be built in shared debug mode on Windows"
                )
            if is_msvc_static_runtime(self):
                raise ConanInvalidConfiguration(
                    "Ginkgo does not support mixing static CRT and shared library"
                )

    def build_requirements(self):
        if Version(self.version) >= "1.7.0":
            if self.options.cuda:
                self.tool_requires("cmake/[>=3.18 <4]")
            else:
                self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GINKGO_BUILD_TESTS"] = False
        tc.variables["GINKGO_BUILD_EXAMPLES"] = False
        tc.variables["GINKGO_BUILD_BENCHMARKS"] = False
        tc.variables["GINKGO_DEVEL_TOOLS"] = False
        tc.variables["GINKGO_BUILD_REFERENCE"] = True
        tc.variables["GINKGO_BUILD_OMP"] = self.options.openmp
        tc.variables["GINKGO_BUILD_CUDA"] = self.options.cuda
        tc.variables["GINKGO_BUILD_HIP"] = False
        if Version(self.version) >= "1.7.0":
            tc.variables["GINKGO_BUILD_SYCL"] = False
        else:
            tc.variables["GINKGO_BUILD_DPCPP"] = False
        tc.variables["GINKGO_BUILD_HWLOC"] = False
        tc.variables["GINKGO_BUILD_MPI"] = False
        if "half" in self.options:
            tc.variables["GINKGO_ENABLE_HALF"] = self.options.half
        if "bfloat16" in self.options:
            tc.variables["GINKGO_ENABLE_BFLOAT16"] = self.options.bfloat16
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Ginkgo")
        self.cpp_info.set_property("cmake_target_name", "Ginkgo::ginkgo")
        self.cpp_info.set_property("pkg_config_name", "ginkgo")

        debug_suffix = "d" if self.settings.build_type == "Debug" else ""
        has_dpcpp_device = Version(self.version) >= "1.4.0"
        # Shared MSVC builds ues a separate library for part of Ginkgo since 1.8.0
        has_config_library = Version(self.version) >= "1.8.0" and self.options.shared and self.settings.os == "Windows"

        self.cpp_info.components["ginkgo_core"].set_property(
            "cmake_target_name", "Ginkgo::ginkgo"
        )
        self.cpp_info.components["ginkgo_core"].set_property(
            "pkg_config_name", "ginkgo"
        )
        self.cpp_info.components["ginkgo_core"].libs = ["ginkgo" + debug_suffix]
        self.cpp_info.components["ginkgo_core"].requires = [
            "ginkgo_omp",
            "ginkgo_cuda",
            "ginkgo_reference",
            "ginkgo_hip",
        ]

        self.cpp_info.components["ginkgo_cuda"].set_property(
            "cmake_target_name", "Ginkgo::ginkgo_cuda"
        )
        self.cpp_info.components["ginkgo_cuda"].libs = ["ginkgo_cuda" + debug_suffix]
        self.cpp_info.components["ginkgo_cuda"].requires = ["ginkgo_hip"]

        self.cpp_info.components["ginkgo_omp"].set_property(
            "cmake_target_name", "Ginkgo::ginkgo_omp"
        )
        self.cpp_info.components["ginkgo_omp"].libs = ["ginkgo_omp" + debug_suffix]
        self.cpp_info.components["ginkgo_omp"].requires = ["ginkgo_cuda", "ginkgo_hip"]

        self.cpp_info.components["ginkgo_hip"].set_property(
            "cmake_target_name", "Ginkgo::ginkgo_hip"
        )
        self.cpp_info.components["ginkgo_hip"].libs = ["ginkgo_hip" + debug_suffix]

        self.cpp_info.components["ginkgo_reference"].set_property(
            "cmake_target_name", "Ginkgo::ginkgo_reference"
        )
        self.cpp_info.components["ginkgo_reference"].libs = [
            "ginkgo_reference" + debug_suffix
        ]

        if has_dpcpp_device:  # Always add these components
            # See https://github.com/conan-io/conan-center-index/pull/7044#discussion_r698181588
            self.cpp_info.components["ginkgo_core"].requires += ["ginkgo_dpcpp"]
            self.cpp_info.components["ginkgo_core"].requires += ["ginkgo_device"]

            self.cpp_info.components["ginkgo_dpcpp"].set_property(
                "cmake_target_name", "Ginkgo::ginkgo_dpcpp"
            )
            self.cpp_info.components["ginkgo_dpcpp"].libs = [
                "ginkgo_dpcpp" + debug_suffix
            ]

            self.cpp_info.components["ginkgo_device"].set_property(
                "cmake_target_name", "Ginkgo::ginkgo_device"
            )
            self.cpp_info.components["ginkgo_device"].libs = [
                "ginkgo_device" + debug_suffix
            ]

            self.cpp_info.components["ginkgo_omp"].requires += [
                "ginkgo_dpcpp",
                "ginkgo_device",
            ]
            self.cpp_info.components["ginkgo_reference"].requires += ["ginkgo_device"]
            self.cpp_info.components["ginkgo_hip"].requires += ["ginkgo_device"]
            self.cpp_info.components["ginkgo_cuda"].requires += ["ginkgo_device"]
            self.cpp_info.components["ginkgo_dpcpp"].requires += ["ginkgo_device"]
        
        if has_config_library:
            self.cpp_info.components["ginkgo_core"].requires += ["ginkgo_config"]

            self.cpp_info.components["ginkgo_config"].set_property("cmake_target_name", "Ginkgo::ginkgo_core")
            self.cpp_info.components["ginkgo_config"].libs = ["ginkgo_core" + debug_suffix]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Ginkgo"
        self.cpp_info.names["cmake_find_package_multi"] = "Ginkgo"
        self.cpp_info.components["ginkgo_core"].names["cmake_find_package"] = "ginkgo"
        self.cpp_info.components["ginkgo_core"].names[
            "cmake_find_package_multi"
        ] = "ginkgo"
