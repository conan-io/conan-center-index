# GDAL 3.5+ CMake conan recipe

## Remaining package issues:

- test package does not link with `-o gdal:shared=False`
- `gdal:with_libiconv` produce link errors

## Dependency issues

- if `armadillo:use_hdf5=True`, there is an include error
- `with_poppler` and `with_kml` have a boost version conflict

# Testing

```
conan create \
  -o gdal:shared=True \
  -o libcurl:shared=True \
  -o openssl:shared=True \
  -o libxml2:shared=True \
  -o hdf5:shared=True \
  -o armadillo:use_hdf5=False \
  -o gdal:blosc=True \
  -o gdal:with_armadillo=True \
  -o gdal:with_arrow=True \
  -o gdal:with_cfitsio=True \
  -o gdal:with_cryptopp=True \
  -o gdal:with_expat=True \
  -o gdal:with_hdf5=True \
  -o gdal:with_libcurl=True \
  -o gdal:with_libiconv=False \
  -o gdal:with_libkml=False \
  -o gdal:with_libxml2=True \
  -o gdal:with_lz4=True \
  -o gdal:with_openssl=True \
  -o gdal:with_pg=True \
  -o gdal:with_poppler=True \
  -o gdal:with_zstd=True \
  . "gdal/3.5.1@"  --build=missing
```
