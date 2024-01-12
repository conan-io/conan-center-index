/** \file
 * Header for classes representing a Windows directory tree.
 */

#pragma once

#include <iostream>
#include <fmt/ostream.h>
#include "tree-base.hpp"
#include "primitives.hpp"


/**
 * Namespace for classes representing a Windows directory tree.
 */
/**
 * \dot
 * digraph example {
 *   node [shape=record, fontname=Helvetica, fontsize=10];
 *   Directory [ label="Directory" URL="\ref directory::Directory"];
 *   Drive [ label="Drive" URL="\ref directory::Drive"];
 *   Entry [ label="Entry" URL="\ref directory::Entry", style=dotted];
 *   File [ label="File" URL="\ref directory::File"];
 *   Mount [ label="Mount" URL="\ref directory::Mount"];
 *   System [ label="System" URL="\ref directory::System"];
 *   Entry -> Directory [ arrowhead=open, style=dotted ];
 *   Entry -> File [ arrowhead=open, style=dotted ];
 *   Entry -> Mount [ arrowhead=open, style=dotted ];
 *   Directory -> Entry [ label="entries*", arrowhead=open, style=bold, fontname=Helvetica, fontsize=10];
 *   prim0 [ label="primitives::Letter" URL="\ref primitives::Letter"];
 *   Drive -> prim0 [ label="letter", arrowhead=normal, style=solid, fontname=Helvetica, fontsize=10];
 *   Drive -> Directory [ label="root_dir", arrowhead=normal, style=solid, fontname=Helvetica, fontsize=10];
 *   prim1 [ label="primitives::String" URL="\ref primitives::String"];
 *   Entry -> prim1 [ label="name", arrowhead=normal, style=solid, fontname=Helvetica, fontsize=10];
 *   prim2 [ label="primitives::String" URL="\ref primitives::String"];
 *   File -> prim2 [ label="contents", arrowhead=normal, style=solid, fontname=Helvetica, fontsize=10];
 *   Mount -> Directory [ label="target@", arrowhead=normal, style=dashed, fontname=Helvetica, fontsize=10];
 *   System -> Drive [ label="drives+", arrowhead=normal, style=bold, fontname=Helvetica, fontsize=10];
 * }
 * \enddot
 */
namespace directory {

// Base classes used to construct the tree.
using Base = tree::base::Base;
template <class T> using Maybe   = tree::base::Maybe<T>;
template <class T> using One     = tree::base::One<T>;
template <class T> using Any     = tree::base::Any<T>;
template <class T> using Many    = tree::base::Many<T>;
template <class T> using OptLink = tree::base::OptLink<T>;
template <class T> using Link    = tree::base::Link<T>;

// Forward declarations for all classes.
class Node;
class Directory;
class Drive;
class Entry;
class File;
class Mount;
class System;
class VisitorBase;
template <typename T = void>
class Visitor;
class RecursiveVisitor;
class Dumper;
class JsonDumper;

/**
 * Enumeration of all node types.
 */
enum class NodeType {
    Directory,
    Drive,
    File,
    Mount,
    System
};

/**
 * Main class for all nodes.
 */
class Node : public Base {
public:

    /**
     * Returns the `NodeType` of this node.
     */
    virtual NodeType type() const = 0;

    /**
     * Returns a shallow copy of this node.
     */
    virtual One<Node> copy() const = 0;

    /**
     * Returns a deep copy of this node.
     */
    virtual One<Node> clone() const = 0;

    /**
     * Value-based equality operator. Ignores annotations!
     */
    virtual bool equals(const Node& rhs) const = 0;

    /**
     * Pointer-based equality operator.
     */
    virtual bool operator==(const Node& rhs) const = 0;

    /**
     * Pointer-based inequality operator.
     */
    inline bool operator!=(const Node& rhs) const {
        return !(*this == rhs);
    }

protected:

    /**
     * Internal helper method for visitor pattern.
     */
    virtual void visit_internal(VisitorBase &visitor, void *retval=nullptr) = 0;

public:

