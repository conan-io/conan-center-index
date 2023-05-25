import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class ThrustConan(ConanFile):
    name = "thrust"
    license = "Apache-2.0"
    description = (
        "Thrust is a parallel algorithms library which resembles "
        "the C++ Standard Template Library (STL)."
    )
    topics = ("parallel", "stl", "header-only", "cuda", "gpgpu")
    homepage = "https://thrust.github.io/"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {
        "device_system": ["cuda", "cpp", "omp", "tbb"],
    }
    default_options = {
        "device_system": "tbb",
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # TODO: https://github.com/conan-io/conan-center-index/pull/17484
        # Otherwise CUB from system CUDA is used, which is not guaranteed to be compatible
        # self.requires("cub/1.17.2")

        if self.options.device_system == "tbb":
            self.requires("onetbb/2021.9.0")

        if self.options.device_system in ["cuda", "omp"]:
            dev = str(self.options.device_system).upper()
            self.output.warning(
                f"Conan package for {dev} is not available,"
                f" this package will use {dev} from system."
            )

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        for pattern in ["*.h", "*.inl"]:
            copy(
                self,
                pattern=pattern,
                src=os.path.join(self.source_folder, "thrust"),
                dst=os.path.join(self.package_folder, "include", "thrust"),
            )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        dev = str(self.options.device_system).upper()
        self.cpp_info.defines = [f"THRUST_DEVICE_SYSTEM=THRUST_DEVICE_SYSTEM_{dev}"]
        # Since CUB and Thrust are provided separately, their versions are not guaranteed to match
        self.cpp_info.defines += ["THRUST_IGNORE_CUB_VERSION_CHECK=1"]
