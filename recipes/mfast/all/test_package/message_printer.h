#ifndef MESSAGE_PRINTER_H
#define MESSAGE_PRINTER_H

#include <mfast.h>
#include <iostream>
#include <boost/io/ios_state.hpp>

using namespace mfast;

class indenter
{
  std::size_t level_;

  public:
    indenter()
      : level_(0)
    {
    }

    indenter& operator ++()
    {
      ++level_;
      return *this;
    }

    indenter& operator --()
    {
      --level_;
      return *this;
    }

    std::size_t blanks() const
    {
      return level_*2;
    }

};

std::ostream&
operator << (std::ostream& os, const indenter& indent)
{
  os << std::setw(indent.blanks()) << ' ';
  return os;
}

class message_printer
{
  std::ostream& os_;
  indenter indent_;

  public:

    enum {
      visit_absent = 0
    };


    message_printer(std::ostream& os)
      : os_(os)
    {
    }

    template <typename IntType>
    void visit_i(const int_cref<IntType>& ref)
    {
      // matches int32_cref, uint32_cref, int64_cref, uint64_cref
      os_ << ref.value();
    }

    void visit_i(const enum_cref& ref)
    {
      os_ << ref.value_name();
    }

    void visit_i(const decimal_cref& ref)
    {
      os_ << ref.mantissa() << "*10^" << (int)ref.exponent();
    }

    template <typename CharType>
    void visit_i(const string_cref<CharType>& ref)
    {
      // matches ascii_string_cref and unicode_string_cref
      os_ << ref.c_str();
    }

    void visit_i(const byte_vector_cref& ref)
    {
      boost::io::ios_flags_saver  ifs( os_ );
      os_ << std::hex << std::setfill('0');

      for (std::size_t i = 0 ; i < ref.size(); ++i){
        os_ << std::setw(2) <<  static_cast<unsigned>(ref[i]);
      }
      os_ << std::setfill(' ');

    }

    template <typename IntType>
    void visit_i(const int_vector_cref<IntType>& ref)
    {
      // matches int32_vector_cref, uint32_vector_cref, int64_vector_cref, uint64_vector_cref

      char sep[2]= { '\x0', '\x0'};
      os_ << "{";
      for (std::size_t i = 0; i < ref.size(); ++i)
      {
        os_ << sep << ref[i];
        sep[0] = ',';
      }
      os_ << "}";
    }

    template <typename T>
    void visit(const T& ref)
    {
      os_ << indent_ << ref.name() << ": ";
      this->visit_i(ref);
      os_ << "\n";
    }

    template <typename CompositeTypeRef>
    void visit(const CompositeTypeRef& ref, int)
    {
      os_ << indent_ << ref.name() << ":\n";
      ++indent_;
      ref.accept_accessor(*this);
      --indent_;
    }

    void visit(const sequence_element_cref&  ref, int index)
    {
      os_ << indent_ <<  "[" << index << "]:\n";
      ++indent_;
      ref.accept_accessor(*this);
      --indent_;
    }
};
#endif // MESSAGE_PRINTER_H
