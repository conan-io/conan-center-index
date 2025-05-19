from conan import ConanFile, conan_version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, collect_libs
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"

class PackageConan(ConanFile):
    name = "xml-security-c"
    description = (
        "C++ library is an implementation of the XML Digital Signature and Encryption specifications"
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://santuario.apache.org/cindex.html"
    topics = ("santuario", "xml", "dsig", "enc", "digital-signature", "encryption", "verification")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_xalan": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_xalan": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("xerces-c/3.2.5")
        self.requires("openssl/3.2.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.with_xalan:
            tc.variables["WITH_XALAN"] = "YES"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        for license_file in ("LICENSE.txt", "NOTICE.txt"):
            copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))        
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

        if self.settings.os == "Windows":
            rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        # if package has an official FindPACKAGE.cmake listed in https://cmake.org/cmake/help/latest/manual/cmake-modules.7.html#find-modules
        # examples: bzip2, freetype, gdal, icu, libcurl, libjpeg, libpng, libtiff, openssl, sqlite3, zlib...
        # if package provides a CMake config file (package-config.cmake or packageConfig.cmake, with package::package target, usually installed in <prefix>/lib/cmake/<package>/)
        self.cpp_info.set_property("cmake_file_name", "XmlSecurityC")
        self.cpp_info.set_property("cmake_target_name", "XmlSecurityC::XmlSecurityC")
        # if package provides a pkgconfig file (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        self.cpp_info.set_property("pkg_config_name", "xml-security-c.pc")

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "CoreServices"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        if Version(conan_version).major < 2:
            self.cpp_info.names["cmake_find_package"] = "XmlSecurityC"
            self.cpp_info.names["cmake_find_package_multi"] = "XmlSecurity-C"