    /**
     * Visit this object.
     */
    template <typename T>
    T visit(Visitor<T> &visitor);

    /**
     * Writes a debug dump of this node to the given stream.
     */
    void dump(std::ostream &out=std::cout, int indent=0);

    /**
     * Writes a JSON dump of this node to the given stream.
     */
    void dump_json(std::ostream &out=std::cout);

    /**
     * Alternate debug dump that represents links and node uniqueness via
     * sequence number tags.
     */
    void dump_seq(std::ostream &out=std::cout, int indent=0);

    /**
     * Interprets this node to a node of type Directory. Returns null if it has
     * the wrong type.
     */
    virtual Directory *as_directory();

    /**
     * Interprets this node to a node of type Directory. Returns null if it has
     * the wrong type.
     */
    virtual const Directory *as_directory() const;

    /**
     * Interprets this node to a node of type Drive. Returns null if it has the
     * wrong type.
     */
    virtual Drive *as_drive();

    /**
     * Interprets this node to a node of type Drive. Returns null if it has the
     * wrong type.
     */
    virtual const Drive *as_drive() const;

    /**
     * Interprets this node to a node of type Entry. Returns null if it has the
     * wrong type.
     */
    virtual Entry *as_entry();

    /**
     * Interprets this node to a node of type Entry. Returns null if it has the
     * wrong type.
     */
    virtual const Entry *as_entry() const;

    /**
     * Interprets this node to a node of type File. Returns null if it has the
     * wrong type.
     */
    virtual File *as_file();

    /**
     * Interprets this node to a node of type File. Returns null if it has the
     * wrong type.
     */
    virtual const File *as_file() const;

    /**
     * Interprets this node to a node of type Mount. Returns null if it has the
     * wrong type.
     */
    virtual Mount *as_mount();

    /**
     * Interprets this node to a node of type Mount. Returns null if it has the
     * wrong type.
     */
    virtual const Mount *as_mount() const;

    /**
     * Interprets this node to a node of type System. Returns null if it has the
     * wrong type.
     */
    virtual System *as_system();

    /**
     * Interprets this node to a node of type System. Returns null if it has the
     * wrong type.
     */
    virtual const System *as_system() const;

    /**
     * Serializes this node to the given map.
     */
    virtual void serialize(
        ::tree::cbor::MapWriter &map,
        const ::tree::base::PointerMap &ids
    ) const = 0;

    /**
     * Deserializes the given node.
     */
    static std::shared_ptr<Node> deserialize(
         const ::tree::cbor::MapReader &map,
         ::tree::base::IdentifierMap &ids
    );

};

/**
 * Represents a directory entry.
 */
class Entry : public Node {
public:

    /**
     * Name of the directory entry.
     */
    primitives::String name;

    /**
     * Constructor.
     */
    Entry(const primitives::String &name = primitives::initialize<primitives::String>());

    /**
     * Interprets this node to a node of type Entry. Returns null if it has the
     * wrong type.
     */
    Entry *as_entry() override;

    /**
     * Interprets this node to a node of type Entry. Returns null if it has the
     * wrong type.
     */
    const Entry *as_entry() const override;

    /**
     * Deserializes the given node.
     */
    static std::shared_ptr<Entry> deserialize(const ::tree::cbor::MapReader &map, ::tree::base::IdentifierMap &ids);

};

/**
 * Represents a (sub)directory.
 */
class Directory : public Entry {
public:

    /**
     * The directory contents. Note that directories can be empty.
     */
    Any<Entry> entries;

    /**
     * Constructor.
     */
    Directory(const Any<Entry> &entries = Any<Entry>(), const primitives::String &name = primitives::initialize<primitives::String>());

    /**
     * Registers all reachable nodes with the given PointerMap.
     */
    void find_reachable(::tree::base::PointerMap &map) const override;

    /**
     * Returns whether this `Directory` is complete/fully defined.
     */
    void check_complete(const ::tree::base::PointerMap &map) const override;

