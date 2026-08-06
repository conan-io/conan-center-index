import os
import re
from conan import ConanFile
from conan.tools.files import get, copy, save, load

required_conan_version = ">=2.0"


class OtlConan(ConanFile):
    name = "otl"
    version = "4.0.498"
    description = "Oracle, ODBC and DB2-CLI Template Library — header-only C++ database access"
    license = "ISC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://otl.sourceforge.net/"
    topics = ("database", "odbc", "oracle", "db2", "header-only")
    package_type = "header-library"
    languages = "C++"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    # The version number in the download URL uses a compact form: 4.0.498 -> 40498
    @property
    def _version_compact(self):
        parts = self.version.split(".")
        return f"{parts[0]}{parts[1]}{parts[2]}"

    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def build(self):
        pass

    def package(self):
        # The zip contains a single versioned header (e.g. otlv40498.h).
        # Install it under a stable name so consumers can #include <otl/otlv4.h>
        src_file = f"otlv{self._version_compact}.h"
        dest = os.path.join(self.package_folder, "include", "otl")
        copy(self, src_file, src=self.source_folder, dst=dest)
        os.rename(os.path.join(dest, src_file), os.path.join(dest, "otlv4.h"))

        # Extract the ISC license from the header (between the === markers)
        header_text = load(self, os.path.join(dest, "otlv4.h"))
        m = re.search(
            r"(// =+\n// ORACLE.*?// =+)",
            header_text, re.DOTALL,
        )
        if m:
            license_text = re.sub(r"^// ?", "", m.group(1), flags=re.MULTILINE)
            save(self, os.path.join(self.package_folder, "licenses", "LICENSE"),
                 license_text)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "otl")
        self.cpp_info.set_property("cmake_target_name", "otl::otl")

    def package_id(self):
        self.info.clear()
