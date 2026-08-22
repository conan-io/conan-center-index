from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rm, chdir
from conan.tools.build import check_min_cppstd, cross_building, build_jobs
from conan.tools.scm import Version
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.53.0"


class ComputeLibraryConan(ConanFile):
    name = "compute_library"
    description = "The Compute Library is a set of computer vision and machine learning functions optimized for both Arm CPUs and GPUs using SIMD technologies"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ARM-software/ComputeLibrary"
    topics = ("android", "linux", "machine-learning", "arm", "computer-vision", "neural-network")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "enable_openmp": [True, False],
        "enable_opencl": [True, False],
        "enable_neon": [True, False],
        "enable_multi_isa": [True, False],
    }
    default_options = {
        "shared": False,
        "enable_openmp": False,
        "enable_opencl": True,
        "enable_neon": True,
        "enable_multi_isa": False,
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
            "clang": "5",
            "apple-clang": "5.1",
        }

    def config_options(self):
        # INFO: Neon option is reserved to arm architecture
        if "arm" not in str(self.settings.arch):
            del self.options.enable_neon
        # INFO: OpenMP option only works with g++, according to the documentation
        if self.settings.compiler == "clang":
            del self.options.enable_openmp
        # INFO: OpenCL fails to build with MacOS
        if self.settings.os == "Macos":
            del self.options.enable_opencl

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("scons/4.3.0")

    def requirements(self):
        if self.options.get_safe("enable_opencl"):
            self.requires("opencl-headers/2023.04.17")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")
        # INFO: https://github.com/ARM-software/ComputeLibrary#supported-systems
        supported_os = ["Android", "Linux", "OpenBSD", "Macos", "Tizen", "Windows"]
        if str(self.settings.os) not in supported_os:
            raise ConanInvalidConfiguration(f"{self.ref} does not support {self.settings.os}. It is only supported on {supported_os}.")
        if self.settings.os == "Windows":
            if cross_building(self):
                # INFO: https://arm-software.github.io/ComputeLibrary/latest/how_to_build.xhtml#S1_6_windows_host
                raise ConanInvalidConfiguration(f"Using scons directly from the Windows command line is known to cause problems. Please, try native native build on Windows ARM or cross-build on Linux Ubuntu.")
            if "arm" in str(self.settings.arch):
                # INFO: https://arm-software.github.io/ComputeLibrary/latest/how_to_build.xhtml#S1_6_3_WoA
                self.output.warn("Native builds on Windows are experimental and some features from the library interacting with the OS are missing.")
            if "x86" in str(self.settings.arch):
                raise ConanInvalidConfiguration(f"{self.ref} does not support native builds on Windows x86/x86_64. It is only supported on Windows ARM.")
        if "arm" not in str(self.settings.arch) and "x86" not in str(self.settings.arch):
            # INFO: https://github.com/ARM-software/ComputeLibrary#supported-architecturestechnologies
            raise ConanInvalidConfiguration(f"{self.ref} does not support {self.settings.arch}. It is only supported on arm and x86.")
        if "x86" in str(self.settings.arch) and self.settings.os != "Macos" and not self.options.get_safe("enable_opencl", False):
            raise ConanInvalidConfiguration(f"{self.ref} can be built for x86_64 targets only with enable_neon=False and enable_opencl=True.")
        if self.settings.os == "Linux" and self.settings.compiler == "clang":
            # INFO: https://arm-software.github.io/ComputeLibrary/latest/how_to_build.xhtml#S1_2_linux
            raise ConanInvalidConfiguration(f"{self.ref} does not support Linux with clang. It is only supported on Linux with gcc.")
        if "armv8" not in str(self.settings.arch) and self.options.enable_multi_isa:
            raise ConanInvalidConfiguration(f"{self.ref} does not support multi_isa option for {self.settings.arch}. It is only supported on armv8.")
        if self.settings.arch == "armv8" and self.settings_build.arch == "x86_64" and self.settings.os == "Macos" and self.settings.compiler == "apple-clang":
            raise ConanInvalidConfiguration(f"Mac Intel is not supported for armv8-a. Please, use Mac M1 as native build.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def build(self):
        # INFO: Using scons to build the library we don't have control over shared/static and install step, it is done all together always
        # INFO: https://arm-software.github.io/ComputeLibrary/latest/how_to_build.xhtml
        yes_no = lambda v: "1" if v else "0"
        debug = yes_no(self.settings.build_type == "Debug")
        build_os = str(self.settings.os).lower()
        arch = {"armv8": "armv8a", "x86": "x86_32", "armv7": "armv7a", "armv7hf": "armv7a-hf"}.get(str(self.settings.arch), str(self.settings.arch))
        neon = yes_no(self.options.get_safe("enable_neon"))
        opencl = yes_no(self.options.get_safe("enable_opencl", False))
        openmp = yes_no(self.options.get_safe("enable_openmp"))
        multi_isa = yes_no(self.options.enable_multi_isa)
        build = "cross_compile" if cross_building(self) else "native"
        with chdir(self, self.source_folder):
            self.run(f"scons Werror=0 validation_tests=0 examples=0 gemm_tuner=0 multi_isa={multi_isa} openmp={openmp} debug={debug} neon={neon} opencl={opencl} os={build_os} arch={arch} build={build} build_dir={self.build_folder} install_dir={self.package_folder} -j{build_jobs(self)} toolchain_prefix=''", env="conanbuild")

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        # INFO: Artifacts are installed during build step, so we just need to remove what we don't want
        rm(self, "*.bazel", self.package_folder, recursive=True)
        rm(self, "*.cpp", self.package_folder, recursive=True)
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
        else:
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dylib*", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        suffix = "" if self.options.shared else "-static"
        self.cpp_info.libs = [f"arm_compute{suffix}", f"arm_compute_core{suffix}", f"arm_compute_graph{suffix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
