import os
import shutil
from six import StringIO
from conans import ConanFile, CMake, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"

    def _generate_portable_objects(self):
        os.makedirs(os.path.join(self.build_folder, "po", "es", "LC_MESSAGES"))
        pot_path = os.path.join(self.build_folder, "po", "hello.pot")
        c_path = os.path.join(self.source_folder, "test_package.c")
        self.run("xgettext --msgid-bugs-address=foo@mail.co --package-name=Hello --package-version=1.0 -d hello -k_ -L C -s -o {} {}".format(pot_path, c_path), run_environment=True)

        es_po_path = os.path.join(self.build_folder, "po", "es", "LC_MESSAGES", "hello.po")
        self.run("msginit --no-translator --input={} --locale=es_ES --output={}".format(pot_path, es_po_path), run_environment=True)
        # Translator asks for email. Have to add Language manually
        tools.replace_in_file(es_po_path, "none", "Spanish")
        tools.replace_in_file(es_po_path, '''msgid "Hello World"
msgstr ""''', '''msgid "Hello World"
msgstr "Hola Mundo"''')

        es_mo_path = os.path.join(self.build_folder, "po", "es", "LC_MESSAGES", "hello.mo")
        self.run("msgfmt -o {} {}".format(es_mo_path, es_po_path), run_environment=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            self.output.info("Check working executables")
            for exe in ['gettext', 'ngettext', 'msgcat', 'msgmerge']:
                buffer = StringIO()
                self.run("%s --version" % exe, run_environment=True, output=buffer)
                assert self.deps_cpp_info["gettext"].version in buffer.getvalue()

            self._generate_portable_objects()

            self.output.info("Check working library")
            bin_path = os.path.join("bin", "test_package")
            with tools.environment_append({"LANG": "es_ES"}):
                self.run("%s %s" % (bin_path, os.path.abspath(os.path.join(self.build_folder, "po"))), run_environment=True)
