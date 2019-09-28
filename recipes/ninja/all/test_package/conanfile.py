#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile
import os


class TestPackage(ConanFile):

    def test(self):
        self.run("ninja --version")
