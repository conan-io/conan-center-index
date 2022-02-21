/*
 *  This file was copied from https://github.com/BlueBrain/HighFive/blob/master/src/examples/create_attribute_string_integer.cpp
 *	and changed in terms of namespaces and const correctness.
 */
/*
 *  Copyright (c), 2017, Adrien Devresse
 *
 *  Distributed under the Boost Software License, Version 1.0.
 *    (See accompanying file LICENSE_1_0.txt or copy at
 *          http://www.boost.org/LICENSE_1_0.txt)
 *
 */
#include <iostream>
#include <string>
#include <vector>

#include <highfive/H5Attribute.hpp>
#include <highfive/H5File.hpp>
#include <highfive/H5DataSet.hpp>
#include <highfive/H5DataSpace.hpp>

const std::string FILE_NAME("create_attribute.h5");
const std::string DATASET_NAME("my_dataset");

const std::string ATTRIBUTE_NAME_NOTE("note");
const std::string ATTRIBUTE_NAME_VERSION("version_string");

// create a dataset from a vector of string
// read it back and print it
int main(void)
{
	try
	{
		// Create a new file using the default property lists.
		HighFive::File file(FILE_NAME, HighFive::File::ReadWrite | HighFive::File::Create | HighFive::File::Truncate);

		// Create a dummy dataset of one single integer
		HighFive::DataSet dataset =
			file.createDataSet(DATASET_NAME, HighFive::DataSpace(1), HighFive::AtomicType<int>());

		// Now let's add a attribute on this dataset
		// This attribute will be named "note"
		// and have the following content
		std::string string_list("very important Dataset!");

		HighFive::Attribute attribute = dataset.createAttribute<std::string>(
			ATTRIBUTE_NAME_NOTE, HighFive::DataSpace::From(string_list));
		attribute.write(string_list);

		// We also add a "version" attribute
		// that will be an array 1x2 of integer
		std::vector<int> version;
		version.push_back(1);
		version.push_back(0); // version 1.0

		HighFive::Attribute v = dataset.createAttribute<int>(ATTRIBUTE_NAME_VERSION,
															 HighFive::DataSpace::From(version));
		v.write(version);

		// Ok all attributes are now written

		// let's list the keys of all attributes now
		const std::vector<std::string> all_attributes_keys =
			dataset.listAttributeNames();
		for (const auto &attr : all_attributes_keys)
		{
			std::cout << "attribute: " << attr << std::endl;
		}
	}
	catch (HighFive::Exception &err)
	{
		// catch and print any HDF5 error
		std::cerr << err.what() << std::endl;
	}

	return 0; // successfully terminated
}
