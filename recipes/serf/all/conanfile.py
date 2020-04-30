from conans import AutoToolsBuildEnvironment, ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os


class SerfConan(ConanFile):
    name = "serf"
    description = "The serf library is a high performance C-based HTTP client library built upon the Apache Portable Runtime (APR) library."
    license = "Apache-2.0"
    topics = ("conan", "serf", "apache", "http", "library")
    homepage = "https://serf.apache.org/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("apr-util/1.6.1")
        self.requires("zlib/1.2.11")
        self.requires("openssl/1.1.1g")

    def build_requirements(self):
        self.build_requires("scons/3.1.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        os.mkdir(self._build_subfolder)
        with tools.chdir(self._build_subfolder):
            args = ["-Y", os.path.join(self.source_folder, self._source_subfolder)]
            kwargs = {
                "APR": self.deps_cpp_info["apr"].rootpath,
                "APU": self.deps_cpp_info["apr-util"].rootpath,
                "OPENSSL": self.deps_cpp_info["openssl"].rootpath,
                "PREFIX": self.package_folder,
                "LIBDIR": os.path.join(self.package_folder, "lib"),
                "ZLIB": self.deps_cpp_info["zlib"].rootpath,
                "DEBUG": self.settings.build_type == "Debug",
                "APR_STATIC": not self.options["apr"].shared,
                "CFLAGS": " ".join(self.deps_cpp_info.cflags),
                "LINKFLAGS": " ".join(self.deps_cpp_info.sharedlinkflags) + " " + " ".join("-L'{}'".format(l) for l in self.deps_cpp_info.lib_paths),
                "CPPFLAGS": " ".join("-D{}".format(d) for d in self.deps_cpp_info.defines) + " " + " ".join("-I'{}'".format(inc) for inc in self.deps_cpp_info.include_paths),
            }

            if self.settings.compiler == "Visual Studio":
                kwargs.update({
                    "TARGET_ARCH": str(self.settings.arch),
                    "MSVC_VERSION": str(self.settings.compiler.version),
                })

            escape_str = lambda x : "\"{}\"".format(x)
            self.run("scons {} {}".format(" ".join(escape_str(s) for s in args), " ".join("{}={}".format(k, escape_str(v)) for k, v in kwargs.items())), run_environment=True)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        with tools.chdir(self._build_subfolder):
            self.run("scons install -Y \"{}\"".format(os.path.join(self.source_folder, self._source_subfolder)), run_environment=True)

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        libname = "serf-{}".format(self.version.split(".", 1)[0])
        self.cpp_info.libs = [libname]
        self.cpp_info.includedirs.append(os.path.join("include", libname))
        self.cpp_info.names["pkg_config"] = libname
