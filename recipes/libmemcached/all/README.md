# libmemcached.conan

### build it to local .conan cache with a conan profile other than `default`
```
conan create . -pr debug12
```

### build it for development of the recipe
```
conan create . demo/testing --keep-build
```

### run tests only
```
conan test test_package libmemcached/1.0.18@demo/testing
```

## TODO:
 - PR this to conanindex
