from conans import ConanFile, tools, CMake
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration
import os, shutil, glob

# pylint: disable=missing-class-docstring,missing-function-docstring


class Llvm(ConanFile):
    name = "llvm"
    description = "The LLVM Project is a collection of modular and reusable compiler and toolchain technologies"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/llvm/llvm-project"
    license = "Apache-2.0"
    topics = "cpp", "compiler", "tooling", "clang"

    # Conan settings
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    # Recipe custom stuff
    _source_subfolder = "source_subfolder"

    # https://llvm.org/docs/CMake.html#frequently-used-llvm-related-variables
    _projects = [
        "clang",
        "clang-tools-extra",
        "cross-project-tests",
        "libc",
        "libclc",
        "lld",
        "lldb",
        "openmp",
        "polly",
        "pstl",
    ]
    _runtimes = [
        "compiler-rt",
        "libc",
        "libcxx",
        "libcxxabi",
        "libunwind",
        "openmp",
    ]

    _cmake = None

    # Recipe options
    options = {
        **{
            # "shared": [True, False], # TODO(ruilvo)
            "fPIC": [True, False],
            "allow_debug_builds": [True, False],
            "allow_parallel_builds": [True, False],
            "limit_simultaneous_link_jobs": [True, False],
        },
        **{"with_project_" + project: [True, False] for project in _projects},
        **{"with_runtime_" + runtime: [True, False] for runtime in _runtimes},
    }
    default_options = {
        **{
            # "shared": False,
            "fPIC": True,
            "allow_debug_builds": False,
            "allow_parallel_builds": False,
            "limit_simultaneous_link_jobs": False,
        },
        **{"with_project_" + project: False for project in _projects},
        **{"with_runtime_" + runtime: False for runtime in _runtimes},
    }
    generators = "cmake_find_package"

    # Recipe helpers
    @property
    def _is_msvc(self):
        return (
            self.settings.compiler == "Visual Studio"
            or self.settings.compiler == "msvc"
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        enabled_projects = [
            project
            for project in self._projects
            if getattr(self.options, "with_project_" + project)
        ]
        enabled_runtimes = [
            runtime
            for runtime in self._runtimes
            if getattr(self.options, "with_runtime_" + runtime)
        ]

        cmake_defs = {
            "LLVM_ENABLE_PROJECTS": ";".join(enabled_projects),
            "LLVM_ENABLE_RUNTIMES": ";".join(enabled_runtimes),
            "LLVM_ENABLE_BINDINGS": False,
            # LLVM_BUILD_LLVM_DYLIB  # TODO(ruilvo): for then shared is enabled
        }
        if self.options.get("limit_simultaneous_link_jobs", False):
            cmake_defs["LLVM_PARALLEL_LINK_JOBS"] = 1

        self._cmake = CMake(self, self.options.get("allow_parallel_builds", True))
        self._cmake.configure(
            defs=cmake_defs,
            source_folder=os.path.join(self._source_subfolder, "llvm"),
        )
        return self._cmake

    # Conan methods
    def build_requirements(self):
        self.build_requires("cmake/3.21.3")

    # LLVM requires a bunch of other things during build as options... In the future,
    # complete this with them.

    def config_options(self):
        if self.settings.get("os", False) == "Windows":
            del self.options.fPIC

    def configure(self):
        pass

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "14")

    def validate(self):
        if (
            self.settings.compiler == "gcc"
            and tools.Version(self.settings.compiler.version) < "10"
        ):
            raise ConanInvalidConfiguration(
                "Compiler version too low for this package."
            )

        if (
            self.settings.compiler == "Visual Studio"
            and Version(self.settings.compiler.version) < "16.4"
            # missing check for equivalent msvc version
        ):
            raise ConanInvalidConfiguration(
                "An up to date version of Microsoft Visual Studio 2019 or newer is required."
            )

        if self.settings.build_type == "Debug" and not self.options.get(
            "allow_debug_builds", False
        ):
            raise ConanInvalidConfiguration(
                "Can't make a Debug build without `allow_debug_builds: True`."
            )

        for project in self._projects:
            for runtime in self._runtimes:
                if self.options.get(
                    "with_project_" + project, False
                ) and self.options.get("with_runtime_" + runtime, False):
                    raise ConanInvalidConfiguration(
                        "Can't enable both project and runtime for a module."
                    )

        if self._is_msvc:
            if self.options.get("with_runtime_libc", False):
                raise ConanInvalidConfiguration("Can't build libc as runtime on MSVC.")
            if self.options.get("with_runtime_libcxxabi", False):
                raise ConanInvalidConfiguration("Can't build libcxxabi on Windows.")
            if self.options.get("with_runtime_libunwind", False):
                raise ConanInvalidConfiguration("Can't build libunwind on Windows.")
            if self.options.get("with_project_cross-project-tests", False):
                raise ConanInvalidConfiguration(
                    "Can't build cross-project-tests on Windows."
                )

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True
        )

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy(
            "LICENSE.TXT",
            src=os.path.join(self._source_subfolder, "clang"),
            dst="licenses",
            keep_path=False,
        )

        ignore = ["share", "libexec", "**/Find*.cmake", "**/*Config.cmake"]

        for ignore_entry in ignore:
            ignore_glob = os.path.join(self.package_folder, ignore_entry)

            for ignore_path in glob.glob(ignore_glob, recursive=True):
                self.output.info(
                    'Remove ignored file/directory "{}" from package'.format(
                        ignore_path
                    )
                )

                if os.path.isfile(ignore_path):
                    os.remove(ignore_path)
                else:
                    shutil.rmtree(ignore_path)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.builddirs = ["lib/cmake"]
