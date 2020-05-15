/* parser/listener/visitor header section */

// Generated from TParser.g4 by ANTLR 4.8

/* parser precinclude section */

#include "TParserListener.h"
#include "TParserVisitor.h"

#include "TParser.h"


/* parser postinclude section */
#ifndef _WIN32
#pragma GCC diagnostic ignored "-Wunused-parameter"
#endif


using namespace antlrcpp;
using namespace antlrcpptest;
using namespace antlr4;

TParser::TParser(TokenStream *input) : Parser(input) {
  _interpreter = new atn::ParserATNSimulator(this, _atn, _decisionToDFA, _sharedContextCache);
}

TParser::~TParser() {
  delete _interpreter;
}

std::string TParser::getGrammarFileName() const {
  return "TParser.g4";
}

const std::vector<std::string>& TParser::getRuleNames() const {
  return _ruleNames;
}

dfa::Vocabulary& TParser::getVocabulary() const {
  return _vocabulary;
}

/* parser definitions section */

//----------------- MainContext ------------------------------------------------------------------

TParser::MainContext::MainContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* TParser::MainContext::EOF() {
  return getToken(TParser::EOF, 0);
}

std::vector<TParser::StatContext *> TParser::MainContext::stat() {
  return getRuleContexts<TParser::StatContext>();
}

TParser::StatContext* TParser::MainContext::stat(size_t i) {
  return getRuleContext<TParser::StatContext>(i);
}


size_t TParser::MainContext::getRuleIndex() const {
  return TParser::RuleMain;
}

void TParser::MainContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterMain(this);
}

void TParser::MainContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitMain(this);
}


antlrcpp::Any TParser::MainContext::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitMain(this);
  else
    return visitor->visitChildren(this);
}

TParser::MainContext* TParser::main() {
  MainContext *_localctx = _tracker.createInstance<MainContext>(_ctx, getState());
  enterRule(_localctx, 0, TParser::RuleMain);
  size_t _la = 0;

  auto onExit = finally([=] {
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(27); 
    _errHandler->sync(this);
    _la = _input->LA(1);
    do {
      setState(26);
      stat();
      setState(29); 
      _errHandler->sync(this);
      _la = _input->LA(1);
    } while ((((_la & ~ 0x3fULL) == 0) &&
      ((1ULL << _la) & ((1ULL << TParser::Return)
      | (1ULL << TParser::Continue)
      | (1ULL << TParser::INT)
      | (1ULL << TParser::ID)
      | (1ULL << TParser::OpenPar)
      | (1ULL << TParser::String))) != 0));
    setState(31);
    match(TParser::EOF);
   
  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- DivideContext ------------------------------------------------------------------

TParser::DivideContext::DivideContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* TParser::DivideContext::ID() {
  return getToken(TParser::ID, 0);
}

TParser::And_Context* TParser::DivideContext::and_() {
  return getRuleContext<TParser::And_Context>(0);
}

tree::TerminalNode* TParser::DivideContext::GreaterThan() {
  return getToken(TParser::GreaterThan, 0);
}


size_t TParser::DivideContext::getRuleIndex() const {
  return TParser::RuleDivide;
}

void TParser::DivideContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterDivide(this);
}

void TParser::DivideContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitDivide(this);
}


antlrcpp::Any TParser::DivideContext::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitDivide(this);
  else
    return visitor->visitChildren(this);
}

TParser::DivideContext* TParser::divide() {
  DivideContext *_localctx = _tracker.createInstance<DivideContext>(_ctx, getState());
  enterRule(_localctx, 2, TParser::RuleDivide);

  auto onExit = finally([=] {
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(33);
    match(TParser::ID);
    setState(37);
    _errHandler->sync(this);

    switch (getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 1, _ctx)) {
    case 1: {
      setState(34);
      and_();
      setState(35);
      match(TParser::GreaterThan);
      break;
    }

    }
    setState(39);

    if (!(doesItBlend())) throw FailedPredicateException(this, "doesItBlend()");
   
  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- And_Context ------------------------------------------------------------------

TParser::And_Context::And_Context(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* TParser::And_Context::And() {
  return getToken(TParser::And, 0);
}


size_t TParser::And_Context::getRuleIndex() const {
  return TParser::RuleAnd_;
}

void TParser::And_Context::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterAnd_(this);
}

void TParser::And_Context::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitAnd_(this);
}


antlrcpp::Any TParser::And_Context::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitAnd_(this);
  else
    return visitor->visitChildren(this);
}

TParser::And_Context* TParser::and_() {
  And_Context *_localctx = _tracker.createInstance<And_Context>(_ctx, getState());
  enterRule(_localctx, 4, TParser::RuleAnd_);
   doInit(); 

  auto onExit = finally([=] {
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(41);
    match(TParser::And);
   _ctx->stop = _input->LT(-1);
     doAfter(); 
  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- ConquerContext ------------------------------------------------------------------

TParser::ConquerContext::ConquerContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<TParser::DivideContext *> TParser::ConquerContext::divide() {
  return getRuleContexts<TParser::DivideContext>();
}

TParser::DivideContext* TParser::ConquerContext::divide(size_t i) {
  return getRuleContext<TParser::DivideContext>(i);
}

TParser::And_Context* TParser::ConquerContext::and_() {
  return getRuleContext<TParser::And_Context>(0);
}

tree::TerminalNode* TParser::ConquerContext::ID() {
  return getToken(TParser::ID, 0);
}

std::vector<tree::TerminalNode *> TParser::ConquerContext::LessThan() {
  return getTokens(TParser::LessThan);
}

tree::TerminalNode* TParser::ConquerContext::LessThan(size_t i) {
  return getToken(TParser::LessThan, i);
}


size_t TParser::ConquerContext::getRuleIndex() const {
  return TParser::RuleConquer;
}

void TParser::ConquerContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterConquer(this);
}

void TParser::ConquerContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitConquer(this);
}


antlrcpp::Any TParser::ConquerContext::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitConquer(this);
  else
    return visitor->visitChildren(this);
}

