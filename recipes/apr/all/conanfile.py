from conans import AutoToolsBuildEnvironment, ConanFile, CMake, tools
from conans.errors import ConanException, ConanInvalidConfiguration
import os
import re

required_conan_version = ">=1.36.0"


class AprConan(ConanFile):
    name = "apr"
    description = "The Apache Portable Runtime (APR) provides a predictable and consistent interface to underlying platform-specific implementations"
    license = "Apache-2.0"
    topics = ("apache", "platform", "library")
    homepage = "https://apr.apache.org/"
    url = "https://github.com/conan-io/conan-center-index"

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

    generators = "cmake"
    _autotools = None
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _should_call_autoreconf(self):
        return self.settings.compiler == "apple-clang" and \
               tools.Version(self.settings.compiler.version) >= "12" and \
               self.version == "1.7.0"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        if hasattr(self, "settings_build") and tools.cross_building(self):
            raise ConanInvalidConfiguration("apr cannot be cross compiled due to runtime checks")

    def build_requirements(self):
        if self._should_call_autoreconf:
            self.build_requires("libtool/2.4.6")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

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
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--with-installbuilddir=${prefix}/bin/build-1",
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        if tools.cross_building(self):
            #
            conf_args.append("apr_cv_mutex_robust_shared=yes")
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
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
            if self._should_call_autoreconf:
                with tools.chdir(self._source_subfolder):
                    self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
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
            tools.files.rmdir(self, os.path.join(self.package_folder, "build-1"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

            apr_rules_mk = os.path.join(self.package_folder, "bin", "build-1", "apr_rules.mk")
            apr_rules_cnt = open(apr_rules_mk).read()
            for key in ("apr_builddir", "apr_builders", "top_builddir"):
                apr_rules_cnt, nb = re.subn("^{}=[^\n]*\n".format(key), "{}=$(_APR_BUILDDIR)\n".format(key), apr_rules_cnt, flags=re.MULTILINE)
                if nb == 0:
                    raise ConanException("Could not find/replace {} in {}".format(key, apr_rules_mk))
            open(apr_rules_mk, "w").write(apr_rules_cnt)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name",  "apr-1")
        self.cpp_info.libs = ["libapr-1" if self.settings.compiler == "Visual Studio" and self.options.shared else "apr-1"]
        if not self.options.shared:
            self.cpp_info.defines = ["APR_DECLARE_STATIC"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs = ["dl", "pthread"]
            if self.settings.os == "Windows":
                self.cpp_info.system_libs = ["rpcrt4"]

        apr_root = tools.unix_path(self.package_folder)
        self.output.info("Settings APR_ROOT environment var: {}".format(apr_root))
        self.env_info.APR_ROOT = apr_root

        apr_mk_dir = tools.unix_path(os.path.join(self.package_folder, "bin", "build-1"))
        self.env_info._APR_BUILDDIR = apr_mk_dir
