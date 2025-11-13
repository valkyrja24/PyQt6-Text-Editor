# 📝 PyQt6 Text Editor

A simple yet functional **text (and rich text) editor** built using **Python and PyQt6**.  
This project demonstrates how to create menus, toolbars, dialogs, and event handling in a GUI desktop application.

---

## 🚀 Features

✅ **File Operations**  
- New, Open, Save, Save As, Print  
- Prompts to save unsaved changes before exit  

✅ **Edit Operations**  
- Undo / Redo  
- Cut / Copy / Paste  
- Find & Replace dialog  

✅ **Formatting Tools**  
- Font and text color picker  
- Bold / Italic / Underline toggles  
- Text alignment (Left, Center, Right, Justify)

✅ **Interface Elements**  
- Menu bar  
- Toolbars (main + formatting)  
- Status bar  
- Dialog windows (font, color, file, print, about)

✅ **Other Features**  
- Keyboard shortcuts (Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+F, Ctrl+B, etc.)  
- Modified state indicator in window title  
- Cross-platform (Windows, macOS, Linux)

---

## 🛠 Requirements

- Python **3.9+**
- **PyQt6**

Install PyQt6 using:
```bash
pip install PyQt6
```

---

## ⚙️ Import Notes for PyQt6

PyQt6 has updated where certain classes are imported from.  
Make sure your import section includes this correction:

```python
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog, QMessageBox,
    QToolBar, QFontDialog, QColorDialog, QStatusBar, QDialog,
    QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox
)
from PyQt6.QtGui import (
    QIcon, QKeySequence, QTextCursor, QTextCharFormat, QAction
)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtCore import Qt, QFile, QTextStream, QSize
```

> ✅ **Note:** `QAction` must be imported from `PyQt6.QtGui`, not `PyQt6.QtWidgets`.

---

## 📂 Installation & Running

1. Clone or download this repository.  
2. Ensure Python and PyQt6 are installed.  
3. Run the application:

```bash
python text_editor.py
```

You should now see the text editor window open.

---

## 🌟 Conclusion

This PyQt6 Text Editor demonstrates how to build a fully functional, user-friendly text editing application with PyQt6.  
It includes menus, dialogs, and formatting tools that can serve as a solid foundation for further development.  

You can extend this project by adding:
- Syntax highlighting for code
- Tabbed document editing
- Auto-save and session restore
- Dark and light themes

Happy coding! 💻✨