TParser::ConquerContext* TParser::conquer() {
  ConquerContext *_localctx = _tracker.createInstance<ConquerContext>(_ctx, getState());
  enterRule(_localctx, 6, TParser::RuleConquer);
  size_t _la = 0;

  auto onExit = finally([=] {
    exitRule();
  });
  try {
    setState(63);
    _errHandler->sync(this);
    switch (getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 5, _ctx)) {
    case 1: {
      enterOuterAlt(_localctx, 1);
      setState(44); 
      _errHandler->sync(this);
      _la = _input->LA(1);
      do {
        setState(43);
        divide();
        setState(46); 
        _errHandler->sync(this);
        _la = _input->LA(1);
      } while (_la == TParser::ID);
      break;
    }

    case 2: {
      enterOuterAlt(_localctx, 2);
      setState(48);

      if (!(doesItBlend())) throw FailedPredicateException(this, "doesItBlend()");
      setState(49);
      and_();
       myAction(); 
      break;
    }

    case 3: {
      enterOuterAlt(_localctx, 3);
      setState(52);
      dynamic_cast<ConquerContext *>(_localctx)->idToken = match(TParser::ID);
      setState(60);
      _errHandler->sync(this);

      switch (getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 4, _ctx)) {
      case 1 + 1: {
        setState(56);
        _errHandler->sync(this);
        _la = _input->LA(1);
        while (_la == TParser::LessThan) {
          setState(53);
          match(TParser::LessThan);
          setState(58);
          _errHandler->sync(this);
          _la = _input->LA(1);
        }
        setState(59);
        divide();
        break;
      }

      }
       (dynamic_cast<ConquerContext *>(_localctx)->idToken != nullptr ? dynamic_cast<ConquerContext *>(_localctx)->idToken->getText() : ""); 
      break;
    }

    }
   
  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- UnusedContext ------------------------------------------------------------------

TParser::UnusedContext::UnusedContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

TParser::UnusedContext::UnusedContext(ParserRuleContext *parent, size_t invokingState, double input)
  : ParserRuleContext(parent, invokingState) {
  this->input = input;
}

TParser::StatContext* TParser::UnusedContext::stat() {
  return getRuleContext<TParser::StatContext>(0);
}


size_t TParser::UnusedContext::getRuleIndex() const {
  return TParser::RuleUnused;
}

void TParser::UnusedContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterUnused(this);
}

void TParser::UnusedContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitUnused(this);
}


antlrcpp::Any TParser::UnusedContext::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitUnused(this);
  else
    return visitor->visitChildren(this);
}

TParser::UnusedContext* TParser::unused(double input) {
  UnusedContext *_localctx = _tracker.createInstance<UnusedContext>(_ctx, getState(), input);
  enterRule(_localctx, 8, TParser::RuleUnused);
   doInit(); 

  auto onExit = finally([=] {

    cleanUp();

    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(65);
    stat();
   _ctx->stop = _input->LT(-1);
     doAfter(); 
  }
  catch (...) {

      // Replaces the standard exception handling.

  }
  return _localctx;
}

//----------------- Unused2Context ------------------------------------------------------------------

TParser::Unused2Context::Unused2Context(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<tree::TerminalNode *> TParser::Unused2Context::Semicolon() {
  return getTokens(TParser::Semicolon);
}

tree::TerminalNode* TParser::Unused2Context::Semicolon(size_t i) {
  return getToken(TParser::Semicolon, i);
}

std::vector<TParser::UnusedContext *> TParser::Unused2Context::unused() {
  return getRuleContexts<TParser::UnusedContext>();
}

TParser::UnusedContext* TParser::Unused2Context::unused(size_t i) {
  return getRuleContext<TParser::UnusedContext>(i);
}

tree::TerminalNode* TParser::Unused2Context::Colon() {
  return getToken(TParser::Colon, 0);
}

tree::TerminalNode* TParser::Unused2Context::Plus() {
  return getToken(TParser::Plus, 0);
}


size_t TParser::Unused2Context::getRuleIndex() const {
  return TParser::RuleUnused2;
}

void TParser::Unused2Context::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterUnused2(this);
}

void TParser::Unused2Context::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitUnused2(this);
}


antlrcpp::Any TParser::Unused2Context::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitUnused2(this);
  else
    return visitor->visitChildren(this);
}

TParser::Unused2Context* TParser::unused2() {
  Unused2Context *_localctx = _tracker.createInstance<Unused2Context>(_ctx, getState());
  enterRule(_localctx, 10, TParser::RuleUnused2);
  size_t _la = 0;

  auto onExit = finally([=] {
    exitRule();
  });
  try {
    size_t alt;
    enterOuterAlt(_localctx, 1);
    setState(70); 
    _errHandler->sync(this);
    alt = 1;
    do {
      switch (alt) {
        case 1: {
              setState(67);
              unused(1);
              setState(68);
              matchWildcard();
              break;
            }

      default:
        throw NoViableAltException(this);
      }
      setState(72); 
      _errHandler->sync(this);
      alt = getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 6, _ctx);
    } while (alt != 2 && alt != atn::ATN::INVALID_ALT_NUMBER);
    setState(75);
    _errHandler->sync(this);

    switch (getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 7, _ctx)) {
    case 1: {
      setState(74);
      _la = _input->LA(1);
      if (!((((_la & ~ 0x3fULL) == 0) &&
        ((1ULL << _la) & ((1ULL << TParser::Colon)
        | (1ULL << TParser::Semicolon)
        | (1ULL << TParser::Plus))) != 0))) {
      _errHandler->recoverInline(this);
      }
      else {
        _errHandler->reportMatch(this);
        consume();
      }
      break;
    }

    }
    setState(77);
    _la = _input->LA(1);
    if (_la == 0 || _la == Token::EOF || (_la == TParser::Semicolon)) {
    _errHandler->recoverInline(this);
    }
    else {
      _errHandler->reportMatch(this);
      consume();
    }
   
  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- StatContext ------------------------------------------------------------------

TParser::StatContext::StatContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

std::vector<TParser::ExprContext *> TParser::StatContext::expr() {
  return getRuleContexts<TParser::ExprContext>();
}

TParser::ExprContext* TParser::StatContext::expr(size_t i) {
  return getRuleContext<TParser::ExprContext>(i);
}

tree::TerminalNode* TParser::StatContext::Equal() {
  return getToken(TParser::Equal, 0);
}

