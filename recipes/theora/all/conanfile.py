from conan.tools.microsoft import msvc_runtime_flag
from conans import ConanFile, MSBuild, AutoToolsBuildEnvironment, tools
import functools
import os
import re
import shutil
import stat

required_conan_version = ">=1.36.0"


class TheoraConan(ConanFile):
    name = "theora"
    description = "Theora is a free and open video compression format from the Xiph.org Foundation"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/theora"
    topics = ("theora", "video", "video-compressor", "video-format")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("ogg/1.3.5")

    def build_requirements(self):
        if not self._is_msvc:
            self.build_requires("gnu-config/cci.20201022")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version][0], strip_root=True, destination=self._source_subfolder)

        source = self.conan_data["sources"][self.version][1]
        url = source["url"]
        filename = url[url.rfind("/") + 1:]
        tools.files.download(self, url, filename)
        tools.check_sha256(filename, source["sha256"])

        shutil.move(filename, os.path.join(self._source_subfolder, "lib", filename))

    def _build_msvc(self):
        def format_libs(libs):
            return " ".join([l + ".lib" for l in libs])

        project = "libtheora"
        config = "dynamic" if self.options.shared else "static"
        sln_dir = os.path.join(self._source_subfolder, "win32", "VS2008")
        vcproj_path = os.path.join(sln_dir, project, "{}_{}.vcproj".format(project, config))

        # fix hard-coded ogg names
        if self.options.shared:
            tools.replace_in_file(vcproj_path,
                                  "libogg.lib",
                                  format_libs(self.deps_cpp_info["ogg"].libs))

        # Honor vc runtime from profile
        if "MT" in msvc_runtime_flag(self):
            tools.replace_in_file(vcproj_path, 'RuntimeLibrary="2"', 'RuntimeLibrary="0"')
            tools.replace_in_file(vcproj_path, 'RuntimeLibrary="3"', 'RuntimeLibrary="1"')

        sln = "{}_{}.sln".format(project, config)
        targets = ["libtheora" if self.options.shared else "libtheora_static"]
        properties = {
            # Enable LTO when CFLAGS contains -GL
            "WholeProgramOptimization": "true" if any(re.finditer("(^| )[/-]GL($| )", tools.get_env("CFLAGS", ""))) else "false",
        }

        with tools.chdir(sln_dir):
            msbuild = MSBuild(self)
            msbuild.build(sln, targets=targets, platforms={"x86": "Win32", "x86_64": "x64"}, properties=properties)

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--disable-examples",
        ]
        autotools.configure(configure_dir=self._source_subfolder, args=args)
        return autotools

    def build(self):
        if self._is_msvc:
            self._build_msvc()
        else:
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                        os.path.join(self._source_subfolder, "config.sub"))
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                        os.path.join(self._source_subfolder, "config.guess"))
            configure = os.path.join(self._source_subfolder, "configure")
            permission = stat.S_IMODE(os.lstat(configure).st_mode)
            os.chmod(configure, (permission | stat.S_IEXEC))
            # relocatable shared libs on macOS
            tools.replace_in_file(configure, "-install_name \\$rpath/", "-install_name @rpath/")
            # avoid SIP issues on macOS when dependencies are shared
            if tools.is_apple_os(self.settings.os):
                libpaths = ":".join(self.deps_cpp_info.lib_paths)
                tools.replace_in_file(
                    configure,
                    "#! /bin/sh\n",
                    "#! /bin/sh\nexport DYLD_LIBRARY_PATH={}:$DYLD_LIBRARY_PATH\n".format(libpaths),
                )
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            include_folder = os.path.join(self._source_subfolder, "include")
            self.copy(pattern="*.h", dst="include", src=include_folder)
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "theora_full_package") # to avoid conflicts with _theora component

        self.cpp_info.components["_theora"].set_property("pkg_config_name", "theora")
        prefix = "lib" if self._is_msvc else ""
        suffix = "_static" if self._is_msvc and not self.options.shared else ""
        self.cpp_info.components["_theora"].libs = [f"{prefix}theora{suffix}"]
        self.cpp_info.components["_theora"].requires = ["ogg::ogg"]

        self.cpp_info.components["theoradec"].set_property("pkg_config_name", "theoradec")
        self.cpp_info.components["theoradec"].requires = ["ogg::ogg"]
        if self._is_msvc:
            self.cpp_info.components["theoradec"].requires.append("_theora")
        else:
            self.cpp_info.components["theoradec"].libs = ["theoradec"]

        self.cpp_info.components["theoraenc"].set_property("pkg_config_name", "theoraenc")
        self.cpp_info.components["theoraenc"].requires = ["theoradec", "ogg::ogg"]
        if self._is_msvc:
            self.cpp_info.components["theoradec"].requires.append("_theora")
        else:
            self.cpp_info.components["theoraenc"].libs = ["theoraenc"]

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "theora_full_package"
