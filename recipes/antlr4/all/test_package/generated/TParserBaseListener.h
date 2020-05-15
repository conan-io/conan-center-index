/* parser/listener/visitor header section */

// Generated from TParser.g4 by ANTLR 4.8

#pragma once

/* base listener preinclude section */

#include "antlr4-runtime.h"
#include "TParserListener.h"

/* base listener postinclude section */

namespace antlrcpptest {

/**
 * This class provides an empty implementation of TParserListener,
 * which can be extended to create a listener which only needs to handle a subset
 * of the available methods.
 */
class  TParserBaseListener : public TParserListener {
public:
/* base listener public declarations/members section */

  virtual void enterMain(TParser::MainContext * /*ctx*/) override { }
  virtual void exitMain(TParser::MainContext * /*ctx*/) override { }

  virtual void enterDivide(TParser::DivideContext * /*ctx*/) override { }
  virtual void exitDivide(TParser::DivideContext * /*ctx*/) override { }

  virtual void enterAnd_(TParser::And_Context * /*ctx*/) override { }
  virtual void exitAnd_(TParser::And_Context * /*ctx*/) override { }

  virtual void enterConquer(TParser::ConquerContext * /*ctx*/) override { }
  virtual void exitConquer(TParser::ConquerContext * /*ctx*/) override { }

  virtual void enterUnused(TParser::UnusedContext * /*ctx*/) override { }
  virtual void exitUnused(TParser::UnusedContext * /*ctx*/) override { }

  virtual void enterUnused2(TParser::Unused2Context * /*ctx*/) override { }
  virtual void exitUnused2(TParser::Unused2Context * /*ctx*/) override { }

  virtual void enterStat(TParser::StatContext * /*ctx*/) override { }
  virtual void exitStat(TParser::StatContext * /*ctx*/) override { }

  virtual void enterExpr(TParser::ExprContext * /*ctx*/) override { }
  virtual void exitExpr(TParser::ExprContext * /*ctx*/) override { }

  virtual void enterReturn(TParser::ReturnContext * /*ctx*/) override { }
  virtual void exitReturn(TParser::ReturnContext * /*ctx*/) override { }

  virtual void enterContinue(TParser::ContinueContext * /*ctx*/) override { }
  virtual void exitContinue(TParser::ContinueContext * /*ctx*/) override { }

  virtual void enterId(TParser::IdContext * /*ctx*/) override { }
  virtual void exitId(TParser::IdContext * /*ctx*/) override { }

  virtual void enterArray(TParser::ArrayContext * /*ctx*/) override { }
  virtual void exitArray(TParser::ArrayContext * /*ctx*/) override { }

  virtual void enterIdarray(TParser::IdarrayContext * /*ctx*/) override { }
  virtual void exitIdarray(TParser::IdarrayContext * /*ctx*/) override { }

  virtual void enterAny(TParser::AnyContext * /*ctx*/) override { }
  virtual void exitAny(TParser::AnyContext * /*ctx*/) override { }


  virtual void enterEveryRule(antlr4::ParserRuleContext * /*ctx*/) override { }
  virtual void exitEveryRule(antlr4::ParserRuleContext * /*ctx*/) override { }
  virtual void visitTerminal(antlr4::tree::TerminalNode * /*node*/) override { }
  virtual void visitErrorNode(antlr4::tree::ErrorNode * /*node*/) override { }

private:  
/* base listener private declarations/members section */
};

}  // namespace antlrcpptest
