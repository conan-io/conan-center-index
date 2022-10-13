from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, download, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, MSBuild, MSBuildToolchain, unix_path, msvc_runtime_flag

import os
import re
import stat

# 1.53 for cpp_info.bindir
required_conan_version = ">=1.53.0"


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
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)
 
    # this technique taken from xz_utils recipe, with the extra MT stuff stripped out (assuming we dont need it)
    @property
    def _effective_msbuild_type(self):
        # treat "RelWithDebInfo" and "MinSizeRel" as "Release"
        return "Debug" if self.settings.build_type == "Debug" else "Release"


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="source")

    def requirements(self):
        self.requires("ogg/1.3.5")

    def build_requirements(self):
        if not is_msvc(self):
            self.build_requires("gnu-config/cci.20201022")  # TODO Bump this version? Needed for non-windows?
            if self._settings_build.os == "Windows":
                if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
                    self.build_requires("msys2/cci.latest")
                self.win_bash = True

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        def_file = self.conan_data["def_files"][self.version]
        url = def_file["url"]
        filename = url[url.rfind("/") + 1:]
        download(self, **def_file, filename=os.path.join(self.source_folder, "lib", filename))

    # TODO move below generate() once initial review is done
    def _build_msvc(self):
        def format_libs(libs):
            return " ".join([l + ".lib" for l in libs])

        project = "libtheora"
        config = "dynamic" if self.options.shared else "static"
        sln_dir = os.path.join(self.source_folder, "win32", "VS2008")
        vcproj_path = os.path.join(sln_dir, project, "{}_{}.vcproj".format(project, config))

        # fix hard-coded ogg names
        if self.options.shared:
            replace_in_file(self, vcproj_path,
                                  "libogg.lib",
                                  format_libs(self.deps_cpp_info["ogg"].libs))

        # Honor vc runtime from profile
        if "MT" in msvc_runtime_flag(self):
            replace_in_file(self, vcproj_path, 'RuntimeLibrary="2"', 'RuntimeLibrary="0"')
            replace_in_file(self, vcproj_path, 'RuntimeLibrary="3"', 'RuntimeLibrary="1"')

        sln = "{}_{}.sln".format(project, config)
        targets = ["libtheora" if self.options.shared else "libtheora_static"]

        with chdir(self, sln_dir):
            msbuild = MSBuild(self)
            msbuild.build_type = self._effective_msbuild_type
            # TODO this didn't work without chdir... msbuild.build(os.path.join(sln_dir,sln), targets=targets)
            msbuild.build(os.path.join(sln_dir,sln), targets=targets)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)

            # TODO if self.settings.build_type == "RelWithDebInfo":    # was converted to "Release" as no RelWithDebInfo option
                # TODO cxx_flags.append("/Z7")

            # TODO how to do this in conan v2 ?   Same trick also used in recipe for lcms.
            # Enable LTO when CFLAGS contains -GL
            # if any(re.finditer("(^| )[/-]GL($| )", tools.get_env("CFLAGS", ""))):
                # tc.properties["WholeProgramOptimization"] = "true"

            tc.generate()

        else:
            tc = AutotoolsToolchain(self)
            tc.configure_args.append("--disable-examples")
            tc.generate()
            env = VirtualBuildEnv(self)
            env.generate()

    def build(self):
        if is_msvc(self):
            self._build_msvc()
        else:
            gnu_config = self.dependencies["gnu-config"]
            copy(self, "config.sub",   gnu_config.cpp_info.bindir, self.source_folder)
            copy(self, "config.guess", gnu_config.cpp_info.bindir, self.source_folder)
            configure = os.path.join(self.source_folder, "configure")
            permission = stat.S_IMODE(os.lstat(configure).st_mode)
            os.chmod(configure, (permission | stat.S_IEXEC))
            # relocatable shared libs on macOS
            replace_in_file(self, configure, "-install_name \\$rpath/", "-install_name @rpath/")
            # avoid SIP issues on macOS when dependencies are shared
            if tools.is_apple_os(self.settings.os):
                libpaths = ":".join(self.deps_cpp_info.lib_paths)
                replace_in_file(self,
                    configure,
                    "#! /bin/sh\n",
                    "#! /bin/sh\nexport DYLD_LIBRARY_PATH={}:$DYLD_LIBRARY_PATH\n".format(libpaths),
                )
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, pattern="LICENSE", dst="licenses", src=self.source_folder)
        copy(self, pattern="COPYING", dst="licenses", src=self.source_folder)
        if is_msvc(self):
            copy(self, pattern="*.h", dst="include", src=os.path.join(self.source_folder, "include"))
            copy(self, pattern="*.dll", dst="bin", src=self.source_folder, keep_path=False)
            copy(self, pattern="*.lib", dst="lib", src=self.source_folder, keep_path=False)
        else:
            autotools = Autotools(self)
            # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
            autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "theora_full_package") # to avoid conflicts with _theora component

        self.cpp_info.components["_theora"].set_property("pkg_config_name", "theora")
        prefix = "lib" if is_msvc(self) else ""
        suffix = "_static" if is_msvc(self) and not self.options.shared else ""
        self.cpp_info.components["_theora"].libs = [f"{prefix}theora{suffix}"]
        self.cpp_info.components["_theora"].requires = ["ogg::ogg"]

        self.cpp_info.components["theoradec"].set_property("pkg_config_name", "theoradec")
        self.cpp_info.components["theoradec"].requires = ["ogg::ogg"]
        if is_msvc(self):
            self.cpp_info.components["theoradec"].requires.append("_theora")
        else:
            self.cpp_info.components["theoradec"].libs = ["theoradec"]

        self.cpp_info.components["theoraenc"].set_property("pkg_config_name", "theoraenc")
        self.cpp_info.components["theoraenc"].requires = ["theoradec", "ogg::ogg"]
        if is_msvc(self):
            self.cpp_info.components["theoradec"].requires.append("_theora")
        else:
            self.cpp_info.components["theoraenc"].libs = ["theoraenc"]

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "theora_full_package"
