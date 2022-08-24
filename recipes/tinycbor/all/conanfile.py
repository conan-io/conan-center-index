import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class tinycborConan(ConanFile):
    name = "tinycbor"
    license = "MIT"
    homepage = "https://github.com/intel/tinycbor"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("A small CBOR encoder and decoder library, \
                    optimized for very fast operation with very small footprint.")
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False], "shared": [True, False]}
    default_options = {"fPIC": True, "shared": False}
    topics = ("CBOR", "encoder", "decoder")
    _source_subfolder = "source_subfolder"
    _env_build = None
    _env_vars = []

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os != "Linux" and self.options.shared:
            raise ConanInvalidConfiguration("Shared library only supported on Linux platform")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if not self._env_build:
            self._env_build = AutoToolsBuildEnvironment(self)
            self._env_vars = self._env_build.vars
            self._env_vars['DESTDIR'] = self.package_folder
            if self.settings.os == "Windows":
                self._env_vars["BUILD_SHARED"] = "0"
                self._env_vars["BUILD_STATIC"] = "1"
            else:
                self._env_vars["BUILD_SHARED"] = "1" if self.options.shared else "0"
                self._env_vars["BUILD_STATIC"] = "1" if not self.options.shared else "0"
        return self._env_build, self._env_vars

    def _build_nmake(self):
        with tools.chdir(self._source_subfolder):
            vcvars_command = tools.vcvars_command(self.settings)
            self.run("%s && nmake -f Makefile.nmake" % vcvars_command)

    def _build_make(self):
        with tools.chdir(self._source_subfolder):
            env_build, env_vars = self._configure_autotools()
            env_build.make(vars=env_vars)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self.settings.compiler == "Visual Studio":
            self._build_nmake()
        else:
            self._build_make()

    def _package_unix(self):
        with tools.chdir(self._source_subfolder):
            env_build, env_vars = self._configure_autotools()
            env_build.install(vars=env_vars)
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "bin"))

    def _package_visual(self):
        self.copy("tinycbor.lib", src=os.path.join(self._source_subfolder, "lib"), dst="lib")
        for header in ["cbor.h", "cborjson.h", "tinycbor-version.h"]:
            self.copy(header, src=os.path.join(self._source_subfolder, "src"), dst="include")

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            self._package_visual()
        else:
            self._package_unix()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
        self.cpp_info.includedirs = ["include", os.path.join("include","tinycbor")]
