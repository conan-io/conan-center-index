from conans import tools
from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, rmdir, rm, mkdir, rename, chdir, load
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc, VCVars
from conan.tools.apple import is_apple_os
from conan.tools.env import VirtualBuildEnv, Environment
from conan.tools.gnu import AutotoolsToolchain
import os
import re
import json


required_conan_version = ">=1.53.0"


class SerfConan(ConanFile):
    name = "serf"
    description = "The serf library is a high performance C-based HTTP client library built upon the Apache Portable Runtime (APR) library."
    license = "Apache-2.0"
    topics = ("apache", "http", "library", "apr")
    homepage = "https://serf.apache.org/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "patches/**", "SConscript"
    settings = "os", "arch", "compiler", "build_type"
    generators = "scons"
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
        copy(self, "SConscript", src=self.recipe_folder, dst=self.export_sources_folder)

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
        self.requires("apr-util/1.6.1")
        self.requires("zlib/1.2.13")
        self.requires("openssl/3.0.7")

    def build_requirements(self):
        self.tool_requires("scons/4.3.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
 #       pc_in = os.path.join(self.source_folder, "build", "serf.pc.in")
 #       tools.save(pc_in, tools.load(pc_in))

    @property
    def _cc(self):
        if tools.get_env("CC"):
            return tools.get_env("CC")
        if is_apple_os(self):
            return "clang"
        return {
            "Visual Studio": "cl",
            "msvc": "cl",
        }.get(str(self.settings.compiler), str(self.settings.compiler))

    def _lib_path_arg(self, path):
        argname = "LIBPATH:" if is_msvc(self) else "L"
        return "-{}'{}'".format(argname, path.replace("\\", "/"))

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        env = tc.environment()
        env.define("APR", self.dependencies["apr"].package_folder.replace("\\", "/"))
        env.define("APU", self.dependencies["apr-util"].package_folder.replace("\\", "/"))
        env.define("OPENSSL", self.dependencies["openssl"].package_folder.replace("\\", "/"))
        env.define("PREFIX", self.package_folder.replace("\\", "/"))
        env.define("LIBDIR", os.path.join(self.package_folder, "lib").replace("\\", "/"))
        env.define("ZLIB", self.dependencies["zlib"].package_folder.replace("\\", "/"))
        env.define("DEBUG", self.settings.build_type == "Debug")
        env.define("APR_STATIC", not self.dependencies["apr"].options.shared)
        env.define("CFLAGS", " ".join(self.deps_cpp_info.cflags + (["-fPIC"] if self.options.get_safe("fPIC") else []) + tc.cflags))
        env.define("LINKFLAGS", " ".join(self.deps_cpp_info.sharedlinkflags) + " " + " ".join(self._lib_path_arg(l.cpp_info.libdirs) for l in self.dependencies))
        env.define("CPPFLAGS", " ".join("-D{}".format(d) for d in tc.defines) + " " + " ".join("-I'{}'".format(inc.cpp_info.includedirs.replace("\\", "/")) for inc in self.dependencies))
        env.define("CC", self._cc)
        env.define("SOURCE_LAYOUT", "False")
        if is_msvc(self):
            vcvars = VCVars(self)
            vcvars.generate()

            env.define("TARGET_ARCH", str(self.settings.arch))
            env.define("MSVC_VERSION", "{:.1f}".format(float(tools.msvs_toolset(self.settings).lstrip("v")) / 10))

            winenv = Environment()
            winenv.define("OPENSSL_LIBS", ";".join("{}.lib".format(lib) for lib in self.dependencies["openssl"].libs))
            winenvvars = winenv.vars(self)
            winenvvars.save("scons_windows_environment")

        envvars = env.vars(self)
        envvars.save_script("scons.conf")


    def build(self):
        apply_conandata_patches(self)
        args = ["-Y", self.source_folder]
        gen_info = json.loads(load(self, os.path.join(self.generators_folder, "gen_info.conf")))
        escape_str = lambda x : "'{}'".format(x)
        with self._build_context():
            self.run("scons {} {}".format(" ".join(escape_str(s) for s in args), " ".join("{}={}".format(k, escape_str(v)) for k, v in gen_info.items())), run_environment=True)

    @property
    def _static_ext(self):
        return "a"

    @property
    def _shared_ext(self):
        if is_apple_os(self):
            return "dylib"
        return {
            "Windows": "dll",
        }.get(str(self.settings.os), "so")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            with self._build_context():
                self.run("scons install -Y \"{}\"".format(os.path.join(self.source_folder)), run_environment=True)

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.exp", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, f"serf-{Version(self.version).major}.*", os.path.join(self.package_folder, "lib"))
        if self.settings.os == "Windows":
            if self.options.shared:
                mkdir(self, os.path.join(self.package_folder, "bin"))
                rename(self, os.path.join(self.package_folder, "lib", f"libserf-{Version(self.version).major}.dll"),
                             os.path.join(self.package_folder, "bin", f"libserf-{Version(self.version).major}.dll"))
        else:
            ext_to_remove = self._static_ext if self.options.shared else self._shared_ext
            for fn in os.listdir(os.path.join(self.package_folder, "lib")):
                if any(re.finditer(r"\.{}(\.?|$)".format(ext_to_remove), fn)):
                    os.unlink(os.path.join(self.package_folder, "lib", fn))

    def package_info(self):
        libprefix = ""
        if self.settings.os == "Windows" and self.options.shared:
            libprefix = "lib"
        libname = f"{libprefix}serf-{Version(self.version).major}"
        self.cpp_info.libs = [libname]
        self.cpp_info.includedirs.append(os.path.join("include", f"serf-{format(Version(self.version).major)}"))
        self.cpp_info.set_property("", libname)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["user32", "advapi32", "gdi32", "ws2_32", "crypt32", "mswsock", "rpcrt4", "secur32"]
