import os
import re
from conans import AutoToolsBuildEnvironment, ConanFile, CMake, tools
from conans.errors import ConanException


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
        "force_apr_uuid": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "force_apr_uuid": True,
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
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.libs = []
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
        if self.options.force_apr_uuid:
            tools.replace_in_file(os.path.join(self._source_subfolder, "include", "apr.h.in"),
                                  "@osuuid@", "0")

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            cmake = self._configure_cmake()
            cmake.build(target="libapr-1" if self.options.shared else "apr-1")
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            cmake = self._configure_cmake()
            cmake.install()
        else:
            autotools = self._configure_autotools()
            autotools.install()

            os.unlink(os.path.join(self.package_folder, "lib", "libapr-1.la"))
            tools.rmdir(os.path.join(self.package_folder, "build-1"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

            apr_rules_mk = os.path.join(self.package_folder, "bin", "build-1", "apr_rules.mk")
            apr_rules_cnt = open(apr_rules_mk).read()
            for key in ("apr_builddir", "apr_builders", "top_builddir"):
                apr_rules_cnt, nb = re.subn("^{}=[^\n]*\n".format(key), "{}=$(_APR_BUILDDIR)\n".format(key), apr_rules_cnt, flags=re.MULTILINE)
                if nb == 0:
                    raise ConanException("Could not find/replace {} in {}".format(key, apr_rules_mk))
            open(apr_rules_mk, "w").write(apr_rules_cnt)

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "apr-1"
        self.cpp_info.libs = ["apr-1"]
        if not self.options.shared:
            self.cpp_info.defines = ["APR_DECLARE_STATIC"]
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["dl", "pthread"]

        apr_root = self.package_folder
        if tools.os_info.is_windows:
            apr_root = tools.unix_path(apr_root)
        self.output.info("Settings APR_ROOT environment var: {}".format(apr_root))
        self.env_info.APR_ROOT = apr_root

        apr_mk_dir = os.path.join(self.package_folder, "bin", "build-1")
        if tools.os_info.is_windows:
            apr_mk_dir = tools.unix_path(apr_mk_dir)
        self.env_info._APR_BUILDDIR = apr_mk_dir
