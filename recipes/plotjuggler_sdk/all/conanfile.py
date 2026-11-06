import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.1"


class PlotjugglerSdkConan(ConanFile):
    name = "plotjuggler_sdk"
    description = (
        "C++20 foundation libraries for PlotJuggler: plugin SDK and plugin host loaders."
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/PlotJuggler/plotjuggler_sdk"
    topics = ("plotjuggler", "plugin-sdk", "telemetry", "data-visualization")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    # The SDK ships as static archives only (host loaders + vocabulary types);
    # there is intentionally no `shared` option. There is deliberately no `fPIC`
    # option either: PlotJuggler plugins are shared objects and the host loaders
    # dlopen() them, so every target hardcodes POSITION_INDEPENDENT_CODE ON
    # upstream. Exposing fPIC would be a no-op knob (CCI requires options to have
    # an observable effect). `with_host` lets consumers that only author plugins
    # skip the host-side loader libraries. `assert_throws` switches PJ_ASSERT
    # from assert() to throwing.
    options = {
        "with_host": [True, False],
        "assert_throws": [True, False],
    }
    default_options = {
        "with_host": True,
        "assert_throws": False,
    }

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        # Tune these against the oldest toolchains you actually intend to
        # support; these are conservative C++20 baselines.
        return {
            "gcc": "11",
            "clang": "14",
            "apple-clang": "14",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # nlohmann_json is in PUBLIC installed headers (config_envelope.hpp,
        # widget_data, plugin_catalog) and is find_dependency()'d by the
        # installed CMake usage, so it must propagate to consumers.
        self.requires("nlohmann_json/3.12.0", transitive_headers=True)

        # fmt and fast_float are header-only, private implementation details:
        # they never appear in an installed pj_base header and are never linked
        # into the archives' public surface. Keep them invisible so they do not
        # propagate to downstream consumers of this static-library package.
        self.requires(
            "fmt/12.1.0",
            headers=True,
            libs=False,
            visible=False,
            transitive_headers=False,
            transitive_libs=False,
        )
        self.requires(
            "fast_float/8.1.0",
            headers=True,
            libs=False,
            visible=False,
            transitive_headers=False,
            transitive_libs=False,
        )

    def build_requirements(self):
        # The SDK's CMakeLists requires CMake >= 3.22; some CCI build images
        # (notably macOS) ship an older one.
        self.tool_requires("cmake/[>=3.22]")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which needs at least "
                f"{self.settings.compiler} {minimum_version} "
                f"(got {self.settings.compiler.version})."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["PJ_INSTALL_SDK"] = True
        tc.cache_variables["PJ_BUILD_TESTS"] = False
        tc.cache_variables["PJ_BUILD_PORTED_PLUGINS"] = False
        # Never fail a third-party package build on a warning from a compiler
        # version upstream has not pinned. Requires the PJ_WARNINGS_AS_ERRORS
        # option (SDK >= the release that added it).
        tc.cache_variables["PJ_WARNINGS_AS_ERRORS"] = False
        tc.cache_variables["PJ_ASSERT_THROWS"] = bool(self.options.assert_throws)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE*",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()

        # Conan Center re-derives the CMake package from package_info() below, so
        # the project-installed find/config/targets files must be removed. Keep
        # PjPluginManifest.cmake — it is a genuine build helper shipped as a
        # cmake_build_module, not a generated find script.
        cmake_dir = os.path.join(self.package_folder, "lib", "cmake", "plotjuggler_sdk")
        rm(self, "plotjuggler_sdkConfig*.cmake", cmake_dir)
        rm(self, "plotjuggler_sdkTargets*.cmake", cmake_dir)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "plotjuggler_sdk")

        # Ship the PjPluginManifest helper as a build module so consumers can
        # call pj_emit_plugin_manifest() after find_package() returns.
        self.cpp_info.set_property(
            "cmake_build_modules",
            [os.path.join("lib", "cmake", "plotjuggler_sdk", "PjPluginManifest.cmake")],
        )

        # --- base ---
        base = self.cpp_info.components["base"]
        base.set_property("cmake_target_name", "plotjuggler_sdk::base")
        base.libs = ["pj_base"]
        base.includedirs = ["include"]
        # assert.hpp is a header that branches on PJ_ASSERT_THROWS at the
        # *consumer's* compile time; upstream exports it PUBLIC on pj_base. The
        # define must ride along or consumers get assert() while the archive was
        # built to throw (and vice versa). Propagated to plugin_sdk/plugin_host
        # via their `requires = ["base", ...]`.
        if self.options.assert_throws:
            base.defines = ["PJ_ASSERT_THROWS"]

        # --- plugin_sdk (umbrella INTERFACE: pj_base + nlohmann_json) ---
        sdk = self.cpp_info.components["plugin_sdk"]
        sdk.set_property("cmake_target_name", "plotjuggler_sdk::plugin_sdk")
        sdk.libs = []  # INTERFACE only
        sdk.includedirs = ["include"]
        sdk.requires = ["base", "nlohmann_json::nlohmann_json"]
        # PJ_DIALOG_PLUGIN's variadic-overload macro needs conformant __VA_ARGS__
        # expansion on MSVC. Upstream sets this as an INTERFACE option on the
        # dialog SDK target, which is dropped when we strip the project's CMake
        # targets — restore it here so MSVC dialog-plugin authors still compile.
        if is_msvc(self):
            sdk.cxxflags = ["/Zc:preprocessor"]

        # --- plugin_host (umbrella linking every host-side loader) ---
        if self.options.with_host:
            host = self.cpp_info.components["plugin_host"]
            host.set_property("cmake_target_name", "plotjuggler_sdk::plugin_host")
            host.libs = [
                "pj_data_source_host",
                "pj_message_parser_host",
                "pj_toolbox_host",
                "pj_dialog_library",
                "pj_plugin_catalog",
                "pj_plugin_loader_detail",
            ]
            host.includedirs = ["include"]
            host.requires = ["base", "nlohmann_json::nlohmann_json"]
            if self.settings.os in ("Linux", "FreeBSD"):
                host.system_libs = ["dl"]