    /**
     * Returns the `NodeType` of this node.
     */
    NodeType type() const override;

protected:

    /**
     * Helper method for visiting nodes.
     */
    void visit_internal(VisitorBase &visitor, void *retval) override;

public:

    /**
     * Interprets this node to a node of type Directory. Returns null if it has
     * the wrong type.
     */
    Directory *as_directory() override;

    /**
     * Interprets this node to a node of type Directory. Returns null if it has
     * the wrong type.
     */
    const Directory *as_directory() const override;

    /**
     * Returns a shallow copy of this node.
     */
    One<Node> copy() const override;

    /**
     * Returns a deep copy of this node.
     */
    One<Node> clone() const override;

    /**
     * Value-based equality operator. Ignores annotations!
     */
    bool equals(const Node &rhs) const override;

    /**
     * Pointer-based equality operator.
     */
    bool operator==(const Node &rhs) const override;

    /**
     * Serializes this node to the given map.
     */
    void serialize(
        ::tree::cbor::MapWriter &map,
        const ::tree::base::PointerMap &ids
    ) const override;

    /**
     * Deserializes the given node.
     */
    static std::shared_ptr<Directory> deserialize(const ::tree::cbor::MapReader &map, ::tree::base::IdentifierMap &ids);

};

/**
 * Represents a drive.
 */
class Drive : public Node {
public:

    /**
     * The drive letter used to identify it.
     */
    primitives::Letter letter;

    /**
     * Root directory.
     */
    One<Directory> root_dir;

    /**
     * Constructor.
     */
    Drive(const primitives::Letter &letter = primitives::initialize<primitives::Letter>(), const One<Directory> &root_dir = One<Directory>());

    /**
     * Registers all reachable nodes with the given PointerMap.
     */
    void find_reachable(::tree::base::PointerMap &map) const override;

    /**
     * Returns whether this `Drive` is complete/fully defined.
     */
    void check_complete(const ::tree::base::PointerMap &map) const override;

    /**
     * Returns the `NodeType` of this node.
     */
    NodeType type() const override;

protected:

    /**
     * Helper method for visiting nodes.
     */
    void visit_internal(VisitorBase &visitor, void *retval) override;

public:

    /**
     * Interprets this node to a node of type Drive. Returns null if it has the
     * wrong type.
     */
    Drive *as_drive() override;

    /**
     * Interprets this node to a node of type Drive. Returns null if it has the
     * wrong type.
     */
    const Drive *as_drive() const override;

    /**
     * Returns a shallow copy of this node.
     */
    One<Node> copy() const override;

    /**
     * Returns a deep copy of this node.
     */
    One<Node> clone() const override;

    /**
     * Value-based equality operator. Ignores annotations!
     */
    bool equals(const Node &rhs) const override;

    /**
     * Pointer-based equality operator.
     */
    bool operator==(const Node &rhs) const override;

    /**
     * Serializes this node to the given map.
     */
    void serialize(
        ::tree::cbor::MapWriter &map,
        const ::tree::base::PointerMap &ids
    ) const override;

    /**
     * Deserializes the given node.
     */
    static std::shared_ptr<Drive> deserialize(const ::tree::cbor::MapReader &map, ::tree::base::IdentifierMap &ids);

};

/**
 * Represents a regular file.
 */
class File : public Entry {
public:

    /**
     * The file contents.
     */
    primitives::String contents;

    /**
     * Constructor.
     */
    File(const primitives::String &contents = primitives::initialize<primitives::String>(), const primitives::String &name = primitives::initialize<primitives::String>());

    /**
     * Registers all reachable nodes with the given PointerMap.
     */
    void find_reachable(::tree::base::PointerMap &map) const override;

    /**
     * Returns whether this `File` is complete/fully defined.
     */
    void check_complete(const ::tree::base::PointerMap &map) const override;

    /**
     * Returns the `NodeType` of this node.
     */
    NodeType type() const override;

protected:

    /**
     * Helper method for visiting nodes.
     */
    void visit_internal(VisitorBase &visitor, void *retval) override;

public:

