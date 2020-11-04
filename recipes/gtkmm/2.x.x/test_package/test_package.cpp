/* Application main window
 *
 * Demonstrates a typical application window, with menubar, toolbar, statusbar.
 */

#include <gtkmm.h>

class Example_AppWindow : public Gtk::Window
{
public:
  Example_AppWindow();
  virtual ~Example_AppWindow();

protected:
  //Signal handlers:
  virtual void on_menu_item();
  virtual void on_text_changed();
  virtual void on_text_mark_set(const Gtk::TextBuffer::iterator& new_location, const Glib::RefPtr<Gtk::TextBuffer::Mark>& mark);

  //Member widgets:
  Gtk::Table m_Table;
  Gtk::Menu m_Menubar;
  Gtk::Toolbar m_Toolbar;
  Gtk::ScrolledWindow m_ScrolledWindow;
  Gtk::TextView m_TextView;
  Gtk::Statusbar m_Statusbar;
};


//Called by DemoWindow;
Gtk::Window* do_appwindow()
{
  return new Example_AppWindow();
}


Example_AppWindow::Example_AppWindow()
: m_Table(1, 4)
{
  set_title("Application Window");

  add(m_Table);

/*
  //Menu:
  {
    using namespace Gtk::Menu_Helpers;

    //File menu:
    Gtk::Menu* pMenuFile = Gtk::manage( new Gtk::Menu() );
    MenuList& list_file = pMenuFile->items();
    list_file.push_back( MenuElem("_New", "<control>N", sigc::mem_fun(*this, &Example_AppWindow::on_menu_item)) );
    list_file.push_back( MenuElem("_Open", "<control>O", sigc::mem_fun(*this, &Example_AppWindow::on_menu_item)) );
    list_file.push_back( MenuElem("_Save", "<control>S", sigc::mem_fun(*this, &Example_AppWindow::on_menu_item)) );
    list_file.push_back( MenuElem("Save _As", sigc::mem_fun(*this, &Example_AppWindow::on_menu_item)) );
    list_file.push_back(SeparatorElem());
    list_file.push_back( MenuElem("_Quit", "<control>Q", sigc::mem_fun(*this, &Example_AppWindow::on_menu_item)) );

    //Preferences menu:
    Gtk::Menu* pMenuPreferences = Gtk::manage( new Gtk::Menu() );
    MenuList& list_preferences = pMenuPreferences->items();

    // Create a submenu
    Gtk::Menu* pMenuSub_Color = Gtk::manage( new Gtk::Menu());
    MenuList& list_sub = pMenuSub_Color->items();
    list_sub.push_back( MenuElem("_Red", sigc::mem_fun(*this, &Example_AppWindow::on_menu_item)) );
    list_sub.push_back( MenuElem("_Green", sigc::mem_fun(*this, &Example_AppWindow::on_menu_item)) );
    list_sub.push_back( MenuElem("_Blue", sigc::mem_fun(*this, &Example_AppWindow::on_menu_item)) );

    list_preferences.push_back( MenuElem("_Color", *pMenuSub_Color) );

    // Create a submenu
    Gtk::Menu* pMenuSub_Shape = Gtk::manage( new Gtk::Menu());
    list_sub = pMenuSub_Shape->items();
    list_sub.push_back( MenuElem("_Square", sigc::mem_fun(*this, &Example_AppWindow::on_menu_item)) );
    list_sub.push_back( MenuElem("_Rectangle", sigc::mem_fun(*this, &Example_AppWindow::on_menu_item)) );
    list_sub.push_back( MenuElem("_Oval", sigc::mem_fun(*this, &Example_AppWindow::on_menu_item)) );

    list_preferences.push_back( MenuElem("_Shape", *pMenuSub_Shape) );

    //Help menu:
    Gtk::Menu* pMenuHelp = Gtk::manage( new Gtk::Menu() );
    MenuList& list_help = pMenuHelp->items();
    list_help.push_back( MenuElem("_About", sigc::mem_fun(*this, &Example_AppWindow::on_menu_item)) );


    //Create the menu bar
    MenuList& list_bar = m_Menubar.items();
    list_bar.push_front(MenuElem("_Help", *pMenuHelp));
    list_bar.front()->set_right_justified();
    list_bar.push_front(MenuElem("_Preferences", *pMenuPreferences));
    list_bar.push_front(MenuElem("_File", *pMenuFile));

    //Add the menu bar to the Table:
    m_Table.attach(m_Menubar,
                    // X direction             Y direction
                    0, 1,                      0, 1,
                    Gtk::FILL|Gtk::EXPAND, Gtk::AttachOptions(0)
                    );
  } //menu

*/
  //Toolbar:
  {
    m_Table.attach(m_Toolbar,
                   /* X direction */       /* Y direction */
                   0, 1,                   1, 2,
                   Gtk::FILL|Gtk::EXPAND, Gtk::AttachOptions(0)
                   );
  }


  m_ScrolledWindow.set_policy(Gtk::POLICY_AUTOMATIC, Gtk::POLICY_AUTOMATIC);
  m_ScrolledWindow.set_shadow_type(Gtk::SHADOW_IN);
  m_Table.attach(m_ScrolledWindow,
                 /* X direction */       /* Y direction */
                 0, 1,                   2, 3);

  set_default_size(200, 200);

  m_ScrolledWindow.add(m_TextView);


  /* Create statusbar */

  m_Table.attach(m_Statusbar,
                 /* X direction */       /* Y direction */
                 0, 1,                   3, 4,
                 Gtk::FILL|Gtk::EXPAND, Gtk::AttachOptions(0)
                 );


  /* Show text widget info in the statusbar */
  Glib::RefPtr<Gtk::TextBuffer> refTextBuffer = m_TextView.get_buffer();
  refTextBuffer->signal_changed().connect(sigc::mem_fun(*this, &Example_AppWindow::on_text_changed));
  refTextBuffer->signal_mark_set().connect(sigc::mem_fun(*this, &Example_AppWindow::on_text_mark_set));
  on_text_changed();

  show_all();
}

Example_AppWindow::~Example_AppWindow()
{
}

void Example_AppWindow::on_menu_item()
{
  Gtk::MessageDialog dialog(*this, "You selected or toggled the menu item", false,
                            Gtk::MESSAGE_INFO, Gtk::BUTTONS_CLOSE);
  dialog.run();
}

void Example_AppWindow::on_text_changed()
{
  m_Statusbar.pop();

  Glib::RefPtr<Gtk::TextBuffer> refBuffer = m_TextView.get_buffer();
  gint count = refBuffer->get_char_count();

  Gtk::TextBuffer::iterator iter = refBuffer->get_iter_at_mark(refBuffer->get_insert());

  gint row = iter.get_line();
  gint col = iter.get_line_offset();

  gchar* msg = g_strdup_printf ("Cursor at row %d column %d - %d chars in document",
                         row, col, count);
  m_Statusbar.push(msg);
  g_free (msg);
}


void Example_AppWindow::on_text_mark_set(const Gtk::TextBuffer::iterator&, const Glib::RefPtr<Gtk::TextBuffer::Mark>&)
{
  on_text_changed();
}

int main (int argc, char *argv[])
{
  Gtk::Main kit(argc, argv);

  Example_AppWindow window;

  return 0;
}
