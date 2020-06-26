#include "MDRefreshSample.h"
#include <iostream>
#include <iomanip>
#include <map>
#include <vector>
#include "message_printer.h"

int main()
{
  MDRefreshSample::MDRefreshSample message;
  MDRefreshSample::MDRefreshSample_mref ref = message.ref();
  ref.set_MDEntries().resize(1);
  MDRefreshSample::MDRefreshSample_mref::MDEntries_element_mref entry(ref.set_MDEntries()[0]);
  entry.set_MDUpdateAction().as(1);
  const char* str = "abcd";
  entry.set_MDEntryType().as(str);

  entry.set_Symbol().as("AAPL");
  entry.set_SecurityType().as("Stock");
  entry.set_MDEntryPx().as(1, 2);
  entry.set_MDEntrySize().as(3,4);
  entry.set_NumberOfOrders().as(100);

  message_printer printer(std::cout);
  ref.accept_accessor(printer);
  return 0;
}