    /**
     * Interprets this node to a node of type File. Returns null if it has the
     * wrong type.
     */
    File *as_file() override;

    /**
     * Interprets this node to a node of type File. Returns null if it has the
     * wrong type.
     */
    const File *as_file() const override;

    /**
     * Returns a shallow copy of this node.
     */
    One<Node> copy() const override;

    /**
     * Returns a deep copy of this node.
     */
    One<Node> clone() const override;

    /**
     * Value-based equality operator. Ignores annotations!
     */
    bool equals(const Node &rhs) const override;

    /**
     * Pointer-based equality operator.
     */
    bool operator==(const Node &rhs) const override;

    /**
     * Serializes this node to the given map.
     */
    void serialize(
        ::tree::cbor::MapWriter &map,
        const ::tree::base::PointerMap &ids
    ) const override;

    /**
     * Deserializes the given node.
     */
    static std::shared_ptr<File> deserialize(const ::tree::cbor::MapReader &map, ::tree::base::IdentifierMap &ids);

};

/**
 * Represents a link to another directory.
 */
class Mount : public Entry {
public:

    /**
     * The directory linked to.
     */
    Link<Directory> target;

    /**
     * Constructor.
     */
    Mount(const Link<Directory> &target = Link<Directory>(), const primitives::String &name = primitives::initialize<primitives::String>());

    /**
     * Registers all reachable nodes with the given PointerMap.
     */
    void find_reachable(::tree::base::PointerMap &map) const override;

    /**
     * Returns whether this `Mount` is complete/fully defined.
     */
    void check_complete(const ::tree::base::PointerMap &map) const override;

    /**
     * Returns the `NodeType` of this node.
     */
    NodeType type() const override;

protected:

    /**
     * Helper method for visiting nodes.
     */
    void visit_internal(VisitorBase &visitor, void *retval) override;

public:

    /**
     * Interprets this node to a node of type Mount. Returns null if it has the
     * wrong type.
     */
    Mount *as_mount() override;

    /**
     * Interprets this node to a node of type Mount. Returns null if it has the
     * wrong type.
     */
    const Mount *as_mount() const override;

    /**
     * Returns a shallow copy of this node.
     */
    One<Node> copy() const override;

    /**
     * Returns a deep copy of this node.
     */
    One<Node> clone() const override;

    /**
     * Value-based equality operator. Ignores annotations!
     */
    bool equals(const Node &rhs) const override;

    /**
     * Pointer-based equality operator.
     */
    bool operator==(const Node &rhs) const override;

    /**
     * Serializes this node to the given map.
     */
    void serialize(
        ::tree::cbor::MapWriter &map,
        const ::tree::base::PointerMap &ids
    ) const override;

    /**
     * Deserializes the given node.
     */
    static std::shared_ptr<Mount> deserialize(const ::tree::cbor::MapReader &map, ::tree::base::IdentifierMap &ids);

};

/**
 * Root node, containing the drives and associated directory trees.
 */
class System : public Node {
public:

    /**
     * The drives available on the system. There must be at least one.
     */
    Many<Drive> drives;

    /**
     * Constructor.
     */
    System(const Many<Drive> &drives = Many<Drive>());

    /**
     * Registers all reachable nodes with the given PointerMap.
     */
    void find_reachable(::tree::base::PointerMap &map) const override;

    /**
     * Returns whether this `System` is complete/fully defined.
     */
    void check_complete(const ::tree::base::PointerMap &map) const override;

    /**
     * Returns the `NodeType` of this node.
     */
    NodeType type() const override;

protected:

    /**
     * Helper method for visiting nodes.
     */
    void visit_internal(VisitorBase &visitor, void *retval) override;

public:

    /**
     * Interprets this node to a node of type System. Returns null if it has the
     * wrong type.
     */
    System *as_system() override;

    /**
     * Interprets this node to a node of type System. Returns null if it has the
     * wrong type.
     */
    const System *as_system() const override;

    /**
     * Returns a shallow copy of this node.
     */
    One<Node> copy() const override;