tree::TerminalNode* TParser::StatContext::Semicolon() {
  return getToken(TParser::Semicolon, 0);
}


size_t TParser::StatContext::getRuleIndex() const {
  return TParser::RuleStat;
}

void TParser::StatContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterStat(this);
}

void TParser::StatContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitStat(this);
}


antlrcpp::Any TParser::StatContext::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitStat(this);
  else
    return visitor->visitChildren(this);
}

TParser::StatContext* TParser::stat() {
  StatContext *_localctx = _tracker.createInstance<StatContext>(_ctx, getState());
  enterRule(_localctx, 12, TParser::RuleStat);

  auto onExit = finally([=] {
    exitRule();
  });
  try {
    setState(87);
    _errHandler->sync(this);
    switch (getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 8, _ctx)) {
    case 1: {
      enterOuterAlt(_localctx, 1);
      setState(79);
      expr(0);
      setState(80);
      match(TParser::Equal);
      setState(81);
      expr(0);
      setState(82);
      match(TParser::Semicolon);
      break;
    }

    case 2: {
      enterOuterAlt(_localctx, 2);
      setState(84);
      expr(0);
      setState(85);
      match(TParser::Semicolon);
      break;
    }

    }
   
  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- ExprContext ------------------------------------------------------------------

TParser::ExprContext::ExprContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* TParser::ExprContext::OpenPar() {
  return getToken(TParser::OpenPar, 0);
}

std::vector<TParser::ExprContext *> TParser::ExprContext::expr() {
  return getRuleContexts<TParser::ExprContext>();
}

TParser::ExprContext* TParser::ExprContext::expr(size_t i) {
  return getRuleContext<TParser::ExprContext>(i);
}

tree::TerminalNode* TParser::ExprContext::ClosePar() {
  return getToken(TParser::ClosePar, 0);
}

TParser::IdContext* TParser::ExprContext::id() {
  return getRuleContext<TParser::IdContext>(0);
}

TParser::FlowControlContext* TParser::ExprContext::flowControl() {
  return getRuleContext<TParser::FlowControlContext>(0);
}

tree::TerminalNode* TParser::ExprContext::INT() {
  return getToken(TParser::INT, 0);
}

tree::TerminalNode* TParser::ExprContext::String() {
  return getToken(TParser::String, 0);
}

tree::TerminalNode* TParser::ExprContext::Star() {
  return getToken(TParser::Star, 0);
}

tree::TerminalNode* TParser::ExprContext::Plus() {
  return getToken(TParser::Plus, 0);
}

tree::TerminalNode* TParser::ExprContext::QuestionMark() {
  return getToken(TParser::QuestionMark, 0);
}

tree::TerminalNode* TParser::ExprContext::Colon() {
  return getToken(TParser::Colon, 0);
}

tree::TerminalNode* TParser::ExprContext::Equal() {
  return getToken(TParser::Equal, 0);
}


size_t TParser::ExprContext::getRuleIndex() const {
  return TParser::RuleExpr;
}

void TParser::ExprContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterExpr(this);
}

void TParser::ExprContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitExpr(this);
}


antlrcpp::Any TParser::ExprContext::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitExpr(this);
  else
    return visitor->visitChildren(this);
}


TParser::ExprContext* TParser::expr() {
   return expr(0);
}

TParser::ExprContext* TParser::expr(int precedence) {
  ParserRuleContext *parentContext = _ctx;
  size_t parentState = getState();
  TParser::ExprContext *_localctx = _tracker.createInstance<ExprContext>(_ctx, parentState);
  TParser::ExprContext *previousContext = _localctx;
  (void)previousContext; // Silence compiler, in case the context is not used by generated code.
  size_t startState = 14;
  enterRecursionRule(_localctx, 14, TParser::RuleExpr, precedence);

    

  auto onExit = finally([=] {
    unrollRecursionContexts(parentContext);
  });
  try {
    size_t alt;
    enterOuterAlt(_localctx, 1);
    setState(98);
    _errHandler->sync(this);
    switch (_input->LA(1)) {
      case TParser::OpenPar: {
        setState(90);
        match(TParser::OpenPar);
        setState(91);
        expr(0);
        setState(92);
        match(TParser::ClosePar);
        break;
      }

      case TParser::ID: {
        setState(94);
        dynamic_cast<ExprContext *>(_localctx)->identifier = id();
        break;
      }

      case TParser::Return:
      case TParser::Continue: {
        setState(95);
        flowControl();
        break;
      }

      case TParser::INT: {
        setState(96);
        match(TParser::INT);
        break;
      }

      case TParser::String: {
        setState(97);
        match(TParser::String);
        break;
      }

    default:
      throw NoViableAltException(this);
    }
    _ctx->stop = _input->LT(-1);
    setState(117);
    _errHandler->sync(this);
    alt = getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 11, _ctx);
    while (alt != 2 && alt != atn::ATN::INVALID_ALT_NUMBER) {
      if (alt == 1) {
        if (!_parseListeners.empty())
          triggerExitRuleEvent();
        previousContext = _localctx;
        setState(115);
        _errHandler->sync(this);
        switch (getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 10, _ctx)) {
        case 1: {
          _localctx = _tracker.createInstance<ExprContext>(parentContext, parentState);
          pushNewRecursionContext(_localctx, startState, RuleExpr);
          setState(100);

          if (!(precpred(_ctx, 9))) throw FailedPredicateException(this, "precpred(_ctx, 9)");
          setState(101);
          match(TParser::Star);
          setState(102);
          expr(10);
          break;
        }

        case 2: {
          _localctx = _tracker.createInstance<ExprContext>(parentContext, parentState);
          pushNewRecursionContext(_localctx, startState, RuleExpr);
          setState(103);

          if (!(precpred(_ctx, 8))) throw FailedPredicateException(this, "precpred(_ctx, 8)");
          setState(104);
          match(TParser::Plus);
          setState(105);
          expr(9);
          break;
        }

        case 3: {
          _localctx = _tracker.createInstance<ExprContext>(parentContext, parentState);
          pushNewRecursionContext(_localctx, startState, RuleExpr);
          setState(106);

          if (!(precpred(_ctx, 6))) throw FailedPredicateException(this, "precpred(_ctx, 6)");
          setState(107);
          match(TParser::QuestionMark);
          setState(108);
          expr(0);
          setState(109);
          match(TParser::Colon);
          setState(110);
          expr(6);
          break;
        }

        case 4: {
          _localctx = _tracker.createInstance<ExprContext>(parentContext, parentState);
          pushNewRecursionContext(_localctx, startState, RuleExpr);
          setState(112);

          if (!(precpred(_ctx, 5))) throw FailedPredicateException(this, "precpred(_ctx, 5)");
          setState(113);
          match(TParser::Equal);
          setState(114);
          expr(5);
          break;
        }

        } 
      }
      setState(119);
      _errHandler->sync(this);
      alt = getInterpreter<atn::ParserATNSimulator>()->adaptivePredict(_input, 11, _ctx);
    }
  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }
  return _localctx;
}

