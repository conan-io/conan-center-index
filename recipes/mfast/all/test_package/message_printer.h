#ifndef MESSAGE_PRINTER_H
#define MESSAGE_PRINTER_H

#include <mfast.h>

struct message_printer
{
  enum { visit_absent = 0 };

  message_printer(std::ostream& )
  { }

  template<typename T>
  void visit(T)
  { }

  template<typename T, typename U>
  void visit(T, U)
  { }
};
#endif // MESSAGE_PRINTER_H