    /**
     * Returns a deep copy of this node.
     */
    One<Node> clone() const override;

    /**
     * Value-based equality operator. Ignores annotations!
     */
    bool equals(const Node &rhs) const override;

    /**
     * Pointer-based equality operator.
     */
    bool operator==(const Node &rhs) const override;

    /**
     * Serializes this node to the given map.
     */
    void serialize(
        ::tree::cbor::MapWriter &map,
        const ::tree::base::PointerMap &ids
    ) const override;

    /**
     * Deserializes the given node.
     */
    static std::shared_ptr<System> deserialize(const ::tree::cbor::MapReader &map, ::tree::base::IdentifierMap &ids);

};

/**
 * Internal class for implementing the visitor pattern.
 */
class VisitorBase {
public:

    /**
     * Virtual destructor for proper cleanup.
     */
    virtual ~VisitorBase() = default;

protected:

    friend class Node;
    friend class Directory;
    friend class Drive;
    friend class Entry;
    friend class File;
    friend class Mount;
    friend class System;

    /**
     * Internal visitor function for nodes of any type.
     */
    virtual void raw_visit_node(Node &node, void *retval) = 0;

    /**
     * Internal visitor function for `Directory` nodes.
     */
    virtual void raw_visit_directory(Directory &node, void *retval) = 0;

    /**
     * Internal visitor function for `Drive` nodes.
     */
    virtual void raw_visit_drive(Drive &node, void *retval) = 0;

    /**
     * Internal visitor function for `Entry` nodes.
     */
    virtual void raw_visit_entry(Entry &node, void *retval) = 0;

    /**
     * Internal visitor function for `File` nodes.
     */
    virtual void raw_visit_file(File &node, void *retval) = 0;

    /**
     * Internal visitor function for `Mount` nodes.
     */
    virtual void raw_visit_mount(Mount &node, void *retval) = 0;

    /**
     * Internal visitor function for `System` nodes.
     */
    virtual void raw_visit_system(System &node, void *retval) = 0;

};

/**
 * Base class for the visitor pattern for the tree.
 * 
 * To operate on the tree, derive from this class, describe your operation by
 * overriding the appropriate visit functions. and then call
 * `node->visit(your_visitor)`. The default implementations for the
 * node-specific functions fall back to the more generic functions, eventually
 * leading to `visit_node()`, which must be implemented with the desired
 * behavior for unknown nodes.
 */
template <typename T>
class Visitor : public VisitorBase {
protected:

    /**
     * Internal visitor function for nodes of any type.
     */
    void raw_visit_node(Node &node, void *retval) override;

    /**
     * Internal visitor function for `Directory` nodes.
     */
    void raw_visit_directory(Directory &node, void *retval) override;

    /**
     * Internal visitor function for `Drive` nodes.
     */
    void raw_visit_drive(Drive &node, void *retval) override;

    /**
     * Internal visitor function for `Entry` nodes.
     */
    void raw_visit_entry(Entry &node, void *retval) override;

    /**
     * Internal visitor function for `File` nodes.
     */
    void raw_visit_file(File &node, void *retval) override;

    /**
     * Internal visitor function for `Mount` nodes.
     */
    void raw_visit_mount(Mount &node, void *retval) override;

    /**
     * Internal visitor function for `System` nodes.
     */
    void raw_visit_system(System &node, void *retval) override;

public:

    /**
     * Fallback function for nodes of any type.
     */
    virtual T visit_node(Node &node) = 0;

    /**
     * Visitor function for `Directory` nodes.
     */
    virtual T visit_directory(Directory &node) {
        return visit_entry(node);
    }

    /**
     * Visitor function for `Drive` nodes.
     */
    virtual T visit_drive(Drive &node) {
        return visit_node(node);
    }

    /**
     * Fallback function for `Entry` nodes.
     */
    virtual T visit_entry(Entry &node) {
        return visit_node(node);
    }

    /**
     * Visitor function for `File` nodes.
     */
    virtual T visit_file(File &node) {
        return visit_entry(node);
    }

