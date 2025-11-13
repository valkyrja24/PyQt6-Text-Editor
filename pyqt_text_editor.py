import sys
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

class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find & Replace")
        self.setModal(False)
        self.parent = parent

        self.find_label = QLabel("Find:")
        self.find_input = QLineEdit()
        self.replace_label = QLabel("Replace:")
        self.replace_input = QLineEdit()
        self.match_case = QCheckBox("Match case")
        self.whole_word = QCheckBox("Whole word")  # placeholder (not fully implemented)

        self.find_next_btn = QPushButton("Find Next")
        self.replace_btn = QPushButton("Replace")
        self.replace_all_btn = QPushButton("Replace All")
        self.close_btn = QPushButton("Close")

        h1 = QHBoxLayout()
        h1.addWidget(self.find_label)
        h1.addWidget(self.find_input)

        h2 = QHBoxLayout()
        h2.addWidget(self.replace_label)
        h2.addWidget(self.replace_input)

        h3 = QHBoxLayout()
        h3.addWidget(self.match_case)
        h3.addWidget(self.whole_word)

        h4 = QHBoxLayout()
        h4.addWidget(self.find_next_btn)
        h4.addWidget(self.replace_btn)
        h4.addWidget(self.replace_all_btn)
        h4.addWidget(self.close_btn)

        v = QVBoxLayout()
        v.addLayout(h1)
        v.addLayout(h2)
        v.addLayout(h3)
        v.addLayout(h4)
        self.setLayout(v)

        self.find_next_btn.clicked.connect(self.find_next)
        self.replace_btn.clicked.connect(self.replace_one)
        self.replace_all_btn.clicked.connect(self.replace_all)
        self.close_btn.clicked.connect(self.close)

    def find_next(self):
        text = self.find_input.text()
        if not text:
            return
        flags = QTextDocumentFindFlags = 0
        if self.match_case.isChecked():
            flags = Qt.FindFlag.FindCaseSensitively
        found = self.parent.text_edit.find(text, flags)
        if not found:
            # wrap search from top
            cursor = self.parent.text_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.parent.text_edit.setTextCursor(cursor)
            found = self.parent.text_edit.find(text, flags)
            if not found:
                QMessageBox.information(self, "Find", f"'{text}' not found.")

    def replace_one(self):
        cursor = self.parent.text_edit.textCursor()
        if cursor.hasSelection():
            selection = cursor.selectedText()
            find_text = self.find_input.text()
            if (self.match_case.isChecked() and selection == find_text) or \
               (not self.match_case.isChecked() and selection.lower() == find_text.lower()):
                cursor.insertText(self.replace_input.text())
                # move to next
        self.find_next()

    def replace_all(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        if not find_text:
            return
        # naive replace: operate on whole document text
        doc = self.parent.text_edit.document()
        cursor = QTextCursor(doc)
        text = doc.toPlainText()
        if not self.match_case.isChecked():
            # case-insensitive replace
            import re
            new_text = re.sub(re.escape(find_text), replace_text, text, flags=re.IGNORECASE)
        else:
            new_text = text.replace(find_text, replace_text)
        # replace entire document (keeps undo stack as single action)
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.insertText(new_text)

class TextEditorMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Text Editor")
        self.resize(900, 600)

        self.current_file = None
        self.is_modified = False

        # Central widget
        self.text_edit = QTextEdit()
        self.setCentralWidget(self.text_edit)
        self.text_edit.textChanged.connect(self.on_text_changed)

        # Menus and toolbars
        self.create_actions()
        self.create_menus()
        self.create_toolbars()
        self.create_statusbar()

        # Connect close event handling
        self.setWindowIcon(QIcon())  # default icon (could set a file)

    def create_actions(self):
        # File actions
        self.new_act = QAction("New", self, shortcut=QKeySequence.StandardKey.New, triggered=self.file_new)
        self.open_act = QAction("Open...", self, shortcut=QKeySequence.StandardKey.Open, triggered=self.file_open)
        self.save_act = QAction("Save", self, shortcut=QKeySequence.StandardKey.Save, triggered=self.file_save)
        self.save_as_act = QAction("Save As...", self, shortcut=QKeySequence("Ctrl+Shift+S"), triggered=self.file_save_as)
        self.print_act = QAction("Print...", self, shortcut=QKeySequence.StandardKey.Print, triggered=self.file_print)
        self.exit_act = QAction("Exit", self, shortcut=QKeySequence.StandardKey.Quit, triggered=self.close)

        # Edit actions
        self.undo_act = QAction("Undo", self, shortcut=QKeySequence.StandardKey.Undo, triggered=self.text_edit.undo)
        self.redo_act = QAction("Redo", self, shortcut=QKeySequence.StandardKey.Redo, triggered=self.text_edit.redo)
        self.cut_act = QAction("Cut", self, shortcut=QKeySequence.StandardKey.Cut, triggered=self.text_edit.cut)
        self.copy_act = QAction("Copy", self, shortcut=QKeySequence.StandardKey.Copy, triggered=self.text_edit.copy)
        self.paste_act = QAction("Paste", self, shortcut=QKeySequence.StandardKey.Paste, triggered=self.text_edit.paste)
        self.find_act = QAction("Find & Replace...", self, shortcut=QKeySequence("Ctrl+F"), triggered=self.open_find_replace)

        # Format actions
        self.font_act = QAction("Font...", self, triggered=self.select_font)
        self.color_act = QAction("Color...", self, triggered=self.select_color)
        self.bold_act = QAction("Bold", self, checkable=True, shortcut=QKeySequence("Ctrl+B"), triggered=self.toggle_bold)
        self.italic_act = QAction("Italic", self, checkable=True, shortcut=QKeySequence("Ctrl+I"), triggered=self.toggle_italic)
        self.underline_act = QAction("Underline", self, checkable=True, shortcut=QKeySequence("Ctrl+U"), triggered=self.toggle_underline)
        self.align_left_act = QAction("Align Left", self, triggered=lambda: self.set_alignment(Qt.AlignmentFlag.AlignLeft))
        self.align_center_act = QAction("Align Center", self, triggered=lambda: self.set_alignment(Qt.AlignmentFlag.AlignCenter))
        self.align_right_act = QAction("Align Right", self, triggered=lambda: self.set_alignment(Qt.AlignmentFlag.AlignRight))
        self.align_justify_act = QAction("Justify", self, triggered=lambda: self.set_alignment(Qt.AlignmentFlag.AlignJustify))

        # Help
        self.about_act = QAction("About", self, triggered=self.about)

    def create_menus(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.new_act)
        file_menu.addAction(self.open_act)
        file_menu.addAction(self.save_act)
        file_menu.addAction(self.save_as_act)
        file_menu.addSeparator()
        file_menu.addAction(self.print_act)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_act)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(self.undo_act)
        edit_menu.addAction(self.redo_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_act)
        edit_menu.addAction(self.copy_act)
        edit_menu.addAction(self.paste_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_act)

        # Format menu
        format_menu = menu_bar.addMenu("Format")
        format_menu.addAction(self.font_act)
        format_menu.addAction(self.color_act)
        format_menu.addSeparator()
        format_menu.addAction(self.bold_act)
        format_menu.addAction(self.italic_act)
        format_menu.addAction(self.underline_act)
        format_menu.addSeparator()
        align_menu = format_menu.addMenu("Alignment")
        align_menu.addAction(self.align_left_act)
        align_menu.addAction(self.align_center_act)
        align_menu.addAction(self.align_right_act)
        align_menu.addAction(self.align_justify_act)

        # View menu
        view_menu = menu_bar.addMenu("View")
        self.toggle_toolbar_act = QAction("Show/Hide Toolbars", self, checkable=True, checked=True, triggered=self.toggle_toolbars)
        view_menu.addAction(self.toggle_toolbar_act)

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self.about_act)

    def create_toolbars(self):
        # Main toolbar
        self.main_toolbar = QToolBar("Main")
        self.main_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.main_toolbar)
        self.main_toolbar.addAction(self.new_act)
        self.main_toolbar.addAction(self.open_act)
        self.main_toolbar.addAction(self.save_act)
        self.main_toolbar.addAction(self.print_act)

        # Formatting toolbar
        self.format_toolbar = QToolBar("Format")
        self.format_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.format_toolbar)
        self.format_toolbar.addAction(self.undo_act)
        self.format_toolbar.addAction(self.redo_act)
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(self.cut_act)
        self.format_toolbar.addAction(self.copy_act)
        self.format_toolbar.addAction(self.paste_act)
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(self.bold_act)
        self.format_toolbar.addAction(self.italic_act)
        self.format_toolbar.addAction(self.underline_act)
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(self.font_act)
        self.format_toolbar.addAction(self.color_act)

    def create_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

    # --------------- File operations -----------------
    def maybe_save(self):
        if not self.text_edit.document().isModified():
            return True
        ret = QMessageBox.warning(self, "Unsaved Changes",
                                  "The document has been modified.\nDo you want to save your changes?",
                                  QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        if ret == QMessageBox.StandardButton.Save:
            return self.file_save()
        elif ret == QMessageBox.StandardButton.Cancel:
            return False
        return True

    def file_new(self):
        if not self.maybe_save():
            return
        self.text_edit.clear()
        self.current_file = None
        self.text_edit.document().setModified(False)
        self.statusbar.showMessage("New file", 3000)
        self.setWindowTitle("Untitled - PyQt6 Text Editor")

    def file_open(self):
        if not self.maybe_save():
            return
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.text_edit.setPlainText(text)
                self.current_file = path
                self.text_edit.document().setModified(False)
                self.statusbar.showMessage(f"Opened '{path}'", 4000)
                self.setWindowTitle(f"{path} - PyQt6 Text Editor")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not read file:\n{e}")

    def file_save(self):
        if self.current_file:
            return self._save_to_path(self.current_file)
        else:
            return self.file_save_as()

    def file_save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Text Files (*.txt);;All Files (*)")
        if path:
            return self._save_to_path(path)
        return False

    def _save_to_path(self, path):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            self.current_file = path
            self.text_edit.document().setModified(False)
            self.statusbar.showMessage(f"Saved '{path}'", 4000)
            self.setWindowTitle(f"{path} - PyQt6 Text Editor")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
            return False

    def file_print(self):
        printer = QPrinter()
        dlg = QPrintDialog(printer, self)
        if dlg.exec() == QDialog.Accepted:
            self.text_edit.print(printer)

    # --------------- Edit / Format -----------------
    def on_text_changed(self):
        modified = self.text_edit.document().isModified()
        self.is_modified = modified
        title = (self.current_file if self.current_file else "Untitled") + (" *" if modified else "") + " - PyQt6 Text Editor"
        self.setWindowTitle(title)

    def select_font(self):
        ok, font = QFontDialog.getFont(self.text_edit.currentFont(), self, options=QFontDialog.FontDialogOption.DontUseNativeDialog)
        if ok:
            self.text_edit.setCurrentFont(font)

    def select_color(self):
        color = QColorDialog.getColor(self.text_edit.textColor(), self)
        if color.isValid():
            self.text_edit.setTextColor(color)

    def toggle_bold(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontWeight(75 if checked else 50)  # 75 = Bold, 50 = Normal
        self.merge_format_on_selection(fmt)

    def toggle_italic(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontItalic(checked)
        self.merge_format_on_selection(fmt)

    def toggle_underline(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(checked)
        self.merge_format_on_selection(fmt)

    def merge_format_on_selection(self, format_):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.mergeCharFormat(format_)
        self.text_edit.mergeCurrentCharFormat(format_)

    def set_alignment(self, alignment):
        self.text_edit.setAlignment(alignment)

    # --------------- Find & Replace -----------------
    def open_find_replace(self):
        if not hasattr(self, "_find_dialog") or self._find_dialog is None:
            self._find_dialog = FindReplaceDialog(self)
        self._find_dialog.show()
        self._find_dialog.raise_()
        self._find_dialog.activateWindow()

    # --------------- Helpers -----------------
    def toggle_toolbars(self, checked):
        if checked:
            self.addToolBar(self.main_toolbar)
            self.addToolBar(self.format_toolbar)
        else:
            self.removeToolBar(self.main_toolbar)
            self.removeToolBar(self.format_toolbar)

    def about(self):
        QMessageBox.about(self, "About PyQt6 Text Editor",
                          "<b>PyQt6 Text Editor</b><br>"
                          "Example application demonstrating menus, toolbars, dialogs and event handling.<br><br>"
                          "Built with PyQt6.")

    # Override close event to prompt saving
    def closeEvent(self, event):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()

def main():
    app = QApplication(sys.argv)
    win = TextEditorMainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
