from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import stat
import textwrap

required_conan_version = ">=1.54.0"


class UnicornConan(ConanFile):
    name = "unicorn"
    description = "Unicorn is a lightweight multi-platform, multi-architecture CPU emulator framework."
    topics = ("emulator", "security", "arm", "framework", "cpu", "mips", "x86-64", "reverse-engineering", "x86", "arm64", "sparc", "m68k")
    homepage = "https://www.unicorn-engine.org/"
    url = "https://github.com/conan-io/conan-center-index"
    license = ("GPL-2-or-later", "LGPL-2-or-later")
    package_type = "library"
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

    def _supported_archs(self, info=False):
        """
        Get supported architectures of the current build/package (depends on self.options.supported_archs)
        :return: sorted list of strings
        """
        options = self.info.options if info else self.options
        return sorted(set(str(options.supported_archs).split(",")))

    @property
    def _needs_jwasm(self):
        return self.settings.os == "Windows" and not is_msvc(self)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        self.options.supported_archs = ",".join(self._all_supported_archs)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        # normalize the supported_archs option (sorted+comma separated)
        self.info.options.supported_archs = ",".join(self._supported_archs(info=True))

    def validate(self):
        unsupported_archs = [arch for arch in self._supported_archs() if arch not in self._all_supported_archs]
        if unsupported_archs:
            raise ConanInvalidConfiguration(
                f"Invalid arch(s) in supported_archs option: {unsupported_archs}\n"
                f"Valid supported architectures are: {self._all_supported_archs}"
            )
        if "arm" in self.settings.arch:
            # FIXME: will/should be fixed with unicorn 2 (https://github.com/unicorn-engine/unicorn/issues/1379)
            raise ConanInvalidConfiguration("arm builds of unicorn are currently unsupported")

    def build_requirements(self):
        if self._needs_jwasm:
            self.tool_requires("jwasm/2.13")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _jwasm_wrapper(self):
        return os.path.join(self.build_folder, "jwasm_wrapper.py")

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = CMakeToolchain(self)
        tc.variables["UNICORN_INSTALL"] = True
        tc.variables["UNICORN_BUILD_SAMPLES"] = False
        tc.cache_variables["UNICORN_ARCH"] = ";".join(self._supported_archs())
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

    def _patch_sources(self):
        apply_conandata_patches(self)
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

    def build(self):
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
        if Version(self.version) >= "2.0.0" and self.options.shared:
            rm(self, "*unicorn.a", os.path.join(self.package_folder, "lib"))
            rm(self, "*unicorn.lib", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "unicorn")
        suffix = "-import" if Version(self.version) >= "2.0.0" and is_msvc(self) and self.options.shared else ""
        self.cpp_info.libs = [f"unicorn{suffix}"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["m", "pthread"]