    /**
     * Visitor function for `Mount` nodes.
     */
    virtual T visit_mount(Mount &node) {
        return visit_entry(node);
    }

    /**
     * Visitor function for `System` nodes.
     */
    virtual T visit_system(System &node) {
        return visit_node(node);
    }

};

    /**
     * Internal visitor function for nodes of any type.
     */
    template <typename T>
    void Visitor<T>::raw_visit_node(Node &node, void *retval) {
        if (retval == nullptr) {
            this->visit_node(node);
        } else {
            *((T*)retval) = this->visit_node(node);
        };
    }

    /**
     * Internal visitor function for nodes of any type.
     */
    template <>
    void Visitor<void>::raw_visit_node(Node &node, void *retval);

    /**
     * Internal visitor function for `Directory` nodes.
     */
    template <typename T>
    void Visitor<T>::raw_visit_directory(Directory &node, void *retval) {
        if (retval == nullptr) {
            this->visit_directory(node);
        } else {
            *((T*)retval) = this->visit_directory(node);
        };
    }

    /**
     * Internal visitor function for `Directory` nodes.
     */
    template <>
    void Visitor<void>::raw_visit_directory(Directory &node, void *retval);

    /**
     * Internal visitor function for `Drive` nodes.
     */
    template <typename T>
    void Visitor<T>::raw_visit_drive(Drive &node, void *retval) {
        if (retval == nullptr) {
            this->visit_drive(node);
        } else {
            *((T*)retval) = this->visit_drive(node);
        };
    }

    /**
     * Internal visitor function for `Drive` nodes.
     */
    template <>
    void Visitor<void>::raw_visit_drive(Drive &node, void *retval);

    /**
     * Internal visitor function for `Entry` nodes.
     */
    template <typename T>
    void Visitor<T>::raw_visit_entry(Entry &node, void *retval) {
        if (retval == nullptr) {
            this->visit_entry(node);
        } else {
            *((T*)retval) = this->visit_entry(node);
        };
    }

    /**
     * Internal visitor function for `Entry` nodes.
     */
    template <>
    void Visitor<void>::raw_visit_entry(Entry &node, void *retval);

    /**
     * Internal visitor function for `File` nodes.
     */
    template <typename T>
    void Visitor<T>::raw_visit_file(File &node, void *retval) {
        if (retval == nullptr) {
            this->visit_file(node);
        } else {
            *((T*)retval) = this->visit_file(node);
        };
    }

    /**
     * Internal visitor function for `File` nodes.
     */
    template <>
    void Visitor<void>::raw_visit_file(File &node, void *retval);

    /**
     * Internal visitor function for `Mount` nodes.
     */
    template <typename T>
    void Visitor<T>::raw_visit_mount(Mount &node, void *retval) {
        if (retval == nullptr) {
            this->visit_mount(node);
        } else {
            *((T*)retval) = this->visit_mount(node);
        };
    }

    /**
     * Internal visitor function for `Mount` nodes.
     */
    template <>
    void Visitor<void>::raw_visit_mount(Mount &node, void *retval);

    /**
     * Internal visitor function for `System` nodes.
     */
    template <typename T>
    void Visitor<T>::raw_visit_system(System &node, void *retval) {
        if (retval == nullptr) {
            this->visit_system(node);
        } else {
            *((T*)retval) = this->visit_system(node);
        };
    }

    /**
     * Internal visitor function for `System` nodes.
     */
    template <>
    void Visitor<void>::raw_visit_system(System &node, void *retval);

/**
 * Visitor base class defaulting to DFS pre-order traversal.
 * 
 * The visitor functions for nodes with subnode fields default to DFS traversal
 * in addition to falling back to more generic node types.Links and OptLinks are
 * *not* followed.
 */
class RecursiveVisitor : public Visitor<void> {
public:

    /**
     * Recursive traversal for `Directory` nodes.
     */
    void visit_directory(Directory &node) override;

