/** \file
 * Defines primitives used in the generated directory tree structure.
 */

#pragma once

#include <string>

/**
 * Namespace with primitives used in the generated directory tree structure.
 */
namespace primitives {

/**
 * Letter primitive, used to represent drive letters.
 */
using Letter = char;

/**
 * Strings, used to represent filenames and file contents.
 */
using String = std::string;

/**
 * Initialization function. This must be specialized for any types used as
 * primitives in a tree that are actual C primitives (int, char, bool, etc),
 * as these are not initialized by the T() construct.
 */
template <class T>
T initialize() { return T(); };

/**
 * Declare the default initializer for drive letters. It's declared inline
 * to avoid having to make a cpp file just for this.
 */
template <>
inline Letter initialize<Letter>() {
    return 'A';
}

/**
 * Serialization function. This must be specialized for any types used as
 * primitives in a tree. The default implementation doesn't do anything.
 */
template <typename T>
void serialize(const T &obj, tree::cbor::MapWriter &map) {
}

/**
 * Serialization function for Letter.
 */
template <>
inline void serialize<Letter>(const Letter &obj, tree::cbor::MapWriter &map) {
    map.append_int("val", obj);
}

/**
 * Serialization function for String.
 */
template <>
inline void serialize<String>(const String &obj, tree::cbor::MapWriter &map) {
    map.append_string("val", obj);
}

/**
 * Deserialization function. This must be specialized for any types used as
 * primitives in a tree. The default implementation doesn't do anything.
 */
template <typename T>
T deserialize(const tree::cbor::MapReader &map) {
    return initialize<T>();
}

/**
 * Deserialization function for Letter.
 */
template <>
inline Letter deserialize<Letter>(const tree::cbor::MapReader &map) {
    return map.at("val").as_int();
}

/**
 * Deserialization function for String.
 */
template <>
inline String deserialize<String>(const tree::cbor::MapReader &map) {
    return map.at("val").as_string();
}

} // namespace primitives
