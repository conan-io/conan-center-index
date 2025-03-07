import os
import re

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, load, mkdir, rm, rmdir, save
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvs_toolset, msvc_runtime_flag
from conan.tools.scm import Version
from conan.tools.scons import SConsDeps

required_conan_version = ">=2.0"


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

    def validate(self):
        if self.settings.build_type == "Debug" and self.settings.compiler == "gcc" and Version(self.settings.compiler.version) == 11:
            # https://github.com/conan-io/conan-center-index/pull/22003#issuecomment-1984297329
            # Fails with 'error adding symbols: File format not recognized'
            raise ConanInvalidConfiguration("Debug build is not supported for GCC 11")

    def build_requirements(self):
        self.tool_requires("scons/4.6.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        pc_in = os.path.join(self.source_folder, "build", "serf.pc.in")
        save(self, pc_in, load(self, pc_in))

    @property
    def _cc(self):
        if "CC" in os.environ:
            return os.environ["CC"]
        if is_apple_os(self):
            return "clang"
        if is_msvc(self):
            return "cl"
        return str(self.settings.compiler)

    def generate(self):
        tc = SConsDeps(self)
        tc.generate()

        kwargs = {}
        kwargs["CC"] = self._cc
        kwargs["PREFIX"] = self.package_folder.replace("\\", "/")
        kwargs["LIBDIR"] = os.path.join(self.package_folder, "lib").replace("\\", "/")
        kwargs["DEBUG"] = self.settings.build_type == "Debug"
        kwargs["SOURCE_LAYOUT"] = False
        kwargs["APR_STATIC"] = not self.dependencies["apr"].options.shared
        kwargs["APR"] = self.dependencies["apr"].package_folder.replace("\\", "/")
        kwargs["APU"] = self.dependencies["apr-util"].package_folder.replace("\\", "/")
        kwargs["OPENSSL"] = self.dependencies["openssl"].package_folder.replace("\\", "/")
        kwargs["ZLIB"] = self.dependencies["zlib"].package_folder.replace("\\", "/")
        if is_msvc(self):
            kwargs["TARGET_ARCH"] = str(self.settings.arch)
            kwargs["MSVC_VERSION"] = "{:.1f}".format(float(msvs_toolset(self).lstrip("v")) / 10)
        scons_args = " ".join(f'{k}="{v}"' for k, v in kwargs.items())
        save(self, os.path.join(self.generators_folder, "scons_args"), scons_args)

    def _patch_sources(self):
        sconstruct = os.path.join(self.source_folder, "SConstruct")
        if is_msvc(self):
            content = load(self, sconstruct)
            content = content.replace("allowed_values=('14.0', '12.0',", "allowed_values=('14.3', '14.2', '14.1', '14.0', '12.0',")
            content = content.replace("zlib.lib", self.dependencies['zlib'].cpp_info.libs[0])
            content = content.replace("['libeay32.lib', 'ssleay32.lib']",
                                      str([f"{lib}.lib" for lib in self.dependencies["openssl"].cpp_info.aggregated_components().libs]))
            content = content.replace("['$OPENSSL/include/openssl']",
                                      "['$OPENSSL/include', '$OPENSSL/include/openssl']")
            content = content.replace("['$APR/include/apr-1', '$APU/include/apr-1']",
                                      "['$APR/include', '$APU/include']")
            content = content.replace("['shell32.lib', 'xml.lib']",
                                      "['shell32.lib']")
            runtime_flag = f", '/{msvc_runtime_flag(self)}'"
            content = content.replace(", '/MDd'", runtime_flag)
            content = content.replace(", '/MD'", runtime_flag)
            save(self, sconstruct, content)

        # Inject SConsDeps
        conandeps = os.path.join(self.generators_folder, "SConscript_conandeps").replace("\\", "/")
        save(self, sconstruct,
             f"\ninfo = SConscript('{conandeps}')\n"
             "env.MergeFlags(info['conandeps'])\n",
             append=True)

    def build(self):
        self._patch_sources()
        args = load(self, os.path.join(self.generators_folder, "scons_args"))
        with chdir(self, self.source_folder):
            self.run(f'scons -Y "{self.source_folder}" {args}')

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
                if any(re.finditer(rf"\.{ext_to_remove}(\.?|$)", fn)):
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