    /**
     * Recursive traversal for `Drive` nodes.
     */
    void visit_drive(Drive &node) override;

    /**
     * Recursive traversal for `Entry` nodes.
     */
    void visit_entry(Entry &node) override;

    /**
     * Recursive traversal for `File` nodes.
     */
    void visit_file(File &node) override;

    /**
     * Recursive traversal for `Mount` nodes.
     */
    void visit_mount(Mount &node) override;

    /**
     * Recursive traversal for `System` nodes.
     */
    void visit_system(System &node) override;

};

/**
 * Visitor class that debug-dumps a tree to a stream
 */
class Dumper : public RecursiveVisitor {
protected:

    /**
     * Output stream to dump to.
     */
    std::ostream &out;

    /**
     * Current indentation level.
     */
    int indent = 0;

    /**
     * When non-null, the print node IDs from here instead of link contents.
     */
    ::tree::base::PointerMap *ids;
    /**
     * Whether we're printing the contents of a link.
     */
    bool in_link = false;

    /**
     * Writes the current indentation level's worth of spaces.
     */
    void write_indent();

public:

    /**
     * Construct a dumping visitor.
     */
    Dumper(std::ostream &out, int indent=0, ::tree::base::PointerMap *ids = nullptr) : out(out), indent(indent), ids(ids) {};

    /**
     * Dumps a `Node`.
     */
    void visit_node(Node &node) override;
    /**
     * Dumps a `Directory` node.
     */
    void visit_directory(Directory &node) override;

    /**
     * Dumps a `Drive` node.
     */
    void visit_drive(Drive &node) override;

    /**
     * Dumps a `Entry` node.
     */
    void visit_entry(Entry &node) override;

    /**
     * Dumps a `File` node.
     */
    void visit_file(File &node) override;

    /**
     * Dumps a `Mount` node.
     */
    void visit_mount(Mount &node) override;

    /**
     * Dumps a `System` node.
     */
    void visit_system(System &node) override;

};

/**
 * Visitor class that JSON dumps a tree to a stream
 */
class JsonDumper : public RecursiveVisitor {
protected:

    /**
     * Output stream to dump to.
     */
    std::ostream &out;
    /**
     * Whether we're printing the contents of a link.
     */
    bool in_link = false;
public:

    /**
     * Construct a dumping visitor.
     */
    JsonDumper(std::ostream &out) : out(out) {};

    /**
     * JSON dumps a `Node`.
     */
    void visit_node(Node &node) override;
    /**
     * JSON dumps a `Directory` node.
     */
    void visit_directory(Directory &node) override;

    /**
     * JSON dumps a `Drive` node.
     */
    void visit_drive(Drive &node) override;

    /**
     * JSON dumps a `Entry` node.
     */
    void visit_entry(Entry &node) override;

    /**
     * JSON dumps a `File` node.
     */
    void visit_file(File &node) override;

    /**
     * JSON dumps a `Mount` node.
     */
    void visit_mount(Mount &node) override;

    /**
     * JSON dumps a `System` node.
     */
    void visit_system(System &node) override;

};

/**
 * Visit this object.
 */
template <typename T>
T Node::visit(Visitor<T> &visitor) {
    T retval;
    this->visit_internal(visitor, &retval);
    return retval;
}

/**
 * Visit this object.
 */
template <>
void Node::visit(Visitor<void> &visitor);

/**
 * Stream << overload for tree nodes (writes debug dump).
 */
std::ostream &operator<<(std::ostream &os, const Node &object);

} // namespace directory

/**
 * std::ostream support via fmt (uses operator<<).
 */
template <> struct fmt::formatter<directory::Directory> : ostream_formatter {};
template <> struct fmt::formatter<directory::Drive> : ostream_formatter {};
template <> struct fmt::formatter<directory::Entry> : ostream_formatter {};
template <> struct fmt::formatter<directory::File> : ostream_formatter {};
template <> struct fmt::formatter<directory::Mount> : ostream_formatter {};
template <> struct fmt::formatter<directory::System> : ostream_formatter {};