//----------------- FlowControlContext ------------------------------------------------------------------

TParser::FlowControlContext::FlowControlContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}


size_t TParser::FlowControlContext::getRuleIndex() const {
  return TParser::RuleFlowControl;
}

void TParser::FlowControlContext::copyFrom(FlowControlContext *ctx) {
  ParserRuleContext::copyFrom(ctx);
}

//----------------- ReturnContext ------------------------------------------------------------------

tree::TerminalNode* TParser::ReturnContext::Return() {
  return getToken(TParser::Return, 0);
}

TParser::ExprContext* TParser::ReturnContext::expr() {
  return getRuleContext<TParser::ExprContext>(0);
}

TParser::ReturnContext::ReturnContext(FlowControlContext *ctx) { copyFrom(ctx); }

void TParser::ReturnContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterReturn(this);
}
void TParser::ReturnContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitReturn(this);
}

antlrcpp::Any TParser::ReturnContext::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitReturn(this);
  else
    return visitor->visitChildren(this);
}
//----------------- ContinueContext ------------------------------------------------------------------

tree::TerminalNode* TParser::ContinueContext::Continue() {
  return getToken(TParser::Continue, 0);
}

TParser::ContinueContext::ContinueContext(FlowControlContext *ctx) { copyFrom(ctx); }

void TParser::ContinueContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterContinue(this);
}
void TParser::ContinueContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitContinue(this);
}

antlrcpp::Any TParser::ContinueContext::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitContinue(this);
  else
    return visitor->visitChildren(this);
}
TParser::FlowControlContext* TParser::flowControl() {
  FlowControlContext *_localctx = _tracker.createInstance<FlowControlContext>(_ctx, getState());
  enterRule(_localctx, 16, TParser::RuleFlowControl);

  auto onExit = finally([=] {
    exitRule();
  });
  try {
    setState(123);
    _errHandler->sync(this);
    switch (_input->LA(1)) {
      case TParser::Return: {
        _localctx = dynamic_cast<FlowControlContext *>(_tracker.createInstance<TParser::ReturnContext>(_localctx));
        enterOuterAlt(_localctx, 1);
        setState(120);
        match(TParser::Return);
        setState(121);
        expr(0);
        break;
      }

      case TParser::Continue: {
        _localctx = dynamic_cast<FlowControlContext *>(_tracker.createInstance<TParser::ContinueContext>(_localctx));
        enterOuterAlt(_localctx, 2);
        setState(122);
        match(TParser::Continue);
        break;
      }

    default:
      throw NoViableAltException(this);
    }
   
  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- IdContext ------------------------------------------------------------------

TParser::IdContext::IdContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* TParser::IdContext::ID() {
  return getToken(TParser::ID, 0);
}


size_t TParser::IdContext::getRuleIndex() const {
  return TParser::RuleId;
}

void TParser::IdContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterId(this);
}

void TParser::IdContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitId(this);
}


antlrcpp::Any TParser::IdContext::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitId(this);
  else
    return visitor->visitChildren(this);
}

TParser::IdContext* TParser::id() {
  IdContext *_localctx = _tracker.createInstance<IdContext>(_ctx, getState());
  enterRule(_localctx, 18, TParser::RuleId);

  auto onExit = finally([=] {
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(125);
    match(TParser::ID);
   
  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- ArrayContext ------------------------------------------------------------------

TParser::ArrayContext::ArrayContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* TParser::ArrayContext::OpenCurly() {
  return getToken(TParser::OpenCurly, 0);
}

tree::TerminalNode* TParser::ArrayContext::CloseCurly() {
  return getToken(TParser::CloseCurly, 0);
}

std::vector<tree::TerminalNode *> TParser::ArrayContext::INT() {
  return getTokens(TParser::INT);
}

tree::TerminalNode* TParser::ArrayContext::INT(size_t i) {
  return getToken(TParser::INT, i);
}

std::vector<tree::TerminalNode *> TParser::ArrayContext::Comma() {
  return getTokens(TParser::Comma);
}

tree::TerminalNode* TParser::ArrayContext::Comma(size_t i) {
  return getToken(TParser::Comma, i);
}


size_t TParser::ArrayContext::getRuleIndex() const {
  return TParser::RuleArray;
}

void TParser::ArrayContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterArray(this);
}

void TParser::ArrayContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitArray(this);
}


antlrcpp::Any TParser::ArrayContext::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitArray(this);
  else
    return visitor->visitChildren(this);
}

