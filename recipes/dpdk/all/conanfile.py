from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class DpdkConan(ConanFile):
    name = "dpdk"
    homepage = "https://dpdk.org"
    description = "libraries to accelerate packet processing workloads"
    topics = ("dpdk", "networking")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    generators = "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
        }
    default_options = {
        "shared": False,
        "fPIC": True
        }

    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("DPDK is only supported on Linux")

    def build_requirements(self):
        self.build_requires("meson/[>=0.49.2]")
        print("RUNNING PIP")
        import pip
        if hasattr(pip, "main"):
            pip.main(["install", "pyelftools"])
        else:
            from pip._internal import main
            main(['install', "pyelftools"])

    def requirements(self):
        self.requires("libbpf/0.4.0")
        self.requires("jansson/2.14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_meson(self):
        if self._meson:
            return self._meson

        self._meson = Meson(self)
        self._meson.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder, pkg_config_paths=[self.install_folder])
        return self._meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy("*", dst="licenses", src=os.path.join(self._source_subfolder, "license"))
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
