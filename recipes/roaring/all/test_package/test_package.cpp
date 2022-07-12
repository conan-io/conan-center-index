#include <cassert>
#include <cstdio>
#include <iostream>

#include "roaring/roaring.hh"
#include "roaring/roaring.h"

#ifndef ROARING_NO_NAMESPACE
using namespace roaring;
#endif

void test_example_cpp(bool copy_on_write) {
  // create a new empty bitmap
  Roaring r1;
  r1.setCopyOnWrite(copy_on_write);
  // then we can add values
  for (uint32_t i = 100; i < 1000; i++) {
    r1.add(i);
  }

  // check whether a value is contained
  assert(r1.contains(500));

  // compute how many bits there are:
  uint64_t cardinality = r1.cardinality();
  std::cout << "Cardinality = " << cardinality << std::endl;

  // if your bitmaps have long runs, you can compress them by calling
  // run_optimize
  size_t size = r1.getSizeInBytes();
  r1.runOptimize();
  size_t compact_size = r1.getSizeInBytes();

  std::cout << "size before run optimize " << size << " bytes, and after "
            << compact_size << " bytes." << std::endl;

  // create a new bitmap with varargs
  Roaring r2 = Roaring::bitmapOf(5, 1, 2, 3, 5, 6);

  r2.printf();
  printf("\n");

  // test select
  uint32_t element;
  r2.select(3, &element);
  assert(element == 5);

  assert(r2.minimum() == 1);

  assert(r2.maximum() == 6);

  assert(r2.rank(4) == 3);

  // we can also create a bitmap from a pointer to 32-bit integers
  const uint32_t values[] = {2, 3, 4};
  Roaring r3(3, values);
  r3.setCopyOnWrite(copy_on_write);

  // we can also go in reverse and go from arrays to bitmaps
  uint64_t card1 = r1.cardinality();
  uint32_t *arr1 = new uint32_t[card1];
  assert(arr1 != NULL);
  r1.toUint32Array(arr1);
  Roaring r1f(card1, arr1);
  delete[] arr1;

  // bitmaps shall be equal
  assert(r1 == r1f);

  // we can copy and compare bitmaps
  Roaring z(r3);
  z.setCopyOnWrite(copy_on_write);
  assert(r3 == z);

  // we can compute union two-by-two
  Roaring r1_2_3 = r1 | r2;
  r1_2_3.setCopyOnWrite(copy_on_write);
  r1_2_3 |= r3;

  // we can compute a big union
  const Roaring *allmybitmaps[] = {&r1, &r2, &r3};
  Roaring bigunion = Roaring::fastunion(3, allmybitmaps);
  assert(r1_2_3 == bigunion);

  // we can compute intersection two-by-two
  Roaring i1_2 = r1 & r2;

  // we can write a bitmap to a pointer and recover it later
  size_t expectedsize = r1.getSizeInBytes();
  char *serializedbytes = new char[expectedsize];
  r1.write(serializedbytes);
  Roaring t = Roaring::read(serializedbytes);
  assert(expectedsize == t.getSizeInBytes());
  assert(r1 == t);

  Roaring t2 = Roaring::readSafe(serializedbytes, expectedsize);
  assert(expectedsize == t2.getSizeInBytes());
  assert(r1 == t2);

  delete[] serializedbytes;

  size_t counter = 0;
  for (Roaring::const_iterator i = t.begin(); i != t.end(); i++) {
    ++counter;
  }
  assert(counter == t.cardinality());

  // we can move iterators
  const uint32_t manyvalues[] = {2, 3, 4, 7, 8};
  Roaring rogue(5, manyvalues);
  Roaring::const_iterator j = rogue.begin();
  j.equalorlarger(4);
  assert(*j == 4);

  // test move constructor
  {
    Roaring b;
    b.add(10);
    b.add(20);

    Roaring a(std::move(b));
    assert(a.cardinality() == 2);
    assert(a.contains(10));
    assert(a.contains(20));

    // b should be destroyed without any errors
    assert(b.cardinality() == 0);
  }

  // test move operator
  {
    Roaring b;
    b.add(10);
    b.add(20);

    Roaring a;

    a = std::move(b);
    assert(2 == a.cardinality());
    assert(a.contains(10));
    assert(a.contains(20));

    // b should be destroyed without any errors
    assert(0 == b.cardinality());
  }

  // test toString
  {
    Roaring a;
    a.add(1);
    a.add(2);
    a.add(3);
    a.add(4);

  }
}

int main() {
  Roaring r1;
  // then we can add values
  for (uint32_t i = 100; i < 1000; i++) {
    r1.add(i);
  }

  // check whether a value is contained
  assert(r1.contains(500));

  // compute how many bits there are:
  uint64_t cardinality = r1.cardinality();
  std::cout << "Cardinality = " << cardinality << std::endl;

  // if your bitmaps have long runs, you can compress them by calling
  // run_optimize
  size_t size = r1.getSizeInBytes();
  r1.runOptimize();
  size_t compact_size = r1.getSizeInBytes();

  std::cout << "size before run optimize " << size << " bytes, and after "
            << compact_size << " bytes." << std::endl;

  // create a new bitmap with varargs
  Roaring r2 = Roaring::bitmapOf(5, 1, 2, 3, 5, 6);

  r2.printf();
  printf("\n");

  // test select
  uint32_t element;
  r2.select(3, &element);
  assert(element == 5);

  assert(r2.minimum() == 1);

  assert(r2.maximum() == 6);

  assert(r2.rank(4) == 3);
  return EXIT_SUCCESS;
}
