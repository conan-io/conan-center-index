from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import functools
import os

required_conan_version = ">=1.43.0"

class ZXingCppConan(ConanFile):
    name = "zxing-cpp"
    description = "c++14 port of ZXing, a barcode scanning library"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nu-book/zxing-cpp"
    topics = ("zxing", "barcode", "scanner", "generator")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_encoders": [True, False],
        "enable_decoders": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_encoders": True,
        "enable_decoders": True,
    }

    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compiler_cpp14_support(self):
        return {
            "gcc": "5" if tools.Version(self.version) < "1.2" else "6",
            "Visual Studio": "14",
            "clang": "3.4",
            "apple-clang": "3.4",
        }

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 14)
        try:
            minimum_required_version = self._compiler_cpp14_support[str(self.settings.compiler)]
            if self.settings.compiler.version < tools.Version(minimum_required_version):
                raise ConanInvalidConfiguration("This compiler is too old. This library needs a compiler with c++14 support")
        except KeyError:
            self.output.warn("This recipe might not support the compiler. Consider adding it.")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)
        min_version = self._compiler_cpp14_support.get(str(self.settings.compiler))
        if min_version and tools.Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(
                "This compiler is too old. {} needs a compiler with c++14 support".format(self.name)
            )
        # FIXME: This is a workaround for "The system cannot execute the specified program."
        if tools.Version(self.version) == "1.3.0" and is_msvc_static_runtime(self) and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration("{}/{} doesn't support MT + Debug.".format(self.name, self.version))
        if is_msvc_static_runtime(self) and self.options.shared:
            raise ConanInvalidConfiguration("MT + DLL is not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        if tools.Version(self.version) < "1.1":
            cmake.definitions["ENABLE_ENCODERS"] = self.options.enable_encoders
            cmake.definitions["ENABLE_DECODERS"] = self.options.enable_decoders
        else:
            cmake.definitions["BUILD_WRITERS"] = self.options.enable_encoders
            cmake.definitions["BUILD_READERS"] = self.options.enable_decoders
            cmake.definitions["BUILD_EXAMPLES"] = False
            cmake.definitions["BUILD_BLACKBOX_TESTS"] = False
        if is_msvc(self):
            cmake.definitions["LINK_CPP_STATICALLY"] = "MT" in str(self.settings.compiler.runtime)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ZXing")
        self.cpp_info.set_property("cmake_target_name", "ZXing::ZXing")
        self.cpp_info.set_property("pkg_config_name", "zxing")
        self.cpp_info.libs = ["ZXingCore" if tools.Version(self.version) < "1.1" else "ZXing"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "ZXing"
        self.cpp_info.names["cmake_find_package_multi"] = "ZXing"
        self.cpp_info.names["pkg_config"] = "zxing"