TParser::ArrayContext* TParser::array() {
  ArrayContext *_localctx = _tracker.createInstance<ArrayContext>(_ctx, getState());
  enterRule(_localctx, 20, TParser::RuleArray);
  size_t _la = 0;

  auto onExit = finally([=] {
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(127);
    match(TParser::OpenCurly);
    setState(128);
    dynamic_cast<ArrayContext *>(_localctx)->intToken = match(TParser::INT);
    dynamic_cast<ArrayContext *>(_localctx)->el.push_back(dynamic_cast<ArrayContext *>(_localctx)->intToken);
    setState(133);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == TParser::Comma) {
      setState(129);
      match(TParser::Comma);
      setState(130);
      dynamic_cast<ArrayContext *>(_localctx)->intToken = match(TParser::INT);
      dynamic_cast<ArrayContext *>(_localctx)->el.push_back(dynamic_cast<ArrayContext *>(_localctx)->intToken);
      setState(135);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(136);
    match(TParser::CloseCurly);
   
  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- IdarrayContext ------------------------------------------------------------------

TParser::IdarrayContext::IdarrayContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}

tree::TerminalNode* TParser::IdarrayContext::OpenCurly() {
  return getToken(TParser::OpenCurly, 0);
}

tree::TerminalNode* TParser::IdarrayContext::CloseCurly() {
  return getToken(TParser::CloseCurly, 0);
}

std::vector<TParser::IdContext *> TParser::IdarrayContext::id() {
  return getRuleContexts<TParser::IdContext>();
}

TParser::IdContext* TParser::IdarrayContext::id(size_t i) {
  return getRuleContext<TParser::IdContext>(i);
}

std::vector<tree::TerminalNode *> TParser::IdarrayContext::Comma() {
  return getTokens(TParser::Comma);
}

tree::TerminalNode* TParser::IdarrayContext::Comma(size_t i) {
  return getToken(TParser::Comma, i);
}


size_t TParser::IdarrayContext::getRuleIndex() const {
  return TParser::RuleIdarray;
}

void TParser::IdarrayContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterIdarray(this);
}

void TParser::IdarrayContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitIdarray(this);
}


antlrcpp::Any TParser::IdarrayContext::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitIdarray(this);
  else
    return visitor->visitChildren(this);
}

