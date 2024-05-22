import os

from conan import ConanFile
from conan.tools.apple import is_apple_os, to_apple_arch
from conan.tools.env import VirtualBuildEnv, Environment
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rmdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class SwigConan(ConanFile):
    name = "swig"
    description = "SWIG is a software development tool that connects programs written in C and C++ with a variety of high-level programming languages."
    license = "GPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.swig.org"
    topics = ("python", "java", "wrapper")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        # SWIG prefers static linking
        self.options["pcre"].shared = False
        self.options["pcre2"].shared = False
        self.options["libgettext"].shared = False

    def export_sources(self):
        copy(self, "cmake/*", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _use_pcre2(self):
        return Version(self.version) >= "4.1"

    def requirements(self):
        if self._use_pcre2:
            self.requires("pcre2/10.43")
        else:
            self.requires("pcre/8.45")
        if is_apple_os(self):
            self.requires("libgettext/0.22")

    def package_id(self):
        del self.info.settings.compiler

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
            if is_msvc(self):
                self.tool_requires("cccl/1.3")
        if is_msvc(self):
            self.tool_requires("winflexbison/2.5.25")
        else:
            self.tool_requires("bison/3.8.2")
        self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        build_env = VirtualBuildEnv(self)
        build_env.generate()

        tc = AutotoolsToolchain(self)
        env = tc.environment()

        pcre = "pcre2" if self._use_pcre2 else "pcre"
        tc.configure_args += [
            f"--host={self.settings.arch}",
            "--with-swiglibdir=${prefix}/bin/swiglib",
            f"--with-{pcre}-prefix={self.dependencies[pcre].package_folder}",
        ]
        tc.extra_cflags.append("-DHAVE_PCRE=1")
        if self._use_pcre2:
            env.define("PCRE2_LIBS", " ".join("-l" + lib for lib in self.dependencies["pcre2"].cpp_info.libs))

        if self.settings.os in ["Linux", "FreeBSD"]:
            tc.configure_args.append("LIBS=-ldl")
            tc.extra_defines.append("HAVE_UNISTD_H=1")
        elif self.settings.os == "Windows":
            if is_msvc(self):
                env.define("CC", "cccl -FS")
                env.define("CXX", "cccl -FS")
                tc.configure_args.append("--disable-ccache")
            else:
                tc.extra_ldflags.append("-static")
                tc.configure_args.append("LIBS=-lmingwex -lssp")
        elif is_apple_os(self):
            tc.extra_cflags.append(f"-arch {to_apple_arch(self)}")
            tc.extra_cxxflags.append(f"-arch {to_apple_arch(self)}")
            tc.extra_ldflags.append(f"-arch {to_apple_arch(self)}")
        tc.generate(env)

        if is_msvc(self):
            # Custom AutotoolsDeps for cl-like compilers
            # workaround for https://github.com/conan-io/conan/issues/12784
            includedirs = []
            defines = []
            libs = []
            libdirs = []
            linkflags = []
            cxxflags = []
            cflags = []
            for dependency in self.dependencies.values():
                deps_cpp_info = dependency.cpp_info.aggregated_components()
                includedirs.extend(deps_cpp_info.includedirs)
                defines.extend(deps_cpp_info.defines)
                libs.extend(deps_cpp_info.libs + deps_cpp_info.system_libs)
                libdirs.extend(deps_cpp_info.libdirs)
                linkflags.extend(deps_cpp_info.sharedlinkflags + deps_cpp_info.exelinkflags)
                cxxflags.extend(deps_cpp_info.cxxflags)
                cflags.extend(deps_cpp_info.cflags)

            env = Environment()
            env.append("CPPFLAGS", [f"-I{unix_path(self, p)}" for p in includedirs] + [f"-D{d}" for d in defines])
            env.append("_LINK_", [lib if lib.endswith(".lib") else f"{lib}.lib" for lib in libs])
            env.append("LDFLAGS", [f"-L{unix_path(self, p)}" for p in libdirs] + linkflags)
            env.append("CXXFLAGS", cxxflags)
            env.append("CFLAGS", cflags)
            env.vars(self).save_script("conanautotoolsdeps_cl_workaround")
        else:
            deps = AutotoolsDeps(self)
            deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Rely on AutotoolsDeps instead of pcre2-config
        # https://github.com/swig/swig/blob/v4.1.1/configure.ac#L70-L92
        # https://github.com/swig/swig/blob/v4.0.2/configure.ac#L65-L86
        replace_in_file(self, os.path.join(self.source_folder, "configure.ac"),
                        'AS_IF([test "x$with_pcre" != xno],', 'AS_IF([false],')

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            self.run("./autogen.sh")
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "COPYRIGHT", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.cmake",
             dst=os.path.join(self.package_folder, self._module_subfolder),
             src=os.path.join(self.export_sources_folder, "cmake"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        for path in self.package_path.iterdir():
            if path.is_dir() and path.name not in ["bin", "lib", "licenses"]:
                rmdir(self, path)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _cmake_module_rel_path(self):
        return os.path.join(self._module_subfolder, "conan-swig-variables.cmake")

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.set_property("cmake_file_name", "SWIG")
        self.cpp_info.set_property("cmake_target_name", "SWIG::SWIG")
        self.cpp_info.set_property("cmake_build_modules", [self._cmake_module_rel_path])

        self.buildenv_info.define_path("SWIG_LIB", os.path.join(self.package_folder, "bin", "swiglib"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "SWIG"
        self.cpp_info.names["cmake_find_package_multi"] = "SWIG"
        self.cpp_info.build_modules["cmake_find_package"] = [self._cmake_module_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._cmake_module_rel_path]

        bindir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bindir)
        self.env_info.SWIG_LIB = os.path.join(self.package_folder, "bin", "swiglib")
