from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanException
from contextlib import contextmanager
import glob
import os
import re


class SerfConan(ConanFile):
    name = "serf"
    description = "The serf library is a high performance C-based HTTP client library built upon the Apache Portable Runtime (APR) library."
    license = "Apache-2.0"
    topics = ("conan", "serf", "apache", "http", "library")
    homepage = "https://serf.apache.org/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "patches/**"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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

    def requirements(self):
        self.requires("apr-util/1.6.1")
        self.requires("zlib/1.2.12")
        self.requires("openssl/3.0.3")

    def build_requirements(self):
        self.build_requires("scons/4.3.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(glob.glob("serf-*")[0], self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        pc_in = os.path.join(self._source_subfolder, "build", "serf.pc.in")
        tools.files.save(self, pc_in, tools.files.load(self, pc_in))

    @property
    def _cc(self):
        if tools.get_env("CC"):
            return tools.get_env("CC")
        if tools.is_apple_os(self.settings.os):
            return "clang"
        return {
            "Visual Studio": "cl",
        }.get(str(self.settings.compiler), str(self.settings.compiler))

    def _lib_path_arg(self, path):
        argname = "LIBPATH:" if self.settings.compiler == "Visual Studio" else "L"
        return "-{}'{}'".format(argname, path.replace("\\", "/"))

    @contextmanager
    def _build_context(self):
        extra_env = {}
        if self.settings.compiler == "Visual Studio":
            extra_env["OPENSSL_LIBS"] = ";".join("{}.lib".format(lib) for lib in self.deps_cpp_info["openssl"].libs)
        with tools.environment_append(extra_env):
            with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
                yield

    def build(self):
        self._patch_sources()
        autotools = AutoToolsBuildEnvironment(self)
        args = ["-Y", os.path.join(self.source_folder, self._source_subfolder)]
        kwargs = {
            "APR": self.deps_cpp_info["apr"].rootpath.replace("\\", "/"),
            "APU": self.deps_cpp_info["apr-util"].rootpath.replace("\\", "/"),
            "OPENSSL": self.deps_cpp_info["openssl"].rootpath.replace("\\", "/"),
            "PREFIX": self.package_folder.replace("\\", "/"),
            "LIBDIR": os.path.join(self.package_folder, "lib").replace("\\", "/"),
            "ZLIB": self.deps_cpp_info["zlib"].rootpath.replace("\\", "/"),
            "DEBUG": self.settings.build_type == "Debug",
            "APR_STATIC": not self.options["apr"].shared,
            "CFLAGS": " ".join(self.deps_cpp_info.cflags + (["-fPIC"] if self.options.get_safe("fPIC") else []) + autotools.flags),
            "LINKFLAGS": " ".join(self.deps_cpp_info.sharedlinkflags) + " " + " ".join(self._lib_path_arg(l) for l in self.deps_cpp_info.lib_paths),
            "CPPFLAGS": " ".join("-D{}".format(d) for d in autotools.defines) + " " + " ".join("-I'{}'".format(inc.replace("\\", "/")) for inc in self.deps_cpp_info.include_paths),
            "CC": self._cc,
            "SOURCE_LAYOUT": "False",
        }

        if self.settings.compiler == "Visual Studio":
            kwargs.update({
                "TARGET_ARCH": str(self.settings.arch),
                "MSVC_VERSION": "{:.1f}".format(float(tools.msvs_toolset(self.settings).lstrip("v")) / 10),
            })

        escape_str = lambda x : "\"{}\"".format(x)
        with tools.files.chdir(self, self._source_subfolder):
            with self._build_context():
                    self.run("scons {} {}".format(" ".join(escape_str(s) for s in args), " ".join("{}={}".format(k, escape_str(v)) for k, v in kwargs.items())), run_environment=True)

    @property
    def _static_ext(self):
        return "a"

    @property
    def _shared_ext(self):
        if tools.is_apple_os(self.settings.os):
            return "dylib"
        return {
            "Windows": "dll",
        }.get(str(self.settings.os), "so")

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        with tools.files.chdir(self, self._source_subfolder):
            with self._build_context():
                self.run("scons install -Y \"{}\"".format(os.path.join(self.source_folder, self._source_subfolder)), run_environment=True)

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.settings.os == "Windows":
            for file in glob.glob(os.path.join(self.package_folder, "lib", "*.exp")):
                os.unlink(file)
            for file in glob.glob(os.path.join(self.package_folder, "lib", "*.pdb")):
                os.unlink(file)
            if self.options.shared:
                for file in glob.glob(os.path.join(self.package_folder, "lib", "serf-{}.*".format(self._version_major))):
                    os.unlink(file)
                tools.files.mkdir(self, os.path.join(self.package_folder, "bin"))
                os.rename(os.path.join(self.package_folder, "lib", "libserf-{}.dll".format(self._version_major)),
                          os.path.join(self.package_folder, "bin", "libserf-{}.dll".format(self._version_major)))
            else:
                for file in glob.glob(os.path.join(self.package_folder, "lib", "libserf-{}.*".format(self._version_major))):
                    os.unlink(file)
        else:
            ext_to_remove = self._static_ext if self.options.shared else self._shared_ext
            for fn in os.listdir(os.path.join(self.package_folder, "lib")):
                if any(re.finditer("\\.{}(\.?|$)".format(ext_to_remove), fn)):
                    os.unlink(os.path.join(self.package_folder, "lib", fn))

    @property
    def _version_major(self):
        return self.version.split(".", 1)[0]

    def package_info(self):
        libprefix = ""
        if self.settings.os == "Windows" and self.options.shared:
            libprefix = "lib"
        libname = "{}serf-{}".format(libprefix, self._version_major)
        self.cpp_info.libs = [libname]
        self.cpp_info.includedirs.append(os.path.join("include", "serf-{}".format(self._version_major)))
        self.cpp_info.names["pkg_config"] = libname
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["user32", "advapi32", "gdi32", "ws2_32", "crypt32", "mswsock", "rpcrt4", "secur32"]
