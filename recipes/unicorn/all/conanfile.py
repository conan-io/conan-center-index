from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir, save, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc
import os
import stat
import textwrap

required_conan_version = ">=1.52.0"


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
        "supported_archs": ["ANY"],  # comma-separated list of archs
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "supported_archs": ["ANY"],  # defaults to all archs supported by the current version. See `config_options`.
    }

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
        return self.settings.os == "Windows" and not is_msvc(self)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        if self._needs_jwasm:
            self.tool_requires("jwasm/2.13")

    def package_id(self):
        # normalize the supported_archs option (sorted+comma separated)
        self.info.options.supported_archs = ",".join(self._supported_archs)

    def validate(self):
        unsupported_archs = [arch for arch in self._supported_archs if arch not in self._all_supported_archs]
        if unsupported_archs:
            self.output.info(f"Valid supported architectures are: {self._all_supported_archs}")
            raise ConanInvalidConfiguration(f"Invalid arch(s) in supported_archs option: {unsupported_archs}")
        if "arm" in self.settings.arch:
            # FIXME: will/should be fixed with unicorn 2 (https://github.com/unicorn-engine/unicorn/issues/1379)
            raise ConanInvalidConfiguration("arm builds of unicorn are currently unsupported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    @property
    def _jwasm_wrapper(self):
        return os.path.join(self.build_folder, "jwasm_wrapper.py")

    def _patch_sources(self):
        if self._needs_jwasm:
            save(self, self._jwasm_wrapper, textwrap.dedent("""\
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

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["UNICORN_INSTALL"] = True
        tc.variables["UNICORN_BUILD_SAMPLES"] = False
        tc.cache_variables["UNICORN_ARCH"] = ";".join(self._supported_archs)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"

        if self._needs_jwasm:
            tc.variables["CMAKE_ASM_MASM_COMPILER"] = self._jwasm_wrapper
            if self.settings.arch == "x86_64":
                tc.variables["CMAKE_ASM_MASM_FLAGS"] = {
                    "x86_64": "-win64",
                    "x86": "-coff",
                }[str(self.settings.arch)]

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for lic in ("COPYING", "COPYING.LGPL2", "COPYING_GLIB"):
            copy(self, lic, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["unicorn"]
        self.cpp_info.set_property("pkg_config_name", "unicorn")
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["m", "pthread"]
