from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.build import check_min_cppstd
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.files import chdir, collect_libs, copy, get, rename, rm, rmdir
from conan.tools.system.package_manager import Apk, Apt, Dnf, Yum
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0.5"


class DpdkConan(ConanFile):
    name = "dpdk"
    homepage = "https://dpdk.org"
    description = "libraries to accelerate packet processing workloads"
    topics = ("dpdk", "networking")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    package_type = "shared-library"
    generators = "VirtualBuildEnv", "VirtualRunEnv"
    settings = "os", "arch", "compiler", "build_type"
    options = {
#        "shared": [True],
#        "fPIC": [True]
        }
    default_options = {
#        "shared": True,
#        "fPIC": True
        }

    @property
    def _min_cppstd(self):
        return "11"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "3.6",
        }

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("DPDK is only supported on Linux")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        basic_layout(self, src_folder="src")

    def system_requirements(self):
        # depending on the platform or the tools.system.package_manager:tool configuration
        # only one of these will be executed
        Apk(self).install(["py3-elftools", "numactl-dev"])
        Apt(self).install(["python3-pyelftools", "libnuma-dev"])
        Dnf(self).install(["python3-pyelftools", "numactl-devel"])
        Yum(self).install(["python3-pyelftools", "numactl-devel"])

    def build_requirements(self):
        self.tool_requires("meson/1.5.0")

    def generate(self):
        tc = MesonToolchain(self)
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "*", os.path.join(self.source_folder, "license"), os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

