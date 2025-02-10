// Copyright (c) 2022 Klemens Morgenstern
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

// This comes from the following Boost example:
// https://github.com/boostorg/process/blob/boost-1.86.0/example/v2/intro.cpp

// clang-format: off
#include <boost/asio/read.hpp>
#include <boost/asio/readable_pipe.hpp>
// clang-format: on

#include <boost/process/v2.hpp>
#include <boost/system/error_code.hpp>

#include <string>
#include <iostream>

#if defined(BOOST_NAMESPACE)
namespace boost = BOOST_NAMESPACE;
#endif

namespace proc   = boost::process::v2;
namespace asio   = boost::asio;

int main()
{
  asio::io_context ctx;
  asio::readable_pipe p{ctx};

  const auto exe = proc::environment::find_executable("cmake");

  proc::process c{ctx, exe, {"--version"}, proc::process_stdio{nullptr, p}};

  std::string line;
  boost::system::error_code ec;

  auto sz = asio::read(p, asio::dynamic_buffer(line), ec);

  std::cout << "CMake version: '"  << line << "'" << std::endl;

  c.wait();
}
