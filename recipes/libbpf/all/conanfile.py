from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibbpfConan(ConanFile):
    name = "libbpf"
    description = "eBPF helper library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libbpf/libbpf"
    license = "LGPL-2.1", "BSD-2-Clause"
    topics = ("bpf", "ebpf", "libbpf", "berkeley-packet-filter")
    generators = "pkg_config"
    settings = "os", "arch", "compiler", "build_type"

    _autotools = None

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        self.build_requires("make/4.2.1")

    def requirements(self):
        self.requires("linux-headers-generic/5.13.9")
        self.requires("libelf/0.8.13")
        self.requires("zlib/1.2.11")

    def _configure_autotools(self):
        make_args = [
            "--directory={}".format("src"),
            "PREFIX={}".format(""),
            "DESTDIR={}".format(self.package_folder),
            "LIBSUBDIR={}".format("lib"),
        ]
        if not self.options.shared:
            make_args.append("BUILD_STATIC_ONLY={}".format(1))

        if self._autotools:
            return self._autotools, make_args
        self._autotools = AutoToolsBuildEnvironment(self)
        return self._autotools, make_args

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("This library is only available on Linux")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools, make_args = self._configure_autotools()
            autotools.make(args=make_args)

    def package(self):
        with tools.chdir(self._source_subfolder):
            autotools, make_args = self._configure_autotools()
            autotools.install(args=make_args)

        if self.options.shared:
            os.remove(os.path.join(self.package_folder, "lib", "libbpf.a"))

        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE.BSD-2-Clause", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE.LGPL-2.1", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libbpf"
        self.cpp_info.libs = ["bpf"]
