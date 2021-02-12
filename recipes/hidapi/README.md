# conan-hidapi

conan-hidapi is a conan package for [libusb/hidapi](https://github.com/libusb/hidapi).

## Package Status

| Bintray | Windows | Linux & macOS |
|:--------:|:---------:|:-----------------:|
|[ ![Download](https://api.bintray.com/packages/canmor/conan/hidapi%3Acanmor/images/download.svg) ](https://bintray.com/canmor/conan/hidapi%3Acanmor/_latestVersion)|[![Build status](https://ci.appveyor.com/api/projects/status/6w6vl7a4vcnqrjo4?svg=true)](https://ci.appveyor.com/project/canmor/conan-hidapi)|[![Build Status](https://travis-ci.org/canmor/conan-hidapi.svg?branch=master)](https://travis-ci.org/canmor/conan-hidapi)|

## Conan.io Information

This packages can be found in the my personal Conan repository:

[Conan Repository on Bintray](https://bintray.com/canmor/conan)

*Note: You can click the "Set Me Up" button on the Bintray page above for instructions on using packages from this repository.*

## Known Issues

* Not support x64 for Windows

    [libusb/hidapi](https://github.com/libusb/hidapi) provides a `sln` file to build for Windows, which lack support x64.

If you get an idea to solve one of this issues, please report here or fork.
