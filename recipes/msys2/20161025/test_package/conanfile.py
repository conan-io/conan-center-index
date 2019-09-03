#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os


class TestPackage(ConanFile):
        
    def test(self):
        bash = tools.which("bash.exe")
        
        if bash:
            self.output.info("using bash.exe from: " + bash)
        else:
            raise ConanException("No instance of bash.exe could be found on %PATH%")
        
        self.run('bash.exe -c ^"make --version^"')
        self.run('bash.exe -c ^"! test -f /bin/link^"')
        self.run('bash.exe -c ^"! test -f /usr/bin/link^"')
