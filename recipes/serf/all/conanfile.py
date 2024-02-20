import os
import re

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, load, mkdir, rm, rmdir, save
from conan.tools.gnu import AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path, msvs_toolset
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class SerfConan(ConanFile):
    name = "serf"
    description = ("The serf library is a high performance C-based HTTP client library "
                   "built upon the Apache Portable Runtime (APR) library.")
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://serf.apache.org/"
    topics = ("apache", "http", "library")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("apr-util/1.6.1", transitive_headers=True, transitive_libs=True)
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("openssl/[>=1.1 <4]")

    def build_requirements(self):
        self.tool_requires("scons/4.3.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _cc(self):
        if "CC" in os.environ:
            return os.environ["CC"]
        if is_apple_os(self):
            return "clang"
        if is_msvc(self):
            return "cl"
        return str(self.settings.compiler)

    def _lib_path_arg(self, path):
        argname = "LIBPATH:" if is_msvc(self) else "L"
        return "-{}'{}'".format(argname, unix_path(self, path))

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        autotools = AutotoolsToolchain(self)
        args = ["-Y", self.source_folder]
        libdirs = sum([dep.cpp_info.libdirs for dep in self.dependencies.values()], [])
        sharedlinkflags = sum([dep.cpp_info.sharedlinkflags for dep in self.dependencies.values()], [])
        includedirs = sum([dep.cpp_info.includedirs for dep in self.dependencies.values()], [])
        cflags = sum([dep.cpp_info.cflags for dep in self.dependencies.values()], [])
        cflags += autotools.cflags
        libs = sum([dep.cpp_info.libs for dep in self.dependencies.values()], [])
        if self.options.get_safe("fPIC"):
            cflags.append("-fPIC")
        kwargs = {
            "APR": unix_path(self, self.dependencies["apr"].package_folder),
            "APU": unix_path(self, self.dependencies["apr-util"].package_folder),
            "OPENSSL": unix_path(self, self.dependencies["openssl"].package_folder),
            "PREFIX": unix_path(self, self.package_folder),
            "LIBDIR": unix_path(self, os.path.join(self.package_folder, "lib")),
            "ZLIB": unix_path(self, self.dependencies["zlib"].package_folder),
            "DEBUG": self.settings.build_type == "Debug",
            "APR_STATIC": not self.dependencies["apr"].options.shared,
            "CFLAGS": " ".join(cflags),
            "LINKFLAGS": " ".join(sharedlinkflags + [self._lib_path_arg(l) for l in libdirs]),
            "CPPFLAGS": " ".join([f"-D{d}" for d in autotools.defines] + [f"-I'{unix_path(self, inc)}'" for inc in includedirs]),
            "CC": self._cc,
            "SOURCE_LAYOUT": "False",
        }

        if is_msvc(self):
            kwargs["TARGET_ARCH"] = str(self.settings.arch)
            kwargs["MSVC_VERSION"] = "{:.1f}".format(float(msvs_toolset(self).lstrip("v")) / 10)
            kwargs["ZLIB_LIBNAME"] = f"{self.dependencies['zlib'].cpp_info.libs[0]}"
            env = Environment()
            env.define("OPENSSL_LIBS", os.pathsep.join(f"{lib}.lib" for lib in self.dependencies["openssl"].cpp_info.aggregated_components().libs))
            env.vars(self).save_script("conanbuild_msvc")
        else:
            kwargs["LIBS"] = " ".join(libs)

        escape_str = lambda x: f'"{x}"'
        scons_args = " ".join([escape_str(s) for s in args] + [f"{k}={escape_str(v)}" for k, v in kwargs.items()])
        save(self, os.path.join(self.source_folder, "scons_args"), scons_args)

    def _patch_sources(self):
        apply_conandata_patches(self)
        pc_in = os.path.join(self.source_folder, "build", "serf.pc.in")
        save(self, pc_in, load(self, pc_in))

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            self.run("scons {}".format(load(self, "scons_args")))

    @property
    def _static_ext(self):
        return "a"

    @property
    def _shared_ext(self):
        if is_apple_os(self):
            return "dylib"
        if self.settings.os == "Windows":
            return "dll"
        return "so"

    @property
    def _version_major(self):
        return Version(self.version).major

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            self.run(f'scons install -Y "{self.source_folder}"')

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.settings.os == "Windows":
            rm(self, "*.exp", os.path.join(self.package_folder, "lib"), recursive=True)
            rm(self, "*.pdb", os.path.join(self.package_folder, "lib"), recursive=True)
            if self.options.shared:
                rm(self, f"serf-{self._version_major}.*", os.path.join(self.package_folder, "lib"), recursive=True)
                mkdir(self, os.path.join(self.package_folder, "bin"))
                os.rename(os.path.join(self.package_folder, "lib", f"libserf-{self._version_major}.dll"),
                          os.path.join(self.package_folder, "bin", f"libserf-{self._version_major}.dll"))
            else:
                rm(self, f"libserf-{self._version_major}.*", os.path.join(self.package_folder, "lib"), recursive=True)
        else:
            ext_to_remove = self._static_ext if self.options.shared else self._shared_ext
            for fn in os.listdir(os.path.join(self.package_folder, "lib")):
                if any(re.finditer("\\.{}(\.?|$)".format(ext_to_remove), fn)):
                    os.unlink(os.path.join(self.package_folder, "lib", fn))
            fix_apple_shared_install_name(self)

    def package_info(self):
        libprefix = ""
        if self.settings.os == "Windows" and self.options.shared:
            libprefix = "lib"
        version_major = Version(self.version).major
        libname = f"{libprefix}serf-{version_major}"
        self.cpp_info.libs = [libname]
        self.cpp_info.includedirs.append(os.path.join("include", f"serf-{version_major}"))
        self.cpp_info.set_property("pkg_config_name", libname)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["user32", "advapi32", "gdi32", "ws2_32", "crypt32", "mswsock", "rpcrt4", "secur32"]
