from conans import CMake, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import functools
import os
import stat
import textwrap

required_conan_version = ">=1.33.0"


class UnicornConan(ConanFile):
    name = "unicorn"
    description = "Unicorn is a lightweight multi-platform, multi-architecture CPU emulator framework."
    topics = ("emulator", "security", "arm", "framework", "cpu", "mips", "x86-64", "reverse-engineering", "x86", "arm64", "sparc", "m68k")
    homepage = "https://www.unicorn-engine.org/"
    url = "https://github.com/conan-io/conan-center-index"
    license = ("GPL-2-or-later", "LGPL-2-or-later")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "supported_archs": "ANY",  # comma-separated list of archs
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "supported_archs": "",  # defaults to all archs supported by the current version. See `config_options`.
    }

    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _all_supported_archs(self):
        """
        Get all supported architectures of the current version
        :return: sorted list of strings
        """
        return sorted(["aarch64", "arm", "m68k", "mips", "sparc", "x86"])

    @property
    def _supported_archs(self):
        """
        Get supported architectures of the current build/package (depends on self.options.supported_archs)
        :return: sorted list of strings
        """
        return sorted(set(str(self.options.supported_archs).split(",")))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        self.options.supported_archs = ",".join(self._all_supported_archs)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    @property
    def _needs_jwasm(self):
        return self.settings.os == "Windows" and self.settings.compiler != "Visual Studio"

    def build_requirements(self):
        if self._needs_jwasm:
            self.build_requires("jwasm/2.13")

    def validate(self):
        unsupported_archs = [arch for arch in self._supported_archs if arch not in self._all_supported_archs]
        if unsupported_archs:
            self.output.info(f"Valid supported architectures are: {self._all_supported_archs}")
            raise ConanInvalidConfiguration(f"Invalid arch(s) in supported_archs option: {unsupported_archs}")
        if "arm" in self.settings.arch:
            # FIXME: will/should be fixed with unicorn 2 (https://github.com/unicorn-engine/unicorn/issues/1379)
            raise ConanInvalidConfiguration("arm builds of unicorn are currently unsupported")

    def package_id(self):
        # normalize the supported_archs option (sorted+comma separated)
        self.info.options.supported_archs = ",".join(self._supported_archs)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _jwasm_wrapper(self):
        return os.path.join(self.build_folder, "jwasm_wrapper.py")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["UNICORN_INSTALL"] = True
        cmake.definitions["UNICORN_BUILD_SAMPLES"] = False
        cmake.definitions["UNICORN_ARCH"] = " ".join(self._supported_archs)
        if self._needs_jwasm:
            cmake.definitions["CMAKE_ASM_MASM_COMPILER"] = self._jwasm_wrapper
            if self.settings.arch == "x86_64":
                cmake.definitions["CMAKE_ASM_MASM_FLAGS"] = {
                    "x86_64": "-win64",
                    "x86": "-coff",
                }[str(self.settings.arch)]
        cmake.configure()
        return cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self._needs_jwasm:
            tools.save(self._jwasm_wrapper, textwrap.dedent("""\
                #!/usr/bin/env python
                import os
                import sys
                import subprocess
                args = ["jwasm"]
                # Convert '/' options to '-'
                for arg in sys.argv[1:]:
                    if arg in ("-fpic", "-fPIC", "-Wall", "-fvisibility=hidden"):
                        continue
                    if os.path.exists(arg):
                        args.append(arg)
                    elif arg[:1] == "/":
                        args.append("-"+arg[1:])
                    else:
                        args.append(arg)
                print("args:", args)
                subprocess.run(args, check=True)
            """))
            os.chmod(self._jwasm_wrapper, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        self.copy("COPYING.LGPL2", src=self._source_subfolder, dst="licenses")
        self.copy("COPYING_GLIB", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["unicorn"]
        self.cpp_info.names["pkg_config"] = "unicorn"
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["m", "pthread"]
