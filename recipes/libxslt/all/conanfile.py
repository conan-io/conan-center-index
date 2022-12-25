from conan.tools.microsoft import is_msvc, msvc_runtime_flag
from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.45.0"


class LibxsltConan(ConanFile):
    name = "libxslt"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libxslt is a software library implementing XSLT processor, based on libxml2"
    topics = ("XSLT", "processor")
    homepage = "https://xmlsoft.org"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "debugger": [True, False],
        "crypto": [True, False],
        "profiler": [True, False],
        "plugins": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "debugger": False,
        "crypto": False,
        "profiler": False,
        "plugins": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _option_names(self):
        return [name for name in self.default_options.keys() if name not in ["shared", "fPIC"]]

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

    def requirements(self):
        self.requires("libxml2/2.9.14")

    def validate(self):
        if self.options.plugins and not self.options.shared:
            raise ConanInvalidConfiguration("plugins require shared")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self) and \
           not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if is_msvc(self):
            self._build_msvc()
        else:
            # Relocatable shared libs on macOS
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "configure"),
                "-install_name \\$rpath/",
                "-install_name @rpath/"
            )
            autotools = self._configure_autotools()
            autotools.make()

    def _build_msvc(self):
        with tools.chdir(os.path.join(self._source_subfolder, "win32")):
            debug = "yes" if self.settings.build_type == "Debug" else "no"
            static = "no" if self.options.shared else "yes"

            with tools.vcvars(self):
                args = [
                    "cscript",
                    "configure.js",
                    "compiler=msvc",
                    "prefix={}".format(self.package_folder),
                    "cruntime=/{}".format(msvc_runtime_flag(self)),
                    "debug={}".format(debug),
                    "static={}".format(static),
                    "include=\"{}\"".format(";".join(self.deps_cpp_info.include_paths)),
                    "lib=\"{}\"".format(";".join(self.deps_cpp_info.lib_paths)),
                    "iconv=no",
                    "xslt_debug=no",
                ]
                for name in self._option_names:
                    cname = {"plugins": "modules"}.get(name, name)
                    value = getattr(self.options, name)
                    value = "yes" if value else "no"
                    args.append("%s=%s" % (cname, value))
                configure_command = ' '.join(args)
                self.output.info(configure_command)
                self.run(configure_command)

                # Fix library names because they can be not just zlib.lib
                def format_libs(package):
                    libs = []
                    for lib in self.deps_cpp_info[package].libs:
                        libname = lib
                        if not libname.endswith('.lib'):
                            libname += '.lib'
                        libs.append(libname)
                    for lib in self.deps_cpp_info[package].system_libs:
                        libname = lib
                        if not libname.endswith('.lib'):
                            libname += '.lib'
                        libs.append(libname)
                    return ' '.join(libs)

                def fix_library(option, package, old_libname):
                    if option:
                        tools.replace_in_file("Makefile.msvc",
                                              "LIBS = %s" % old_libname,
                                              "LIBS = %s" % format_libs(package))

                if "icu" in self.deps_cpp_info.deps:
                    fix_library(True, 'icu', 'wsock32.lib')

                tools.replace_in_file("Makefile.msvc", "libxml2.lib", format_libs("libxml2"))
                tools.replace_in_file("Makefile.msvc", "libxml2_a.lib", format_libs("libxml2"))

                # Avoid to indirectly build both static & shared when we build utils
                tools.replace_in_file(
                    "Makefile.msvc",
                    "$(UTILS) : $(UTILS_INTDIR) $(BINDIR) libxslt libxslta libexslt libexslta",
                    "$(UTILS) : $(UTILS_INTDIR) $(BINDIR) libxslt{0} libexslt{0}".format("" if self.options.shared else "a"),
                )

                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    targets = "libxslt{0} libexslt{0} utils".format("" if self.options.shared else "a")
                    self.run("nmake /f Makefile.msvc {}".format(targets))

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-python=no",
            "--with-libxml-src={}".format(tools.unix_path(self.deps_cpp_info["libxml2"].rootpath)),
        ]
        for name in self._option_names:
            value = getattr(self.options, name)
            args.append("--with-{}={}".format(name, yes_no(value)))
        autotools.configure(args=args, configure_dir=self._source_subfolder)
        return autotools

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        if is_msvc(self):
            self.copy("*.h", src=os.path.join(self._source_subfolder, "libxslt"),
                             dst=os.path.join("include", "libxslt"))
            self.copy("*.h", src=os.path.join(self._source_subfolder, "libexslt"),
                             dst=os.path.join("include", "libexslt"))
            build_dir = os.path.join(self._source_subfolder, "win32", "bin.msvc")
            self.copy("*.exe", src=build_dir, dst="bin")
            if self.options.shared:
                self.copy("*xslt.lib", src=build_dir, dst="lib")
                self.copy("*xslt.dll", src=build_dir, dst="bin")
            else:
                self.copy("*xslt_a.lib", src=build_dir, dst="lib")
        else:
            autotools = self._configure_autotools()
            autotools.install()
            os.remove(os.path.join(self.package_folder, "bin", "xslt-config"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.sh")
            tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "LibXslt")
        self.cpp_info.set_property("pkg_config_name", "libxslt_full_package") # unofficial, avoid conflicts in conan generators

        prefix = "lib" if is_msvc(self) else ""
        suffix = "_a" if is_msvc(self) and not self.options.shared else ""

        # xslt
        self.cpp_info.components["xslt"].set_property("cmake_target_name", "LibXslt::LibXslt")
        self.cpp_info.components["xslt"].set_property("pkg_config_name", "libxslt")
        self.cpp_info.components["xslt"].libs = ["{}xslt{}".format(prefix, suffix)]
        if not self.options.shared:
            self.cpp_info.components["xslt"].defines = ["LIBXSLT_STATIC"]
        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.cpp_info.components["xslt"].system_libs.append("m")
        elif self.settings.os == "Windows":
            self.cpp_info.components["xslt"].system_libs.append("ws2_32")
        self.cpp_info.components["xslt"].requires = ["libxml2::libxml2"]

        # exslt
        self.cpp_info.components["exslt"].set_property("cmake_target_name", "LibXslt::LibExslt")
        self.cpp_info.components["exslt"].set_property("pkg_config_name", "libexslt")
        self.cpp_info.components["exslt"].libs = ["{}exslt{}".format(prefix, suffix)]
        self.cpp_info.components["exslt"].requires = ["xslt"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "LibXslt"
        self.cpp_info.names["cmake_find_package_multi"] = "LibXslt"
        self.cpp_info.names["pkg_config"] = "libxslt_full_package"
        self.cpp_info.components["xslt"].names["cmake_find_package"] = "LibXslt"
        self.cpp_info.components["xslt"].names["cmake_find_package_multi"] = "LibXslt"
        self.cpp_info.components["xslt"].names["pkg_config"] = "libxslt"
        self.cpp_info.components["exslt"].names["cmake_find_package"] = "LibExslt"
        self.cpp_info.components["exslt"].names["cmake_find_package_multi"] = "LibExslt"
        self.cpp_info.components["exslt"].names["pkg_config"] = "libexslt"
