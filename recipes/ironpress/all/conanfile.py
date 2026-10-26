from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.files import collect_libs, copy, download, get
import os


required_conan_version = ">=2.0.9"


class IronpressConan(ConanFile):
    name = "ironpress"
    description = "In-process HTML, CSS, and Markdown to PDF renderer"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gastongouron/ironpress"
    topics = ("pdf", "html", "css", "markdown")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    implements = ["auto_shared_fpic"]
    no_copy_source = True

    def layout(self):
        self.folders.source = "src"
        self.folders.build = "build"

    def source(self):
        sources = self.conan_data["sources"][self.version]
        get(self, **sources["archive"], strip_root=True)
        download(
            self,
            **sources["cargo_lock"],
            filename=os.path.join(self.source_folder, "Cargo.lock"),
        )

    def validate(self):
        supported = {
            "Linux": ("x86_64", "armv8"),
            "Macos": ("x86_64", "armv8"),
            "Windows": ("x86_64",),
        }
        os_name = str(self.settings.os)
        architecture = str(self.settings.arch)
        if os_name not in supported or architecture not in supported[os_name]:
            raise ConanInvalidConfiguration(
                f"Ironpress does not publish a native contract for {os_name}/{architecture}."
            )
        if cross_building(self):
            raise ConanInvalidConfiguration(
                "Ironpress requires a native Rust toolchain for the target platform."
            )

    @property
    def _cargo_profile(self):
        return "debug" if self.settings.build_type == "Debug" else "release"

    @property
    def _native_output(self):
        return os.path.join(self.build_folder, "cargo", self._cargo_profile)

    def build(self):
        release = " --release" if self._cargo_profile == "release" else ""
        target_dir = os.path.join(self.build_folder, "cargo")
        manifest = os.path.join(self.source_folder, "Cargo.toml")
        self.run(
            f"cargo build --locked --manifest-path=\"{manifest}\""
            " --package ironpress-ffi"
            f" --target-dir=\"{target_dir}\"{release}"
        )

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        include_dir = os.path.join(self.package_folder, "include")
        copy(
            self,
            "ironpress.h",
            src=os.path.join(self.source_folder, "bindings", "c", "include"),
            dst=include_dir,
        )
        copy(
            self,
            "*.hpp",
            src=os.path.join(self.source_folder, "bindings", "cpp", "include"),
            dst=include_dir,
        )

        if self.options.shared:
            self._package_shared_library()
        else:
            self._package_static_library()

    def _package_shared_library(self):
        if self.settings.os == "Windows":
            copy(
                self,
                "ironpress_ffi.dll",
                src=self._native_output,
                dst=os.path.join(self.package_folder, "bin"),
            )
            copy(
                self,
                "ironpress_ffi.dll.lib",
                src=self._native_output,
                dst=os.path.join(self.package_folder, "lib"),
            )
            return

        extension = "dylib" if self.settings.os == "Macos" else "so"
        copy(
            self,
            f"libironpress_ffi.{extension}",
            src=self._native_output,
            dst=os.path.join(self.package_folder, "lib"),
        )

    def _package_static_library(self):
        filename = (
            "ironpress_ffi.lib"
            if self.settings.os == "Windows"
            else "libironpress_ffi.a"
        )
        copy(
            self,
            filename,
            src=self._native_output,
            dst=os.path.join(self.package_folder, "lib"),
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Ironpress")

        c_api = self.cpp_info.components["c"]
        c_api.set_property("cmake_target_name", "Ironpress::C")
        c_api.set_property("pkg_config_name", "ironpress")
        c_api.libs = collect_libs(self)
        if not self.options.shared:
            c_api.system_libs = self._static_system_libraries()

        cpp_api = self.cpp_info.components["cxx"]
        cpp_api.set_property("cmake_target_name", "Ironpress::CXX")
        cpp_api.requires = ["c"]

    def _static_system_libraries(self):
        if self.settings.os == "Windows":
            return ["kernel32", "ntdll", "userenv", "ws2_32", "dbghelp"]
        if self.settings.os == "Macos":
            return ["iconv", "m"]
        return ["dl", "pthread", "m"]
