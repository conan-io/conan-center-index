import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment

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
    topics = ("conan", "CBOR", "encoder", "decoder")
    exports_sources = ["patches/*"]
    _source_subfolder = "source_subfolder"
    _env_build = None
    _env_vars = []

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
                self._env_build.fpic = self.options.fPIC
        return self._env_build, self._env_vars

    def configure(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")
            self.options.remove("shared") # Shared lib only supported on unix systems
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            env_build, env_vars = self._configure_autotools()
            env_build.make(vars=env_vars)

    def package(self):
        with tools.chdir(self._source_subfolder):
            env_build, env_vars = self._configure_autotools()
            env_build.install(vars=env_vars)
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
        self.cpp_info.includedirs = ["include", os.path.join("include","tinycbor")]
