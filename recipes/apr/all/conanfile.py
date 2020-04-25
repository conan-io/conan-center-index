import os

from conans import AutoToolsBuildEnvironment, ConanFile, CMake, tools


class AprConan(ConanFile):
    name = "apr"
    description = "The Apache Portable Runtime (APR) provides a predictable and consistent interface to underlying platform-specific implementations"
    license = "Apache-2.0"
    topics = ("conan", "apr", "apache", "platform", "library")
    homepage = "https://apr.apache.org/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None
    _cmake = None

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["INSTALL_PDB"] = False
        self._cmake.definitions["APR_BUILD_TESTAPR"] = False
        # self._cmake.definitions["APR_INSTALL_PRIVATE_H"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        conf_args = [
            "--with-installbuilddir=${prefix}/bin/build-1",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.build(target="libapr-1" if self.options.shared else "apr-1")
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.install()
        else:
            autotools = self._configure_autotools()
            autotools.install()

            os.unlink(os.path.join(self.package_folder, "lib", "libapr-1.la"))
            tools.rmdir(os.path.join(self.package_folder, "build-1"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "apr-1"
        self.cpp_info.libs = ["apr-1"]
        if not self.options.shared:
            self.cpp_info.defines = ["APR_DECLARE_STATIC"]
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["dl", "pthread"]

        apr_root = tools.unix_path(self.package_folder)
        self.output.info("Settings APR_ROOT environment var: {}".format(apr_root))
        self.env_info.APR_ROOT = apr_root
