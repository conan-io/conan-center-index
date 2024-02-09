/** \file
 * Implementation for classes representing a Windows directory tree.
 */

#include "directory.actual.hpp"

namespace directory {

/**
 * Writes a debug dump of this node to the given stream.
 */
void Node::dump(std::ostream &out, int indent) {
    auto dumper = Dumper(out, indent);
    visit(dumper);
}

/**
 * Writes a JSON dump of this node to the given stream.
 */
void Node::dump_json(std::ostream &out) {
    auto dumper = JsonDumper(out);
    visit(dumper);
}

/**
 * Alternate debug dump that represents links and node uniqueness via sequence
 * number tags.
 */
void Node::dump_seq(std::ostream &out, int indent) {
    ::tree::base::PointerMap ids;
    ids.enable_exceptions = false;
    ids.add_ref(*this);
    find_reachable(ids);
    auto dumper = Dumper(out, indent, &ids);
    visit(dumper);
}

/**
 * Interprets this node to a node of type Directory. Returns null if it has the
 * wrong type.
 */
Directory *Node::as_directory() {
    return nullptr;
}

/**
 * Interprets this node to a node of type Directory. Returns null if it has the
 * wrong type.
 */
const Directory *Node::as_directory() const {
    return nullptr;
}

/**
 * Interprets this node to a node of type Drive. Returns null if it has the
 * wrong type.
 */
Drive *Node::as_drive() {
    return nullptr;
}

/**
 * Interprets this node to a node of type Drive. Returns null if it has the
 * wrong type.
 */
const Drive *Node::as_drive() const {
    return nullptr;
}

/**
 * Interprets this node to a node of type Entry. Returns null if it has the
 * wrong type.
 */
Entry *Node::as_entry() {
    return nullptr;
}

/**
 * Interprets this node to a node of type Entry. Returns null if it has the
 * wrong type.
 */
const Entry *Node::as_entry() const {
    return nullptr;
}

/**
 * Interprets this node to a node of type File. Returns null if it has the wrong
 * type.
 */
File *Node::as_file() {
    return nullptr;
}

/**
 * Interprets this node to a node of type File. Returns null if it has the wrong
 * type.
 */
const File *Node::as_file() const {
    return nullptr;
}

/**
 * Interprets this node to a node of type Mount. Returns null if it has the
 * wrong type.
 */
Mount *Node::as_mount() {
    return nullptr;
}

/**
 * Interprets this node to a node of type Mount. Returns null if it has the
 * wrong type.
 */
const Mount *Node::as_mount() const {
    return nullptr;
}

/**
 * Interprets this node to a node of type System. Returns null if it has the
 * wrong type.
 */
System *Node::as_system() {
    return nullptr;
}

/**
 * Interprets this node to a node of type System. Returns null if it has the
 * wrong type.
 */
const System *Node::as_system() const {
    return nullptr;
}

/**
 * Deserializes the given node.
 */
std::shared_ptr<Node> Node::deserialize(
    const ::tree::cbor::MapReader &map,
    ::tree::base::IdentifierMap &ids
) {
    auto type = map.at("@t").as_string();
    if (type == "Directory") return Directory::deserialize(map, ids);
    if (type == "Drive") return Drive::deserialize(map, ids);
    if (type == "File") return File::deserialize(map, ids);
    if (type == "Mount") return Mount::deserialize(map, ids);
    if (type == "System") return System::deserialize(map, ids);
    throw std::runtime_error("Schema validation failed: unexpected node type " + type);
}

/**
 * Constructor.
 */
Entry::Entry(const primitives::String &name)
    : name(name)
{}

/**
 * Interprets this node to a node of type Entry. Returns null if it has the
 * wrong type.
 */
Entry *Entry::as_entry() {
    return dynamic_cast<Entry*>(this);
}

/**
 * Interprets this node to a node of type Entry. Returns null if it has the
 * wrong type.
 */
const Entry *Entry::as_entry() const {
    return dynamic_cast<const Entry*>(this);
}

/**
 * Deserializes the given node.
 */
std::shared_ptr<Entry> Entry::deserialize(const ::tree::cbor::MapReader &map, ::tree::base::IdentifierMap &ids) {
    auto type = map.at("@t").as_string();
    if (type == "File") return File::deserialize(map, ids);
    if (type == "Directory") return Directory::deserialize(map, ids);
    if (type == "Mount") return Mount::deserialize(map, ids);
    throw std::runtime_error("Schema validation failed: unexpected node type " + type);
}

/**
 * Constructor.
 */
Directory::Directory(const Any<Entry> &entries, const primitives::String &name)
    : Entry(name), entries(entries)
{}

/**
 * Registers all reachable nodes with the given PointerMap.
 */
void Directory::find_reachable(::tree::base::PointerMap &map) const {
    (void) map;
    entries.find_reachable(map);
}

/**
 * Returns whether this `Directory` is complete/fully defined.
 */
void Directory::check_complete(const ::tree::base::PointerMap &map) const {
    (void) map;
    entries.check_complete(map);
}

/**
 * Returns the `NodeType` of this node.
 */
NodeType Directory::type() const {
    return NodeType::Directory;
}

/**
 * Helper method for visiting nodes.
 */
void Directory::visit_internal(VisitorBase &visitor, void *retval) {
    visitor.raw_visit_directory(*this, retval);
}

/**
 * Interprets this node to a node of type Directory. Returns null if it has the
 * wrong type.
 */
Directory *Directory::as_directory() {
    return dynamic_cast<Directory*>(this);
}

/**
 * Interprets this node to a node of type Directory. Returns null if it has the
 * wrong type.
 */
const Directory *Directory::as_directory() const {
    return dynamic_cast<const Directory*>(this);
}

/**
 * Returns a shallow copy of this node.
 */
One<Node> Directory::copy() const {
    return tree::base::make<Directory>(*this);
}

/**
 * Returns a deep copy of this node.
 */
One<Node> Directory::clone() const {
    auto node = tree::base::make<Directory>(*this);
    node->entries = this->entries.clone();
    return node;
}

/**
 * Value-based equality operator. Ignores annotations!
 */
bool Directory::equals(const Node &rhs) const {
    if (rhs.type() != NodeType::Directory) return false;
    auto rhsc = dynamic_cast<const Directory&>(rhs);
    if (!this->entries.equals(rhsc.entries)) return false;
    if (this->name != rhsc.name) return false;
    return true;
}

/**
 * Pointer-based equality operator.
 */
bool Directory::operator==(const Node &rhs) const {
    if (rhs.type() != NodeType::Directory) return false;
    auto rhsc = dynamic_cast<const Directory&>(rhs);
    if (this->entries != rhsc.entries) return false;
    if (this->name != rhsc.name) return false;
    return true;
}

/**
 * Serializes this node to the given map.
 */
void Directory::serialize(
    ::tree::cbor::MapWriter &map,
    const ::tree::base::PointerMap &ids
) const {
    (void) ids;
    map.append_string("@t", "Directory");
    auto submap = map.append_map("entries");
    entries.serialize(submap, ids);
    submap.close();
    submap = map.append_map("name");
    primitives::serialize<primitives::String>(name, submap);
    submap.close();
    serialize_annotations(map);
}

/**
 * Deserializes the given node.
 */
std::shared_ptr<Directory> Directory::deserialize(const ::tree::cbor::MapReader &map, ::tree::base::IdentifierMap &ids) {
    (void) ids;
    auto type = map.at("@t").as_string();
    if (type != "Directory") {
        throw std::runtime_error("Schema validation failed: unexpected node type " + type);
    }
    auto node = std::make_shared<Directory>(
        Any<Entry>(map.at("entries").as_map(), ids),
        primitives::deserialize<primitives::String>(map.at("name").as_map())
    );
    node->deserialize_annotations(map);
    return node;
}

/**
 * Constructor.
 */
Drive::Drive(const primitives::Letter &letter, const One<Directory> &root_dir)
    : letter(letter), root_dir(root_dir)
{}

/**
 * Registers all reachable nodes with the given PointerMap.
 */
void Drive::find_reachable(::tree::base::PointerMap &map) const {
    (void) map;
    root_dir.find_reachable(map);
}

/**
 * Returns whether this `Drive` is complete/fully defined.
 */
void Drive::check_complete(const ::tree::base::PointerMap &map) const {
    (void) map;
    root_dir.check_complete(map);
}

/**
 * Returns the `NodeType` of this node.
 */
NodeType Drive::type() const {
    return NodeType::Drive;
}

/**
 * Helper method for visiting nodes.
 */
void Drive::visit_internal(VisitorBase &visitor, void *retval) {
    visitor.raw_visit_drive(*this, retval);
}

/**
 * Interprets this node to a node of type Drive. Returns null if it has the
 * wrong type.
 */
Drive *Drive::as_drive() {
    return dynamic_cast<Drive*>(this);
}

/**
 * Interprets this node to a node of type Drive. Returns null if it has the
 * wrong type.
 */
const Drive *Drive::as_drive() const {
    return dynamic_cast<const Drive*>(this);
}

/**
 * Returns a shallow copy of this node.
 */
One<Node> Drive::copy() const {
    return tree::base::make<Drive>(*this);
}

/**
 * Returns a deep copy of this node.
 */
One<Node> Drive::clone() const {
    auto node = tree::base::make<Drive>(*this);
    node->root_dir = this->root_dir.clone();
    return node;
}

/**
 * Value-based equality operator. Ignores annotations!
 */
bool Drive::equals(const Node &rhs) const {
    if (rhs.type() != NodeType::Drive) return false;
    auto rhsc = dynamic_cast<const Drive&>(rhs);
    if (this->letter != rhsc.letter) return false;
    if (!this->root_dir.equals(rhsc.root_dir)) return false;
    return true;
}

/**
 * Pointer-based equality operator.
 */
bool Drive::operator==(const Node &rhs) const {
    if (rhs.type() != NodeType::Drive) return false;
    auto rhsc = dynamic_cast<const Drive&>(rhs);
    if (this->letter != rhsc.letter) return false;
    if (this->root_dir != rhsc.root_dir) return false;
    return true;
}

/**
 * Serializes this node to the given map.
 */
void Drive::serialize(
    ::tree::cbor::MapWriter &map,
    const ::tree::base::PointerMap &ids
) const {
    (void) ids;
    map.append_string("@t", "Drive");
    auto submap = map.append_map("letter");
    primitives::serialize<primitives::Letter>(letter, submap);
    submap.close();
    submap = map.append_map("root_dir");
    root_dir.serialize(submap, ids);
    submap.close();
    serialize_annotations(map);
}

/**
 * Deserializes the given node.
 */
std::shared_ptr<Drive> Drive::deserialize(const ::tree::cbor::MapReader &map, ::tree::base::IdentifierMap &ids) {
    (void) ids;
    auto type = map.at("@t").as_string();
    if (type != "Drive") {
        throw std::runtime_error("Schema validation failed: unexpected node type " + type);
    }
    auto node = std::make_shared<Drive>(
        primitives::deserialize<primitives::Letter>(map.at("letter").as_map()),
        One<Directory>(map.at("root_dir").as_map(), ids)
    );
    node->deserialize_annotations(map);
    return node;
}

/**
 * Constructor.
 */
File::File(const primitives::String &contents, const primitives::String &name)
    : Entry(name), contents(contents)
{}

/**
 * Registers all reachable nodes with the given PointerMap.
 */
void File::find_reachable(::tree::base::PointerMap &map) const {
    (void) map;
}

/**
 * Returns whether this `File` is complete/fully defined.
 */
void File::check_complete(const ::tree::base::PointerMap &map) const {
    (void) map;
}

/**
 * Returns the `NodeType` of this node.
 */
NodeType File::type() const {
    return NodeType::File;
}

/**
 * Helper method for visiting nodes.
 */
void File::visit_internal(VisitorBase &visitor, void *retval) {
    visitor.raw_visit_file(*this, retval);
}

/**
 * Interprets this node to a node of type File. Returns null if it has the wrong
 * type.
 */
File *File::as_file() {
    return dynamic_cast<File*>(this);
}

/**
 * Interprets this node to a node of type File. Returns null if it has the wrong
 * type.
 */
const File *File::as_file() const {
    return dynamic_cast<const File*>(this);
}

/**
 * Returns a shallow copy of this node.
 */
One<Node> File::copy() const {
    return tree::base::make<File>(*this);
}

/**
 * Returns a deep copy of this node.
 */
One<Node> File::clone() const {
    auto node = tree::base::make<File>(*this);
    return node;
}

/**
 * Value-based equality operator. Ignores annotations!
 */
bool File::equals(const Node &rhs) const {
    if (rhs.type() != NodeType::File) return false;
    auto rhsc = dynamic_cast<const File&>(rhs);
    if (this->contents != rhsc.contents) return false;
    if (this->name != rhsc.name) return false;
    return true;
}

/**
 * Pointer-based equality operator.
 */
bool File::operator==(const Node &rhs) const {
    if (rhs.type() != NodeType::File) return false;
    auto rhsc = dynamic_cast<const File&>(rhs);
    if (this->contents != rhsc.contents) return false;
    if (this->name != rhsc.name) return false;
    return true;
}

/**
 * Serializes this node to the given map.
 */
void File::serialize(
    ::tree::cbor::MapWriter &map,
    const ::tree::base::PointerMap &ids
) const {
    (void) ids;
    map.append_string("@t", "File");
    auto submap = map.append_map("contents");
    primitives::serialize<primitives::String>(contents, submap);
    submap.close();
    submap = map.append_map("name");
    primitives::serialize<primitives::String>(name, submap);
    submap.close();
    serialize_annotations(map);
}

/**
 * Deserializes the given node.
 */
std::shared_ptr<File> File::deserialize(const ::tree::cbor::MapReader &map, ::tree::base::IdentifierMap &ids) {
    (void) ids;
    auto type = map.at("@t").as_string();
    if (type != "File") {
        throw std::runtime_error("Schema validation failed: unexpected node type " + type);
    }
    auto node = std::make_shared<File>(
        primitives::deserialize<primitives::String>(map.at("contents").as_map()),
        primitives::deserialize<primitives::String>(map.at("name").as_map())
    );
    node->deserialize_annotations(map);
    return node;
}

/**
 * Constructor.
 */
Mount::Mount(const Link<Directory> &target, const primitives::String &name)
    : Entry(name), target(target)
{}

/**
 * Registers all reachable nodes with the given PointerMap.
 */
void Mount::find_reachable(::tree::base::PointerMap &map) const {
    (void) map;
    target.find_reachable(map);
}

/**
 * Returns whether this `Mount` is complete/fully defined.
 */
void Mount::check_complete(const ::tree::base::PointerMap &map) const {
    (void) map;
    target.check_complete(map);
}

/**
 * Returns the `NodeType` of this node.
 */
NodeType Mount::type() const {
    return NodeType::Mount;
}

/**
 * Helper method for visiting nodes.
 */
void Mount::visit_internal(VisitorBase &visitor, void *retval) {
    visitor.raw_visit_mount(*this, retval);
}

/**
 * Interprets this node to a node of type Mount. Returns null if it has the
 * wrong type.
 */
Mount *Mount::as_mount() {
    return dynamic_cast<Mount*>(this);
}

/**
 * Interprets this node to a node of type Mount. Returns null if it has the
 * wrong type.
 */
const Mount *Mount::as_mount() const {
    return dynamic_cast<const Mount*>(this);
}

/**
 * Returns a shallow copy of this node.
 */
One<Node> Mount::copy() const {
    return tree::base::make<Mount>(*this);
}

/**
 * Returns a deep copy of this node.
 */
One<Node> Mount::clone() const {
    auto node = tree::base::make<Mount>(*this);
    return node;
}

/**
 * Value-based equality operator. Ignores annotations!
 */
bool Mount::equals(const Node &rhs) const {
    if (rhs.type() != NodeType::Mount) return false;
    auto rhsc = dynamic_cast<const Mount&>(rhs);
    if (!this->target.equals(rhsc.target)) return false;
    if (this->name != rhsc.name) return false;
    return true;
}

/**
 * Pointer-based equality operator.
 */
bool Mount::operator==(const Node &rhs) const {
    if (rhs.type() != NodeType::Mount) return false;
    auto rhsc = dynamic_cast<const Mount&>(rhs);
    if (this->target != rhsc.target) return false;
    if (this->name != rhsc.name) return false;
    return true;
}

/**
 * Serializes this node to the given map.
 */
void Mount::serialize(
    ::tree::cbor::MapWriter &map,
    const ::tree::base::PointerMap &ids
) const {
    (void) ids;
    map.append_string("@t", "Mount");
    auto submap = map.append_map("target");
    target.serialize(submap, ids);
    submap.close();
    submap = map.append_map("name");
    primitives::serialize<primitives::String>(name, submap);
    submap.close();
    serialize_annotations(map);
}

/**
 * Deserializes the given node.
 */
std::shared_ptr<Mount> Mount::deserialize(const ::tree::cbor::MapReader &map, ::tree::base::IdentifierMap &ids) {
    (void) ids;
    auto type = map.at("@t").as_string();
    if (type != "Mount") {
        throw std::runtime_error("Schema validation failed: unexpected node type " + type);
    }
    auto node = std::make_shared<Mount>(
        Link<Directory>(map.at("target").as_map(), ids),
        primitives::deserialize<primitives::String>(map.at("name").as_map())
    );
    auto link = map.at("target").as_map().at("@l");
    if (!link.is_null()) {
        ids.register_link(node->target, link.as_int());
    }
    node->deserialize_annotations(map);
    return node;
}

/**
 * Constructor.
 */
System::System(const Many<Drive> &drives)
    : drives(drives)
{}

/**
 * Registers all reachable nodes with the given PointerMap.
 */
void System::find_reachable(::tree::base::PointerMap &map) const {
    (void) map;
    drives.find_reachable(map);
}

/**
 * Returns whether this `System` is complete/fully defined.
 */
void System::check_complete(const ::tree::base::PointerMap &map) const {
    (void) map;
    drives.check_complete(map);
}

/**
 * Returns the `NodeType` of this node.
 */
NodeType System::type() const {
    return NodeType::System;
}

/**
 * Helper method for visiting nodes.
 */
void System::visit_internal(VisitorBase &visitor, void *retval) {
    visitor.raw_visit_system(*this, retval);
}

/**
 * Interprets this node to a node of type System. Returns null if it has the
 * wrong type.
 */
System *System::as_system() {
    return dynamic_cast<System*>(this);
}

/**
 * Interprets this node to a node of type System. Returns null if it has the
 * wrong type.
 */
const System *System::as_system() const {
    return dynamic_cast<const System*>(this);
}

/**
 * Returns a shallow copy of this node.
 */
One<Node> System::copy() const {
    return tree::base::make<System>(*this);
}

/**
 * Returns a deep copy of this node.
 */
One<Node> System::clone() const {
    auto node = tree::base::make<System>(*this);
    node->drives = this->drives.clone();
    return node;
}

/**
 * Value-based equality operator. Ignores annotations!
 */
bool System::equals(const Node &rhs) const {
    if (rhs.type() != NodeType::System) return false;
    auto rhsc = dynamic_cast<const System&>(rhs);
    if (!this->drives.equals(rhsc.drives)) return false;
    return true;
}

/**
 * Pointer-based equality operator.
 */
bool System::operator==(const Node &rhs) const {
    if (rhs.type() != NodeType::System) return false;
    auto rhsc = dynamic_cast<const System&>(rhs);
    if (this->drives != rhsc.drives) return false;
    return true;
}

/**
 * Serializes this node to the given map.
 */
void System::serialize(
    ::tree::cbor::MapWriter &map,
    const ::tree::base::PointerMap &ids
) const {
    (void) ids;
    map.append_string("@t", "System");
    auto submap = map.append_map("drives");
    drives.serialize(submap, ids);
    submap.close();
    serialize_annotations(map);
}

/**
 * Deserializes the given node.
 */
std::shared_ptr<System> System::deserialize(const ::tree::cbor::MapReader &map, ::tree::base::IdentifierMap &ids) {
    (void) ids;
    auto type = map.at("@t").as_string();
    if (type != "System") {
        throw std::runtime_error("Schema validation failed: unexpected node type " + type);
    }
    auto node = std::make_shared<System>(
        Many<Drive>(map.at("drives").as_map(), ids)
    );
    node->deserialize_annotations(map);
    return node;
}

/**
 * Internal visitor function for nodes of any type.
 */
template <>
void Visitor<void>::raw_visit_node(Node &node, void *retval) {
    (void) retval;
    this->visit_node(node);
}

/**
 * Internal visitor function for `Directory` nodes.
 */
template <>
void Visitor<void>::raw_visit_directory(Directory &node, void *retval) {
    (void) retval;
    this->visit_directory(node);
}

/**
 * Internal visitor function for `Drive` nodes.
 */
template <>
void Visitor<void>::raw_visit_drive(Drive &node, void *retval) {
    (void) retval;
    this->visit_drive(node);
}

/**
 * Internal visitor function for `Entry` nodes.
 */
template <>
void Visitor<void>::raw_visit_entry(Entry &node, void *retval) {
    (void) retval;
    this->visit_entry(node);
}

/**
 * Internal visitor function for `File` nodes.
 */
template <>
void Visitor<void>::raw_visit_file(File &node, void *retval) {
    (void) retval;
    this->visit_file(node);
}

/**
 * Internal visitor function for `Mount` nodes.
 */
template <>
void Visitor<void>::raw_visit_mount(Mount &node, void *retval) {
    (void) retval;
    this->visit_mount(node);
}

/**
 * Internal visitor function for `System` nodes.
 */
template <>
void Visitor<void>::raw_visit_system(System &node, void *retval) {
    (void) retval;
    this->visit_system(node);
}

/**
 * Recursive traversal for `Directory` nodes.
 */
void RecursiveVisitor::visit_directory(Directory &node) {
    visit_entry(node);
    node.entries.visit(*this);
}

/**
 * Recursive traversal for `Drive` nodes.
 */
void RecursiveVisitor::visit_drive(Drive &node) {
    visit_node(node);
    node.root_dir.visit(*this);
}

/**
 * Recursive traversal for `Entry` nodes.
 */
void RecursiveVisitor::visit_entry(Entry &node) {
    visit_node(node);
}

/**
 * Recursive traversal for `File` nodes.
 */
void RecursiveVisitor::visit_file(File &node) {
    visit_entry(node);
}

/**
 * Recursive traversal for `Mount` nodes.
 */
void RecursiveVisitor::visit_mount(Mount &node) {
    visit_entry(node);
}

/**
 * Recursive traversal for `System` nodes.
 */
void RecursiveVisitor::visit_system(System &node) {
    visit_node(node);
    node.drives.visit(*this);
}

/**
 * Writes the current indentation level's worth of spaces.
 */
void Dumper::write_indent() {
    for (int i = 0; i < indent; i++) {
        out << "  ";
    }
}

/**
 * Dumps a `Node`.
 */
void Dumper::visit_node(Node &node) {
    (void) node;
    write_indent();
    out << "!Node()" << std::endl;
}

/**
 * Dumps a `Directory` node.
 */
void Dumper::visit_directory(Directory &node) {
    write_indent();
    out << "Directory";
    if (ids != nullptr) {
        out << "@" << ids->get_ref(node);
    }
    out << "(";
    out << std::endl;
    indent++;
    write_indent();
    out << "entries: ";
    if (node.entries.empty()) {
        out << "[]" << std::endl;
    } else {
        out << "[" << std::endl;
        indent++;
        for (auto &sptr : node.entries) {
            if (!sptr.empty()) {
                sptr->visit(*this);
            } else {
                write_indent();
                out << "!NULL" << std::endl;
            }
        }
        indent--;
        write_indent();
        out << "]" << std::endl;
    }
    write_indent();
    out << "name: ";
    std::stringstream ss;
    size_t pos;
    ss << node.name;
    pos = ss.str().find_last_not_of(" \n\r\t");
    if (pos != std::string::npos) {
        ss.str(ss.str().erase(pos+1));
    }
    if (ss.str().find('\n') == std::string::npos) {
        out << ss.str() << std::endl;
    } else {
        out << "primitives::String<<" << std::endl;
        indent++;
        std::string s;
        while (!ss.eof()) {
            std::getline(ss, s);
            write_indent();
            out << s << std::endl;
        }
        indent--;
        write_indent();
        out << ">>" << std::endl;
    }
    indent--;
    write_indent();
    out << ")" << std::endl;
}

/**
 * Dumps a `Drive` node.
 */
void Dumper::visit_drive(Drive &node) {
    write_indent();
    out << "Drive";
    if (ids != nullptr) {
        out << "@" << ids->get_ref(node);
    }
    out << "(";
    out << std::endl;
    indent++;
    write_indent();
    out << "letter: ";
    std::stringstream ss;
    size_t pos;
    ss << node.letter;
    pos = ss.str().find_last_not_of(" \n\r\t");
    if (pos != std::string::npos) {
        ss.str(ss.str().erase(pos+1));
    }
    if (ss.str().find('\n') == std::string::npos) {
        out << ss.str() << std::endl;
    } else {
        out << "primitives::Letter<<" << std::endl;
        indent++;
        std::string s;
        while (!ss.eof()) {
            std::getline(ss, s);
            write_indent();
            out << s << std::endl;
        }
        indent--;
        write_indent();
        out << ">>" << std::endl;
    }
    write_indent();
    out << "root_dir: ";
    if (node.root_dir.empty()) {
        out << "!MISSING" << std::endl;
    } else {
        out << "<" << std::endl;
        indent++;
        node.root_dir.visit(*this);
        indent--;
        write_indent();
        out << ">" << std::endl;
    }
    indent--;
    write_indent();
    out << ")" << std::endl;
}

/**
 * Dumps a `Entry` node.
 */
void Dumper::visit_entry(Entry &node) {
    write_indent();
    out << "Entry";
    if (ids != nullptr) {
        out << "@" << ids->get_ref(node);
    }
    out << "(";
    out << std::endl;
    indent++;
    write_indent();
    out << "name: ";
    std::stringstream ss;
    size_t pos;
    ss << node.name;
    pos = ss.str().find_last_not_of(" \n\r\t");
    if (pos != std::string::npos) {
        ss.str(ss.str().erase(pos+1));
    }
    if (ss.str().find('\n') == std::string::npos) {
        out << ss.str() << std::endl;
    } else {
        out << "primitives::String<<" << std::endl;
        indent++;
        std::string s;
        while (!ss.eof()) {
            std::getline(ss, s);
            write_indent();
            out << s << std::endl;
        }
        indent--;
        write_indent();
        out << ">>" << std::endl;
    }
    indent--;
    write_indent();
    out << ")" << std::endl;
}

/**
 * Dumps a `File` node.
 */
void Dumper::visit_file(File &node) {
    write_indent();
    out << "File";
    if (ids != nullptr) {
        out << "@" << ids->get_ref(node);
    }
    out << "(";
    out << std::endl;
    indent++;
    write_indent();
    out << "contents: ";
    std::stringstream ss;
    size_t pos;
    ss << node.contents;
    pos = ss.str().find_last_not_of(" \n\r\t");
    if (pos != std::string::npos) {
        ss.str(ss.str().erase(pos+1));
    }
    if (ss.str().find('\n') == std::string::npos) {
        out << ss.str() << std::endl;
    } else {
        out << "primitives::String<<" << std::endl;
        indent++;
        std::string s;
        while (!ss.eof()) {
            std::getline(ss, s);
            write_indent();
            out << s << std::endl;
        }
        indent--;
        write_indent();
        out << ">>" << std::endl;
    }
    write_indent();
    out << "name: ";
    ss.str("");
    ss.clear();
    ss << node.name;
    pos = ss.str().find_last_not_of(" \n\r\t");
    if (pos != std::string::npos) {
        ss.str(ss.str().erase(pos+1));
    }
    if (ss.str().find('\n') == std::string::npos) {
        out << ss.str() << std::endl;
    } else {
        out << "primitives::String<<" << std::endl;
        indent++;
        std::string s;
        while (!ss.eof()) {
            std::getline(ss, s);
            write_indent();
            out << s << std::endl;
        }
        indent--;
        write_indent();
        out << ">>" << std::endl;
    }
    indent--;
    write_indent();
    out << ")" << std::endl;
}

/**
 * Dumps a `Mount` node.
 */
void Dumper::visit_mount(Mount &node) {
    write_indent();
    out << "Mount";
    if (ids != nullptr) {
        out << "@" << ids->get_ref(node);
    }
    out << "(";
    out << std::endl;
    indent++;
    write_indent();
    out << "target --> ";
    if (node.target.empty()) {
        out << "!MISSING" << std::endl;
    } else if (ids != nullptr && ids->get(node.target) != (size_t)-1) {
        out << "Directory@" << ids->get(node.target) << std::endl;
    } else {
        out << "<" << std::endl;
        indent++;
        if (!in_link) {
            in_link = true;
            node.target.visit(*this);
            in_link = false;
        } else {
            write_indent();
            out << "..." << std::endl;
        }
        indent--;
        write_indent();
        out << ">" << std::endl;
    }
    write_indent();
    out << "name: ";
    std::stringstream ss;
    size_t pos;
    ss << node.name;
    pos = ss.str().find_last_not_of(" \n\r\t");
    if (pos != std::string::npos) {
        ss.str(ss.str().erase(pos+1));
    }
    if (ss.str().find('\n') == std::string::npos) {
        out << ss.str() << std::endl;
    } else {
        out << "primitives::String<<" << std::endl;
        indent++;
        std::string s;
        while (!ss.eof()) {
            std::getline(ss, s);
            write_indent();
            out << s << std::endl;
        }
        indent--;
        write_indent();
        out << ">>" << std::endl;
    }
    indent--;
    write_indent();
    out << ")" << std::endl;
}

/**
 * Dumps a `System` node.
 */
void Dumper::visit_system(System &node) {
    write_indent();
    out << "System";
    if (ids != nullptr) {
        out << "@" << ids->get_ref(node);
    }
    out << "(";
    out << std::endl;
    indent++;
    write_indent();
    out << "drives: ";
    if (node.drives.empty()) {
        out << "!MISSING" << std::endl;
    } else {
        out << "[" << std::endl;
        indent++;
        for (auto &sptr : node.drives) {
            if (!sptr.empty()) {
                sptr->visit(*this);
            } else {
                write_indent();
                out << "!NULL" << std::endl;
            }
        }
        indent--;
        write_indent();
        out << "]" << std::endl;
    }
    indent--;
    write_indent();
    out << ")" << std::endl;
}

/**
 * JSON dumps a `Node`.
 */
void JsonDumper::visit_node(Node &node) {
    (void) node;
    out << "!Node()";
}

/**
 * JSON dumps a `Directory` node.
 */
void JsonDumper::visit_directory(Directory &node) {
    out << "{";
    out << "\"Directory\":";
    out << "{";
    if (node.entries.empty()) {
        out << "\"entries\":\"[]\"";
    } else {
        out << "\"entries\":[";
        bool first_element = true;
        for (auto &sptr : node.entries) {
            if (first_element) {
                first_element = false;
            } else {
                out << ",";
            }
            if (!sptr.empty()) {
                sptr->visit(*this);
            } else {
                out << "!NULL";
            }
        }
        out << "]";
    }
    out << ",";
    out << "\"name\":\"" << node.name << "\"";
    out << "}";
    out << "}";
}

/**
 * JSON dumps a `Drive` node.
 */
void JsonDumper::visit_drive(Drive &node) {
    out << "{";
    out << "\"Drive\":";
    out << "{";
    out << "\"letter\":\"" << node.letter << "\"";
    out << ",";
    if (node.root_dir.empty()) {
        out << "\"root_dir\":\"!MISSING\"";
    } else {
    out << "\"root_dir\":";
    node.root_dir.visit(*this);
    }
    out << "}";
    out << "}";
}

/**
 * JSON dumps a `Entry` node.
 */
void JsonDumper::visit_entry(Entry &node) {
    out << "{";
    out << "\"Entry\":";
    out << "{";
    out << "\"name\":\"" << node.name << "\"";
    out << "}";
    out << "}";
}

/**
 * JSON dumps a `File` node.
 */
void JsonDumper::visit_file(File &node) {
    out << "{";
    out << "\"File\":";
    out << "{";
    out << "\"contents\":\"" << node.contents << "\"";
    out << ",";
    out << "\"name\":\"" << node.name << "\"";
    out << "}";
    out << "}";
}

/**
 * JSON dumps a `Mount` node.
 */
void JsonDumper::visit_mount(Mount &node) {
    out << "{";
    out << "\"Mount\":";
    out << "{";
    if (node.target.empty()) {
        out << "\"target\":\"!MISSING\"";
    } else {
        if (!in_link) {
            in_link = true;
            out << "\"target\":";
            node.target.visit(*this);
            in_link = false;
        } else {
            out << "\"target\":\"...\"";
        }
    }
    out << ",";
    out << "\"name\":\"" << node.name << "\"";
    out << "}";
    out << "}";
}

/**
 * JSON dumps a `System` node.
 */
void JsonDumper::visit_system(System &node) {
    out << "{";
    out << "\"System\":";
    out << "{";
    if (node.drives.empty()) {
        out << "\"drives\":\"!MISSING\"";
    } else {
        out << "\"drives\":[";
        bool first_element = true;
        for (auto &sptr : node.drives) {
            if (first_element) {
                first_element = false;
            } else {
                out << ",";
            }
            if (!sptr.empty()) {
                sptr->visit(*this);
            } else {
                out << "!NULL";
            }
        }
        out << "]";
    }
    out << "}";
    out << "}";
}

/**
 * Visit this object.
 */
template <>
void Node::visit(Visitor<void> &visitor) {
    this->visit_internal(visitor);
}

/**
 * Stream << overload for tree nodes (writes debug dump).
 */
std::ostream &operator<<(std::ostream &os, const Node &object) {
    const_cast<Node&>(object).dump(os);
    return os;
}

} // namespace directory

