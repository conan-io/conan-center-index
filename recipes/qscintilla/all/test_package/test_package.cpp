#include <Qsci/qscilexercpp.h>
#include <Qsci/qsciscintilla.h>

#include <QApplication>

#include <iostream>

// The widget code is always compiled and linked (what Octave's editor uses), but only run when
// an argument is given: starting QApplication needs a Qt platform plugin, which is not available
// in every Qt configuration (e.g. static Qt without a linked platform plugin, or headless CI).
static int run_widget(int argc, char *argv[]) {
    QApplication app(argc, argv);

    QsciScintilla editor;
    QsciLexerCPP lexer;
    editor.setLexer(&lexer);
    editor.setText("int main() { return 0; }");
    editor.setFolding(QsciScintilla::BoxedTreeFoldStyle);

    std::cout << "QScintilla lexer: " << lexer.language() << ", lines: " << editor.lines() << std::endl;
    return editor.lines() == 1 ? 0 : 1;
}

int main(int argc, char *argv[]) {
    int modifiers = Qt::ControlModifier;
    const int key = QsciScintillaBase::commandKey(Qt::Key_A, modifiers);
    std::cout << "QScintilla " << QSCINTILLA_VERSION_STR << ", Ctrl+A -> Scintilla key " << key << std::endl;

    return argc > 1 ? run_widget(argc, argv) : 0;
}