TParser::IdarrayContext* TParser::idarray() {
  IdarrayContext *_localctx = _tracker.createInstance<IdarrayContext>(_ctx, getState());
  enterRule(_localctx, 22, TParser::RuleIdarray);
  size_t _la = 0;

  auto onExit = finally([=] {
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(138);
    match(TParser::OpenCurly);
    setState(139);
    dynamic_cast<IdarrayContext *>(_localctx)->idContext = id();
    dynamic_cast<IdarrayContext *>(_localctx)->element.push_back(dynamic_cast<IdarrayContext *>(_localctx)->idContext);
    setState(144);
    _errHandler->sync(this);
    _la = _input->LA(1);
    while (_la == TParser::Comma) {
      setState(140);
      match(TParser::Comma);
      setState(141);
      dynamic_cast<IdarrayContext *>(_localctx)->idContext = id();
      dynamic_cast<IdarrayContext *>(_localctx)->element.push_back(dynamic_cast<IdarrayContext *>(_localctx)->idContext);
      setState(146);
      _errHandler->sync(this);
      _la = _input->LA(1);
    }
    setState(147);
    match(TParser::CloseCurly);
   
  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

//----------------- AnyContext ------------------------------------------------------------------

TParser::AnyContext::AnyContext(ParserRuleContext *parent, size_t invokingState)
  : ParserRuleContext(parent, invokingState) {
}


size_t TParser::AnyContext::getRuleIndex() const {
  return TParser::RuleAny;
}

void TParser::AnyContext::enterRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->enterAny(this);
}

void TParser::AnyContext::exitRule(tree::ParseTreeListener *listener) {
  auto parserListener = dynamic_cast<TParserListener *>(listener);
  if (parserListener != nullptr)
    parserListener->exitAny(this);
}


antlrcpp::Any TParser::AnyContext::accept(tree::ParseTreeVisitor *visitor) {
  if (auto parserVisitor = dynamic_cast<TParserVisitor*>(visitor))
    return parserVisitor->visitAny(this);
  else
    return visitor->visitChildren(this);
}

TParser::AnyContext* TParser::any() {
  AnyContext *_localctx = _tracker.createInstance<AnyContext>(_ctx, getState());
  enterRule(_localctx, 24, TParser::RuleAny);

  auto onExit = finally([=] {
    exitRule();
  });
  try {
    enterOuterAlt(_localctx, 1);
    setState(149);
    dynamic_cast<AnyContext *>(_localctx)->t = matchWildcard();
   
  }
  catch (RecognitionException &e) {
    _errHandler->reportError(this, e);
    _localctx->exception = std::current_exception();
    _errHandler->recover(this, _localctx->exception);
  }

  return _localctx;
}

bool TParser::sempred(RuleContext *context, size_t ruleIndex, size_t predicateIndex) {
  switch (ruleIndex) {
    case 1: return divideSempred(dynamic_cast<DivideContext *>(context), predicateIndex);
    case 3: return conquerSempred(dynamic_cast<ConquerContext *>(context), predicateIndex);
    case 7: return exprSempred(dynamic_cast<ExprContext *>(context), predicateIndex);

  default:
    break;
  }
  return true;
}

bool TParser::divideSempred(DivideContext *_localctx, size_t predicateIndex) {
  switch (predicateIndex) {
    case 0: return doesItBlend();

  default:
    break;
  }
  return true;
}

bool TParser::conquerSempred(ConquerContext *_localctx, size_t predicateIndex) {
  switch (predicateIndex) {
    case 1: return doesItBlend();

  default:
    break;
  }
  return true;
}

bool TParser::exprSempred(ExprContext *_localctx, size_t predicateIndex) {
  switch (predicateIndex) {
    case 2: return precpred(_ctx, 9);
    case 3: return precpred(_ctx, 8);
    case 4: return precpred(_ctx, 6);
    case 5: return precpred(_ctx, 5);

  default:
    break;
  }
  return true;
}

// Static vars and initialization.
std::vector<dfa::DFA> TParser::_decisionToDFA;
atn::PredictionContextCache TParser::_sharedContextCache;

// We own the ATN which in turn owns the ATN states.
atn::ATN TParser::_atn;
std::vector<uint16_t> TParser::_serializedATN;

std::vector<std::string> TParser::_ruleNames = {
  "main", "divide", "and_", "conquer", "unused", "unused2", "stat", "expr", 
  "flowControl", "id", "array", "idarray", "any"
};

std::vector<std::string> TParser::_literalNames = {
  "", "", "'return'", "'continue'", "", "", "", "'<'", "'>'", "'='", "'and'", 
  "':'", "';'", "'+'", "'-'", "'*'", "'('", "')'", "'{'", "'}'", "'?'", 
  "','", "", "", "", "", "", "", "'.'", "'..'", "'$'", "'&'"
};

std::vector<std::string> TParser::_symbolicNames = {
  "", "DUMMY", "Return", "Continue", "INT", "Digit", "ID", "LessThan", "GreaterThan", 
  "Equal", "And", "Colon", "Semicolon", "Plus", "Minus", "Star", "OpenPar", 
  "ClosePar", "OpenCurly", "CloseCurly", "QuestionMark", "Comma", "String", 
  "Foo", "Bar", "Any", "Comment", "WS", "Dot", "DotDot", "Dollar", "Ampersand"
};

dfa::Vocabulary TParser::_vocabulary(_literalNames, _symbolicNames);

std::vector<std::string> TParser::_tokenNames;

TParser::Initializer::Initializer() {
	for (size_t i = 0; i < _symbolicNames.size(); ++i) {
		std::string name = _vocabulary.getLiteralName(i);
		if (name.empty()) {
			name = _vocabulary.getSymbolicName(i);
		}

		if (name.empty()) {
			_tokenNames.push_back("<INVALID>");
		} else {
      _tokenNames.push_back(name);
    }
	}

  _serializedATN = {
    0x3, 0x608b, 0xa72a, 0x8133, 0xb9ed, 0x417c, 0x3be7, 0x7786, 0x5964, 
    0x3, 0x21, 0x9a, 0x4, 0x2, 0x9, 0x2, 0x4, 0x3, 0x9, 0x3, 0x4, 0x4, 0x9, 
    0x4, 0x4, 0x5, 0x9, 0x5, 0x4, 0x6, 0x9, 0x6, 0x4, 0x7, 0x9, 0x7, 0x4, 
    0x8, 0x9, 0x8, 0x4, 0x9, 0x9, 0x9, 0x4, 0xa, 0x9, 0xa, 0x4, 0xb, 0x9, 
    0xb, 0x4, 0xc, 0x9, 0xc, 0x4, 0xd, 0x9, 0xd, 0x4, 0xe, 0x9, 0xe, 0x3, 
    0x2, 0x6, 0x2, 0x1e, 0xa, 0x2, 0xd, 0x2, 0xe, 0x2, 0x1f, 0x3, 0x2, 0x3, 
    0x2, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x5, 0x3, 0x28, 0xa, 0x3, 
    0x3, 0x3, 0x3, 0x3, 0x3, 0x4, 0x3, 0x4, 0x3, 0x5, 0x6, 0x5, 0x2f, 0xa, 
    0x5, 0xd, 0x5, 0xe, 0x5, 0x30, 0x3, 0x5, 0x3, 0x5, 0x3, 0x5, 0x3, 0x5, 
    0x3, 0x5, 0x3, 0x5, 0x7, 0x5, 0x39, 0xa, 0x5, 0xc, 0x5, 0xe, 0x5, 0x3c, 
    0xb, 0x5, 0x3, 0x5, 0x5, 0x5, 0x3f, 0xa, 0x5, 0x3, 0x5, 0x5, 0x5, 0x42, 
    0xa, 0x5, 0x3, 0x6, 0x3, 0x6, 0x3, 0x7, 0x3, 0x7, 0x3, 0x7, 0x6, 0x7, 
    0x49, 0xa, 0x7, 0xd, 0x7, 0xe, 0x7, 0x4a, 0x3, 0x7, 0x5, 0x7, 0x4e, 
    0xa, 0x7, 0x3, 0x7, 0x3, 0x7, 0x3, 0x8, 0x3, 0x8, 0x3, 0x8, 0x3, 0x8, 
    0x3, 0x8, 0x3, 0x8, 0x3, 0x8, 0x3, 0x8, 0x5, 0x8, 0x5a, 0xa, 0x8, 0x3, 
    0x9, 0x3, 0x9, 0x3, 0x9, 0x3, 0x9, 0x3, 0x9, 0x3, 0x9, 0x3, 0x9, 0x3, 
    0x9, 0x3, 0x9, 0x5, 0x9, 0x65, 0xa, 0x9, 0x3, 0x9, 0x3, 0x9, 0x3, 0x9, 
    0x3, 0x9, 0x3, 0x9, 0x3, 0x9, 0x3, 0x9, 0x3, 0x9, 0x3, 0x9, 0x3, 0x9, 
    0x3, 0x9, 0x3, 0x9, 0x3, 0x9, 0x3, 0x9, 0x3, 0x9, 0x7, 0x9, 0x76, 0xa, 
    0x9, 0xc, 0x9, 0xe, 0x9, 0x79, 0xb, 0x9, 0x3, 0xa, 0x3, 0xa, 0x3, 0xa, 
    0x5, 0xa, 0x7e, 0xa, 0xa, 0x3, 0xb, 0x3, 0xb, 0x3, 0xc, 0x3, 0xc, 0x3, 
    0xc, 0x3, 0xc, 0x7, 0xc, 0x86, 0xa, 0xc, 0xc, 0xc, 0xe, 0xc, 0x89, 0xb, 
    0xc, 0x3, 0xc, 0x3, 0xc, 0x3, 0xd, 0x3, 0xd, 0x3, 0xd, 0x3, 0xd, 0x7, 
    0xd, 0x91, 0xa, 0xd, 0xc, 0xd, 0xe, 0xd, 0x94, 0xb, 0xd, 0x3, 0xd, 0x3, 
    0xd, 0x3, 0xe, 0x3, 0xe, 0x3, 0xe, 0x3, 0x3e, 0x3, 0x10, 0xf, 0x2, 0x4, 
    0x6, 0x8, 0xa, 0xc, 0xe, 0x10, 0x12, 0x14, 0x16, 0x18, 0x1a, 0x2, 0x4, 
    0x3, 0x2, 0xd, 0xf, 0x3, 0x2, 0xe, 0xe, 0x2, 0xa1, 0x2, 0x1d, 0x3, 0x2, 
    0x2, 0x2, 0x4, 0x23, 0x3, 0x2, 0x2, 0x2, 0x6, 0x2b, 0x3, 0x2, 0x2, 0x2, 
    0x8, 0x41, 0x3, 0x2, 0x2, 0x2, 0xa, 0x43, 0x3, 0x2, 0x2, 0x2, 0xc, 0x48, 
    0x3, 0x2, 0x2, 0x2, 0xe, 0x59, 0x3, 0x2, 0x2, 0x2, 0x10, 0x64, 0x3, 
    0x2, 0x2, 0x2, 0x12, 0x7d, 0x3, 0x2, 0x2, 0x2, 0x14, 0x7f, 0x3, 0x2, 
    0x2, 0x2, 0x16, 0x81, 0x3, 0x2, 0x2, 0x2, 0x18, 0x8c, 0x3, 0x2, 0x2, 
    0x2, 0x1a, 0x97, 0x3, 0x2, 0x2, 0x2, 0x1c, 0x1e, 0x5, 0xe, 0x8, 0x2, 
    0x1d, 0x1c, 0x3, 0x2, 0x2, 0x2, 0x1e, 0x1f, 0x3, 0x2, 0x2, 0x2, 0x1f, 
    0x1d, 0x3, 0x2, 0x2, 0x2, 0x1f, 0x20, 0x3, 0x2, 0x2, 0x2, 0x20, 0x21, 
    0x3, 0x2, 0x2, 0x2, 0x21, 0x22, 0x7, 0x2, 0x2, 0x3, 0x22, 0x3, 0x3, 
    0x2, 0x2, 0x2, 0x23, 0x27, 0x7, 0x8, 0x2, 0x2, 0x24, 0x25, 0x5, 0x6, 
    0x4, 0x2, 0x25, 0x26, 0x7, 0xa, 0x2, 0x2, 0x26, 0x28, 0x3, 0x2, 0x2, 
    0x2, 0x27, 0x24, 0x3, 0x2, 0x2, 0x2, 0x27, 0x28, 0x3, 0x2, 0x2, 0x2, 
    0x28, 0x29, 0x3, 0x2, 0x2, 0x2, 0x29, 0x2a, 0x6, 0x3, 0x2, 0x2, 0x2a, 
    0x5, 0x3, 0x2, 0x2, 0x2, 0x2b, 0x2c, 0x7, 0xc, 0x2, 0x2, 0x2c, 0x7, 
    0x3, 0x2, 0x2, 0x2, 0x2d, 0x2f, 0x5, 0x4, 0x3, 0x2, 0x2e, 0x2d, 0x3, 
    0x2, 0x2, 0x2, 0x2f, 0x30, 0x3, 0x2, 0x2, 0x2, 0x30, 0x2e, 0x3, 0x2, 
    0x2, 0x2, 0x30, 0x31, 0x3, 0x2, 0x2, 0x2, 0x31, 0x42, 0x3, 0x2, 0x2, 
    0x2, 0x32, 0x33, 0x6, 0x5, 0x3, 0x2, 0x33, 0x34, 0x5, 0x6, 0x4, 0x2, 
    0x34, 0x35, 0x8, 0x5, 0x1, 0x2, 0x35, 0x42, 0x3, 0x2, 0x2, 0x2, 0x36, 
    0x3e, 0x7, 0x8, 0x2, 0x2, 0x37, 0x39, 0x7, 0x9, 0x2, 0x2, 0x38, 0x37, 
    0x3, 0x2, 0x2, 0x2, 0x39, 0x3c, 0x3, 0x2, 0x2, 0x2, 0x3a, 0x38, 0x3, 
    0x2, 0x2, 0x2, 0x3a, 0x3b, 0x3, 0x2, 0x2, 0x2, 0x3b, 0x3d, 0x3, 0x2, 
    0x2, 0x2, 0x3c, 0x3a, 0x3, 0x2, 0x2, 0x2, 0x3d, 0x3f, 0x5, 0x4, 0x3, 
    0x2, 0x3e, 0x3f, 0x3, 0x2, 0x2, 0x2, 0x3e, 0x3a, 0x3, 0x2, 0x2, 0x2, 
    0x3f, 0x40, 0x3, 0x2, 0x2, 0x2, 0x40, 0x42, 0x8, 0x5, 0x1, 0x2, 0x41, 
    0x2e, 0x3, 0x2, 0x2, 0x2, 0x41, 0x32, 0x3, 0x2, 0x2, 0x2, 0x41, 0x36, 
    0x3, 0x2, 0x2, 0x2, 0x42, 0x9, 0x3, 0x2, 0x2, 0x2, 0x43, 0x44, 0x5, 
    0xe, 0x8, 0x2, 0x44, 0xb, 0x3, 0x2, 0x2, 0x2, 0x45, 0x46, 0x5, 0xa, 
    0x6, 0x2, 0x46, 0x47, 0xb, 0x2, 0x2, 0x2, 0x47, 0x49, 0x3, 0x2, 0x2, 
    0x2, 0x48, 0x45, 0x3, 0x2, 0x2, 0x2, 0x49, 0x4a, 0x3, 0x2, 0x2, 0x2, 
    0x4a, 0x48, 0x3, 0x2, 0x2, 0x2, 0x4a, 0x4b, 0x3, 0x2, 0x2, 0x2, 0x4b, 
    0x4d, 0x3, 0x2, 0x2, 0x2, 0x4c, 0x4e, 0x9, 0x2, 0x2, 0x2, 0x4d, 0x4c, 
    0x3, 0x2, 0x2, 0x2, 0x4d, 0x4e, 0x3, 0x2, 0x2, 0x2, 0x4e, 0x4f, 0x3, 
    0x2, 0x2, 0x2, 0x4f, 0x50, 0xa, 0x3, 0x2, 0x2, 0x50, 0xd, 0x3, 0x2, 
    0x2, 0x2, 0x51, 0x52, 0x5, 0x10, 0x9, 0x2, 0x52, 0x53, 0x7, 0xb, 0x2, 
    0x2, 0x53, 0x54, 0x5, 0x10, 0x9, 0x2, 0x54, 0x55, 0x7, 0xe, 0x2, 0x2, 
    0x55, 0x5a, 0x3, 0x2, 0x2, 0x2, 0x56, 0x57, 0x5, 0x10, 0x9, 0x2, 0x57, 
    0x58, 0x7, 0xe, 0x2, 0x2, 0x58, 0x5a, 0x3, 0x2, 0x2, 0x2, 0x59, 0x51, 
    0x3, 0x2, 0x2, 0x2, 0x59, 0x56, 0x3, 0x2, 0x2, 0x2, 0x5a, 0xf, 0x3, 
    0x2, 0x2, 0x2, 0x5b, 0x5c, 0x8, 0x9, 0x1, 0x2, 0x5c, 0x5d, 0x7, 0x12, 
    0x2, 0x2, 0x5d, 0x5e, 0x5, 0x10, 0x9, 0x2, 0x5e, 0x5f, 0x7, 0x13, 0x2, 
    0x2, 0x5f, 0x65, 0x3, 0x2, 0x2, 0x2, 0x60, 0x65, 0x5, 0x14, 0xb, 0x2, 
    0x61, 0x65, 0x5, 0x12, 0xa, 0x2, 0x62, 0x65, 0x7, 0x6, 0x2, 0x2, 0x63, 
    0x65, 0x7, 0x18, 0x2, 0x2, 0x64, 0x5b, 0x3, 0x2, 0x2, 0x2, 0x64, 0x60, 
    0x3, 0x2, 0x2, 0x2, 0x64, 0x61, 0x3, 0x2, 0x2, 0x2, 0x64, 0x62, 0x3, 
    0x2, 0x2, 0x2, 0x64, 0x63, 0x3, 0x2, 0x2, 0x2, 0x65, 0x77, 0x3, 0x2, 
    0x2, 0x2, 0x66, 0x67, 0xc, 0xb, 0x2, 0x2, 0x67, 0x68, 0x7, 0x11, 0x2, 
    0x2, 0x68, 0x76, 0x5, 0x10, 0x9, 0xc, 0x69, 0x6a, 0xc, 0xa, 0x2, 0x2, 
    0x6a, 0x6b, 0x7, 0xf, 0x2, 0x2, 0x6b, 0x76, 0x5, 0x10, 0x9, 0xb, 0x6c, 
    0x6d, 0xc, 0x8, 0x2, 0x2, 0x6d, 0x6e, 0x7, 0x16, 0x2, 0x2, 0x6e, 0x6f, 
    0x5, 0x10, 0x9, 0x2, 0x6f, 0x70, 0x7, 0xd, 0x2, 0x2, 0x70, 0x71, 0x5, 
    0x10, 0x9, 0x8, 0x71, 0x76, 0x3, 0x2, 0x2, 0x2, 0x72, 0x73, 0xc, 0x7, 
    0x2, 0x2, 0x73, 0x74, 0x7, 0xb, 0x2, 0x2, 0x74, 0x76, 0x5, 0x10, 0x9, 
    0x7, 0x75, 0x66, 0x3, 0x2, 0x2, 0x2, 0x75, 0x69, 0x3, 0x2, 0x2, 0x2, 
    0x75, 0x6c, 0x3, 0x2, 0x2, 0x2, 0x75, 0x72, 0x3, 0x2, 0x2, 0x2, 0x76, 
    0x79, 0x3, 0x2, 0x2, 0x2, 0x77, 0x75, 0x3, 0x2, 0x2, 0x2, 0x77, 0x78, 
    0x3, 0x2, 0x2, 0x2, 0x78, 0x11, 0x3, 0x2, 0x2, 0x2, 0x79, 0x77, 0x3, 
    0x2, 0x2, 0x2, 0x7a, 0x7b, 0x7, 0x4, 0x2, 0x2, 0x7b, 0x7e, 0x5, 0x10, 
    0x9, 0x2, 0x7c, 0x7e, 0x7, 0x5, 0x2, 0x2, 0x7d, 0x7a, 0x3, 0x2, 0x2, 
    0x2, 0x7d, 0x7c, 0x3, 0x2, 0x2, 0x2, 0x7e, 0x13, 0x3, 0x2, 0x2, 0x2, 
    0x7f, 0x80, 0x7, 0x8, 0x2, 0x2, 0x80, 0x15, 0x3, 0x2, 0x2, 0x2, 0x81, 
    0x82, 0x7, 0x14, 0x2, 0x2, 0x82, 0x87, 0x7, 0x6, 0x2, 0x2, 0x83, 0x84, 
    0x7, 0x17, 0x2, 0x2, 0x84, 0x86, 0x7, 0x6, 0x2, 0x2, 0x85, 0x83, 0x3, 
    0x2, 0x2, 0x2, 0x86, 0x89, 0x3, 0x2, 0x2, 0x2, 0x87, 0x85, 0x3, 0x2, 
    0x2, 0x2, 0x87, 0x88, 0x3, 0x2, 0x2, 0x2, 0x88, 0x8a, 0x3, 0x2, 0x2, 
    0x2, 0x89, 0x87, 0x3, 0x2, 0x2, 0x2, 0x8a, 0x8b, 0x7, 0x15, 0x2, 0x2, 
    0x8b, 0x17, 0x3, 0x2, 0x2, 0x2, 0x8c, 0x8d, 0x7, 0x14, 0x2, 0x2, 0x8d, 
    0x92, 0x5, 0x14, 0xb, 0x2, 0x8e, 0x8f, 0x7, 0x17, 0x2, 0x2, 0x8f, 0x91, 
    0x5, 0x14, 0xb, 0x2, 0x90, 0x8e, 0x3, 0x2, 0x2, 0x2, 0x91, 0x94, 0x3, 
    0x2, 0x2, 0x2, 0x92, 0x90, 0x3, 0x2, 0x2, 0x2, 0x92, 0x93, 0x3, 0x2, 
    0x2, 0x2, 0x93, 0x95, 0x3, 0x2, 0x2, 0x2, 0x94, 0x92, 0x3, 0x2, 0x2, 
    0x2, 0x95, 0x96, 0x7, 0x15, 0x2, 0x2, 0x96, 0x19, 0x3, 0x2, 0x2, 0x2, 
    0x97, 0x98, 0xb, 0x2, 0x2, 0x2, 0x98, 0x1b, 0x3, 0x2, 0x2, 0x2, 0x11, 
    0x1f, 0x27, 0x30, 0x3a, 0x3e, 0x41, 0x4a, 0x4d, 0x59, 0x64, 0x75, 0x77, 
    0x7d, 0x87, 0x92, 
  };

  atn::ATNDeserializer deserializer;
  _atn = deserializer.deserialize(_serializedATN);

  size_t count = _atn.getNumberOfDecisions();
  _decisionToDFA.reserve(count);
  for (size_t i = 0; i < count; i++) { 
    _decisionToDFA.emplace_back(_atn.getDecisionState(i), i);
  }
}

TParser::Initializer TParser::_init;
