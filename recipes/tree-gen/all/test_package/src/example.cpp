#include "output/directory.actual.hpp"  // the generated file
#include "utils.hpp"
#include "version.hpp"  // tree-gen version

#include <cstdio>
#include <iostream>
#include <sstream>  // ostringstream
#include <stdexcept>


void print_tree_gen_version() {
    std::printf("tree-gen version: %s\n", TREE_GEN_VERSION);
    std::printf("tree-gen release year: %s\n", TREE_GEN_RELEASE_YEAR);
}


// Note: the // comment contents of main(), together with the MARKER lines and the output of the program,
// are used to automatically turn this into a restructured-text page for ReadTheDocs.

int main() {
    print_tree_gen_version();

    // **********************
    // Directory tree example
    // **********************
    //
    // This example illustrates the tree system with a Windows-like directory tree structure.
    // The ``System`` root node consists of one or more drives,
    // each of which has a drive letter and a root directory with named files and subdirectories.
    // To make things a little more interesting, a symlink-like "mount" is added as a file type,
    // which links to another directory.
    //
    // Using this tree, this example should teach you the basics of using tree-gen trees.
    // The tutorial runs you through the C++ code of ``main.cpp`` and Python code of ``main.py``,
    // but be sure to check out ``directory.tree``, ``primitives.hpp``, ``primitives.hpp``, and
    // (if you want to reproduce it in your own project) ``CMakeLists.txt`` copied to the bottom of this page as well.
    // You will also find the complete ``main.cpp`` and ``main.py`` there.
    //
    // Let's start by making the root node using ``tree::base::make()``.
    // This works somewhat like ``std::make_shared()``,
    // but instead of returning a ``shared_ptr`` it returns a ``One`` edge.
    // This might come off as a bit odd, considering trees in graph theory start with a node rather than an edge.
    // This is just a choice, though;
    // a side effect of how the internal ``shared_ptr``s work and how Link/OptLink edges work
    // (if you'd store the tree as the root structure directly,
    // the root node wouldn't always be stored in the same place on the heap, breaking link nodes).
    auto system = tree::base::make<directory::System>();
    MARKER

    // At all times, you can use the ``dump()`` method on a node to see what it looks like for debugging purposes.
    // It looks like this:
    system->dump();
    MARKER

    // While this system node exists as a tree in memory and tree-gen seems happy,
    // our system tree is at this time not "well-formed".
    // A tree node (or an edge to one) is only considered well-formed if all of the following are true:
    //
    //  - All ``One`` edges in the tree connect to exactly one node.
    //  - All ``Many`` edges in the tree connect to at least one node.
    //  - All ``Link`` and non-empty ``OptLink`` nodes refer to a node reachable from the root node.
    //  - Each node in the tree is only used by a non-link node once.
    //
    // Currently, the second requirement is not met.
    ASSERT(!system.is_well_formed());
    MARKER

    // You can get slightly more information using ``check_well_formed()``;
    // instead or returning a boolean, it will throw a ``NotWellFormed`` exception with an error message.
    ASSERT_RAISES(tree::base::NotWellFormed, system.check_well_formed());
    MARKER

    // Note that the name of the type is `"mangled" <https://en.wikipedia.org/wiki/Name_mangling#C++>`_.
    // The exact output will vary from compiler to compiler, or even from project to project.
    // But hopefully it'll be readable enough to make sense of in general.

    // To fix that, let's add a default drive node to the tree.
    // This should get drive letter ``A``,
    // because primitives::initialize() is specialized to return that for ``Letter``s (see primitives.hpp).
    system->drives.add(tree::base::make<directory::Drive>());
    MARKER

    // ``Drive`` has a ``One`` edge that is no empty,
    // though, so the tree still isn't well-formed. Let's add one of those as well.
    system->drives[0]->root_dir = tree::base::make<directory::Directory>();
    MARKER

    // Now we have a well-formed tree. Let's have a look:
    system.check_well_formed();
    system->dump();
    MARKER

    // We can just change the drive letter by assignment, as you would expect.
    system->drives[0]->letter = 'C';
    MARKER

    // Before we add files and directories, let's make a shorthand variable for the root directory.
    // Because root_dir is an edge to another node rather than the node itself,
    // and thus acts like a pointer or reference to it,
    // we can just copy it into a variable and modify the variable to update the tree.
    // Note that you'd normally just write "auto" for the type for brevity;
    // the type is shown here to make explicit what it turns into.
    directory::One<directory::Directory> root = system->drives[0]->root_dir;
    MARKER

    // Let's make a "Program Files" subdirectory and add it to the root.
    auto programs = tree::base::make<directory::Directory>(
        tree::base::Any<directory::Entry>{},
        "Program Files");
    root->entries.add(programs);
    system.check_well_formed();
    MARKER

    // That's quite verbose. But in most cases it can be written way shorter.
    // Here's the same with the less versatile but also less verbose emplace() method
    // (which avoids the tree::make() call, but doesn't allow an insertion index to be specified)
    // and with a "using namespace" for the tree.
    // emplace() can also be chained, allowing multiple files and directories to be added at once in this case.
    {
        using namespace directory;

        root->entries.emplace<Directory>(Any<Entry>{}, "Windows")
                     .emplace<Directory>(Any<Entry>{}, "Users")
                     .emplace<File>("lots of hibernation data", "hiberfil.sys")
                     .emplace<File>("lots of page file data", "pagefile.sys")
                     .emplace<File>("lots of swap data", "swapfile.sys");
    }
    system.check_well_formed();
    MARKER

    // In order to look for a file in a directory, you'll have to make your own function to iterate over them.
    // After all, tree-gen doesn't know that the name field is a key; it has no concept of a key-value store.
    // This is simple enough to make,
    // but to prevent this example from getting out of hand we'll just use indices for now.

    // Let's try to read the "lots of data" string from pagefile.sys.
    ASSERT(root->entries[4]->name == "pagefile.sys");
    // ASSERT(root->entries[4]->contents == "lots of page file data");
    //  '-> No member named 'contents' in 'directory::Entry'
    MARKER

    // Hm, that didn't work so well,
    // because C++ doesn't know that entry 4 happens to be a file rather than a directory or a mount.
    // We have to tell it to cast to a file first (which throws a std::bad_cast if it's not actually a file).
    // The easiest way to do that is like this:
    ASSERT(root->entries[4]->as_file()->contents == "lots of page file data");
    MARKER

    // No verbose casts required; tree-gen will make member functions for all the possible subtypes.

    // While it's possible to put the same node in a tree twice (without using a link), this is not allowed.
    // This isn't checked until a well-formedness check is performed,
    // however (and in fact can't be without having access to the root node).
    root->entries.add(root->entries[0]);
    ASSERT_RAISES(tree::base::NotWellFormed, system.check_well_formed());
    MARKER

    // Note that we can index nodes Python-style with negative integers for add() and remove(),
    // so remove(-1) will remove the broken node we just added.
    // Note that the -1 is not actually necessary, though, as it is the default.
    root->entries.remove(-1);
    system.check_well_formed();
    MARKER

    // We *can*, of course, add copies of nodes.
    // That's what copy (shallow) and clone (deep) are for.
    // Usually you'll want a deep copy, but in this case shallow is fine, because a File has no child nodes.
    // Note that, even for a deep copy, links are not modified;
    // it is intended to copy a subtree to another part of the same tree.
    // To make a complete copy of a tree that maintains link semantics (i.e. does not link back to the original tree)
    // the best way would be to go through serialize/deserialize.
    root->entries.add(root->entries[0]->copy());
    system.check_well_formed();
    MARKER

    // Note that the generated classes don't care that there are now two directories named Program Files in the root.
    // As far as they're concerned, they're two different directories with the same name.
    // Let's remove it again, though.
    root->entries.remove();
    MARKER

    // Something we haven't looked at yet are links.
    // Links are edges in the tree that, well, turn it into something that isn't strictly a tree anymore.
    // While One/Maybe/Any/Many require that nodes are unique,
    // Link/OptLink require that they are *not* unique,
    // and are present elsewhere in the tree.
    // Let's make a new directory, and mount it in the Users directory.
    auto user_dir = tree::base::make<directory::Directory>(
        tree::base::Any<directory::Entry>{},
        "");
    root->entries.emplace<directory::Mount>(user_dir, "SomeUser");
    MARKER

    // Note that user_dir is not yet part of the tree.
    // emplace works simply because it doesn't check whether the directory is in the tree yet.
    // But the tree is no longer well-formed now.
    ASSERT_RAISES(tree::base::NotWellFormed, system.check_well_formed());
    MARKER

    // To make it work again, we can add it as a root directory to a second drive.
    system->drives.emplace<directory::Drive>('D', user_dir);
    system.check_well_formed();
    MARKER

    // A good way to confuse a filesystem is to make loops.
    // tree-gen is okay with this, though.
    system->drives[1]->root_dir->entries.emplace<directory::Mount>(root, "evil link to C:");
    system.check_well_formed();
    MARKER

    // The only place where it matters is in the dump function, which only goes one level deep.
    // After that, it'll just print an ellipsis.
    system->dump();
    MARKER

    // Now that we have a nice tree, let's try the serialization and deserialization functionality.
    // Serializing is easy:
    std::string cbor = tree::base::serialize(tree::base::Maybe<directory::System>{ system });
    MARKER

    // Let's write it to a file; we'll load this in Python later.
    {
        std::ofstream cbor_output;
        cbor_output.open("tree.cbor", std::ios::out | std::ios::trunc | std::ios::binary);
        cbor_output << cbor;
    }
    MARKER

    // Let's also have a look at a hexdump of that.
    int count = 0;
    for (char c : cbor) {
        if (count == 16) {
            std::printf("\n");
            count = 0;
        } else if (count > 0 && count % 4 == 0) {
            std::printf(" ");
        }
        std::printf("%02X ", (uint8_t)c);
        count++;
    }
    std::printf("\n");
    MARKER

    // You can pull that through http://cbor.me and https://jsonformatter.org to inspect the output, if you like.

    // We can deserialize it into a complete copy of the tree.
    auto system2 = tree::base::deserialize<directory::System>(cbor);
    system2->dump();
    MARKER

    // Testing the JSON dump
    std::ostringstream oss{};
    system2->dump_json(oss);
    ASSERT(oss.str() ==
        R"({"System":{"drives":[{"Drive":{"letter":"C","root_dir":{"Directory":{"entries":[)"
        R"({"Directory":{"entries":"[]","name":"Program Files"}},{"Directory":{"entries":"[)"
        R"(]","name":"Windows"}},{"Directory":{"entries":"[]","name":"Users"}},{"File":{"co)"
        R"(ntents":"lots of hibernation data","name":"hiberfil.sys"}},{"File":{"contents":")"
        R"(lots of page file data","name":"pagefile.sys"}},{"File":{"contents":"lots of swa)"
        R"(p data","name":"swapfile.sys"}},{"Mount":{"target":{"Directory":{"entries":[{"Mo)"
        R"(unt":{"target":"...","name":"evil link to C:"}}],"name":""}},"name":"SomeUser"}})"
        R"(],"name":""}}}},{"Drive":{"letter":"D","root_dir":{"Directory":{"entries":[{"Mou)"
        R"(nt":{"target":{"Directory":{"entries":[{"Directory":{"entries":"[]","name":"Prog)"
        R"(ram Files"}},{"Directory":{"entries":"[]","name":"Windows"}},{"Directory":{"entr)"
        R"(ies":"[]","name":"Users"}},{"File":{"contents":"lots of hibernation data","name")"
        R"(:"hiberfil.sys"}},{"File":{"contents":"lots of page file data","name":"pagefile.)"
        R"(sys"}},{"File":{"contents":"lots of swap data","name":"swapfile.sys"}},{"Mount":)"
        R"({"target":"...","name":"SomeUser"}}],"name":""}},"name":"evil link to C:"}}],"na)"
        R"(me":""}}}}]}})"
    );
    std::printf("%s", oss.str().c_str());
    std::printf("\n");
    MARKER

    // Note that equality for two link edges is satisfied only if they point to the exact same node.
    // That's not the case for the links in our two entirely separate trees, so the two trees register as unequal.
    ASSERT(!system2.equals(system));
    MARKER

    // To be sure no data was lost, we'll have to check the CBOR and debug dumps instead.
    ASSERT(tree::base::serialize(tree::base::Maybe<directory::System>{ system }) == tree::base::serialize(system2));
    std::ostringstream ss1{};
    system->dump(ss1);
    std::ostringstream ss2{};
    system2->dump(ss2);
    ASSERT(ss1.str() == ss2.str());
    MARKER

    return 0;
}
