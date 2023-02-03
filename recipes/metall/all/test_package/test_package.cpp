// Copyright 2019 Lawrence Livermore National Security, LLC and other Metall Project Developers.
// See the top-level COPYRIGHT file for details.
//
// SPDX-License-Identifier: (Apache-2.0 OR MIT)

#include <iostream>
#include <boost/container/vector.hpp>

#include <metall/metall.hpp> // Only one header file is required to be included

// Type alias
// This is a standard way to give a custom allocator to a container
using vector_t = boost::container::vector<int, metall::manager::allocator_type<int>>;

int main() {

    {
        // Construct a manager object
        // A process can allocate multiple manager objects
        metall::manager manager(metall::create_only,  // Create a new one
                                "/tmp/dir");          // The directory to store backing datastore

        // Allocate and construct a vector object in the persistent memory with a name "vec"
        auto pvec = manager.construct<vector_t>                    // Allocate and construct an object of vector_t
                ("vec")              // Name of the allocated object
                (manager.get_allocator()); // Arguments passed to vector_t's constructor

        pvec->push_back(5); // Can use containers normally

    } // Implicitly sync with backing files, i.e., sync() is called in metall::manager's destructor

    // ---------- Assume exit and restart the program at this point ---------- //

    {
        // Reattach the manager object
        metall::manager manager(metall::open_only, "/tmp/dir");

        // Find the previously constructed object
        // Please do not forget to use ".first" at the end
        auto pvec = manager.find<vector_t>("vec").first;

        pvec->push_back(10); // Can restart to use containers normally

        std::cout << (*pvec)[0] << std::endl; // Will print "5"
        std::cout << (*pvec)[1] << std::endl; // Will print "10"

        manager.destroy<vector_t>("vec"); // Destroy the object
    }

    return 0;
}
