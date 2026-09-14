#main_window.py

import sys

from pathlib import Path

from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt, Signal, QPoint

from PySide6.QtWidgets import (
    QHBoxLayout,
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QTextEdit,
    QListWidget,
    QStackedWidget,
    QStackedLayout,
    QDialog,
    QDialogButtonBox,
    QListWidgetItem,
    QSizePolicy,
    QCalendarWidget,
    QMenu,
    QWidgetAction
    
    

)
from todo_model import (
    todo_list,
    task,
    import_files
)

#
#CREATE APP CUSTOM TITLE BAR
#
class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent

        self.setFixedHeight(20)

        self.title_label = QLabel("The Good Todo List")
        self.minimize_button = QPushButton("—")
        self.close_button = QPushButton("✕")

        self.minimize_button.clicked.connect(self.parent_window.showMinimized)
        self.close_button.clicked.connect(self.parent_window.close)

        layout = QHBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.close_button)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)

    def mouseDoubleClickEvent(self, event):
        if self.parent_window.isFullScreen():
            self.parent_window.showNormal()
        else:
            self.parent_window.showFullScreen()

class ResizeHandle(QWidget):
    def __init__(self, parent, edge):
        super().__init__(parent)

        self.parent_window = parent
        self.edge = edge

        if edge in (Qt.Edge.LeftEdge, Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edge in (Qt.Edge.TopEdge, Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif edge in (Qt.Edge.TopEdge | Qt.Edge.LeftEdge, Qt.Edge.BottomEdge | Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge in (Qt.Edge.TopEdge | Qt.Edge.RightEdge, Qt.Edge.BottomEdge | Qt.Edge.LeftEdge):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 30, 30, 160);
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent_window.windowHandle().startSystemResize(self.edge)


#
#CREATE VARIOUS APP POPUPS LIKE DATE SELECTOR, NEW LIST, AND RIGHT CLICK MENU
#
class DateSelectorPopup(QWidget):
    dateSelected = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)



        self.calendar = QCalendarWidget()
        day_table = self.calendar.findChild(QWidget, "qt_calendar_calendarview")
        if day_table:
            day_table.setAutoFillBackground(False)
        self.time_selector = QTimeEdit()
        self.cancel_button = QPushButton("Cancel")
        self.accept_button = QPushButton("Accept")
        self.date = None

        self.cancel_button.clicked.connect(self.close)
        self.accept_button.clicked.connect(self.on_accept)


        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.accept_button)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(self.time_selector)
        layout.addLayout(button_layout)
        self.setLayout(layout)


    def on_accept(self):
        print(f"Confirmed: {self.calendar.selectedDate().toString()} {self.time_selector.time().toString()}")
        self.date = f"{self.calendar.selectedDate().toString()} {self.time_selector.time().toString()}"
        self.dateSelected.emit(self.date)
        self.close()


class TaskRightClickMenuPopup(QWidget):
    deleteSelected = Signal()
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

        delete_button = QPushButton("Delete Task")
        delete_button.clicked.connect(self.reportDeleteTask)

        edit_button = QPushButton("Edit Task") 

        

        menu_stack = QVBoxLayout()
        menu_stack.addWidget(delete_button)
        menu_stack.addWidget(edit_button)
        menu_stack.setContentsMargins(0,0,0,0)
        menu_stack.setSpacing(0)


        self.setLayout(menu_stack)

    def reportDeleteTask(self):
        self.deleteSelected.emit()


class CreateListPopup(QWidget):
    nameSelected = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

        self.accept_button = QPushButton("Accept")
        self.accept_button.clicked.connect(self.reportLineName)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        button_layout = QHBoxLayout()
        self.new_list_name = None 

        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.cancel_button)



        self.new_list_line = QLineEdit()
        self.new_list_line.setPlaceholderText("Enter New List Name Here...")

        full_widget_layout = QVBoxLayout()

        full_widget_layout.addWidget(self.new_list_line)
        full_widget_layout.addLayout(button_layout)


        self.setLayout(full_widget_layout)

    def reportLineName(self):

        self.new_list_name = self.new_list_line.text()
        self.nameSelected.emit(self.new_list_name)

        self.close()


class ListRightClickMenuPopup(QWidget):
    deleteSelected = Signal()
    renameSelected = Signal()
    def __init__(self, parent):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(True)

        delete_button = QPushButton("Delete List")
        delete_button.clicked.connect(self.reportDeleteList)

        rename_button = QPushButton("Rename List")
        rename_button.clicked.connect(self.reportRenameList)  

        

        menu_stack = QVBoxLayout()
        menu_stack.addWidget(delete_button)
        menu_stack.addWidget(rename_button)
        menu_stack.setContentsMargins(0,0,0,0)
        menu_stack.setSpacing(0)


        self.setLayout(menu_stack)

    def reportDeleteList(self):
        self.deleteSelected.emit()
        self.close()

    def reportRenameList(self):
        self.renameSelected.emit()
        self.close()

#
#create classes for the task view objects, including custom interactive labels
#
class InteractiveLabel(QLabel):
    doubleClicked = Signal()
    rightClicked = Signal(QPoint)
    leftClicked = Signal()

    def __init__(self, text):
        super().__init__(text)
        # self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

    def mouseReleaseEvent(self, ev):
        print(ev.button())
        if ev.button() == Qt.MouseButton.LeftButton:
            self.leftClicked.emit()
        if ev.button() == Qt.MouseButton.RightButton:
            self.rightClicked.emit(ev.globalPos()) 

    def mouseDoubleClickEvent(self, ev):
        self.doubleClicked.emit()


class TaskLabel(QWidget):
    def __init__(self, task_view, parent_list, task_obj):
        super().__init__(task_view)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)


        self.parent_list = parent_list
        self.task_obj = task_obj
        self.task_view = task_view
        
        self.selected = False

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.text = task_obj.task_text
        self.deadline = task_obj.deadline
        self.status = task_obj.status
        self.priority = task_obj.priority
        self.time_created = task_obj.time
        self.notes = task_obj.notes

        self.label = InteractiveLabel(task_obj.task_text)
        self.label.leftClicked.connect(self.setSelected)
        self.label.rightClicked.connect(self.openRightClickMenu)
        self.label.doubleClicked.connect(self.editLabel)

        self.edit_label = QLineEdit(task_obj.task_text)
        self.edit_label.editingFinished.connect(self.returnLabel)

        self.status_checkbox = QCheckBox()
        if self.status == "Complete":
            self.status_checkbox.setChecked(True)
        self.status_checkbox.checkStateChanged.connect(self.toggleTaskStatus)
        
        self.complex_label = QStackedWidget()
        
        self.complex_label.addWidget(self.label)
        self.complex_label.addWidget(self.edit_label)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 10, 0)
        layout.addWidget(self.status_checkbox)
        layout.addWidget(self.complex_label)

    def editLabel(self):
        self.complex_label.setCurrentIndex(1)

    def returnLabel(self):
        self.task_obj.setText(self.edit_label.text())
        self.label.setText(self.task_obj.task_text)
        self.parent_list.save_to_file()
        self.complex_label.setCurrentIndex(0)

    def setDeadline(self, date):
        self.task_obj.setDeadline(date)
        self.deadline = self.task_obj.deadline
        self.parent_list.save_to_file()

    def setNotes(self, notes):
        self.task_obj.setNotes(notes)
        self.notes = notes
        self.parent_list.save_to_file()


    def toggleTaskStatus(self):
        if self.status_checkbox.isChecked() == True:
            self.task_obj.setStatus("Complete")
            print("updated status to complete")

        else:
            self.task_obj.setStatus("Incomplete")
            print("updated status to incomplete")

        self.parent_list.save_to_file()

    def setSelected(self):
        print("task set selected")
        self.task_view.setSelectedTask(self)

    def setSelectedVisualState(self, is_selected):
        self.setProperty("selected", is_selected)
        self.style().unpolish(self)
        self.style().polish(self)

    def setPriority(self, priority):
        self.task_obj.setPriority(priority)
        self.priority = self.task_obj.priority
        self.parent_list.save_to_file()

    def openRightClickMenu(self, point):
        print(f"Opening Right Click Menu!")

        self.right_click_menu_popup = TaskRightClickMenuPopup(self)
        self.right_click_menu_popup.move(point)
        self.right_click_menu_popup.show()
        self.right_click_menu_popup.deleteSelected.connect(self.deleteSelf)

    def deleteSelf(self):
        print("Im Deleting Myself.... no but fr tho")

        self.parent_list.tasks.remove(self.task_obj)
        self.parent_list.save_to_file()
        self.task_view.task_list.remove(self)
        self.setParent(None)

    


class TaskView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.task_list = []
        self.selected_task = None

        self.task_list_layout = QVBoxLayout()
        self.task_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        list_layout_container = QVBoxLayout()
        list_layout_container.addLayout(self.task_list_layout)
        list_layout_container.addStretch()


        self.due_date_display_button = QPushButton()
        self.due_date_display_button.clicked.connect(self.openDateSelectorPopup)
        self.priority_display_box = QComboBox()
        self.priority_display_box.addItems(["None", "Low", "Medium", "High"])
        self.priority_display_box.currentTextChanged.connect(self.setSelectedTaskPriority)

        right_side_top_bar = QHBoxLayout()

        right_side_top_bar.addWidget(self.due_date_display_button)
        right_side_top_bar.addStretch()
        right_side_top_bar.addWidget(self.priority_display_box)

        self.task_notes = QTextEdit()
        self.task_notes.setPlaceholderText("Type Notes Here...")
        self.task_notes.textChanged.connect(self.setSelectedTaskNotes)

        self.time_created_display = QLabel("a time")
        self.time_created_display.textFormat()
        right_side_bottom_bar = QHBoxLayout()
        right_side_bottom_bar.addStretch()
        right_side_bottom_bar.addWidget(self.time_created_display)


        right_side_layout = QVBoxLayout()
        right_side_layout.addLayout(right_side_top_bar)
        right_side_layout.addWidget(self.task_notes)
        right_side_layout.addLayout(right_side_bottom_bar)

        layout = QHBoxLayout(self)
        layout.addLayout(list_layout_container, 1)
        layout.addLayout(right_side_layout, 2)

    def setSelectedTaskNotes(self):
        self.selected_task.setNotes(self.task_notes.toMarkdown())

    def setSelectedTask(self, task):
        if task:
            print(f"Task selected { task.text}")
            if self.selected_task:
                self.selected_task.setSelectedVisualState(False)
            self.selected_task = task
            self.selected_task.setSelectedVisualState(True)

            self.due_date_display_button.setText(f"{task.deadline}")

            if task.priority == "Low":
                self.priority_display_box.setCurrentIndex(1)
            elif task.priority == "Medium":
                self.priority_display_box.setCurrentIndex(2)
            elif task.priority == "High":
                self.priority_display_box.setCurrentIndex(3)
            else:   
                self.priority_display_box.setCurrentIndex(0)


            self.task_notes.setMarkdown(task.notes)
            self.time_created_display.setText(f"Created: {task.time_created}")

    def openDateSelectorPopup(self):
        print(f"current due date{self.selected_task.deadline}")
        self.change_date_popup = DateSelectorPopup(self)
        pos = self.due_date_display_button.mapToGlobal(self.due_date_display_button.rect().bottomLeft())
        self.change_date_popup.move(pos)
        self.change_date_popup.show()
        self.change_date_popup.dateSelected.connect(lambda date: self.setSelectedTaskDueDate(date))

    def setSelectedTaskDueDate(self, date):
        self.selected_task.setDeadline(date)
        self.due_date_display_button.setText(f"{self.selected_task.deadline}")  

    def setSelectedTaskPriority(self, priority):
        print(f"Priority: {priority}")
        self.selected_task.setPriority(priority)



#
# MAIN WINDOW CLASS, 
#   Basically the main function, contains all app logic and functions

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.adjustSize()

        self.user_lists = import_files()
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)


        
        

                
        self.full_application = QHBoxLayout()

        self.left_vert_layout = QVBoxLayout()

        right_vert_layout = QVBoxLayout()

        self.task_display = TaskView(self)

        self.task_display.task_list = []






        #
        # LEFT PANNNEL LAYOUT
        #

        #creates the Add lists button in the top of the side pannel
        self.add_list_button = QPushButton("Add List")
        self.add_list_button.clicked.connect(self.openListAdder)
        self.left_vert_layout.addWidget(self.add_list_button)

        #creates the list of todo-lists in the side pannel
        self.list_of_lists = QListWidget()
        self.list_of_lists.currentItemChanged.connect(self.updateTaskDisplay)
        self.list_of_lists.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_of_lists.customContextMenuRequested.connect(self.showListContextMenu)
        for list_obj in self.user_lists:
            item = QListWidgetItem(list_obj.name)
            item.setData(Qt.UserRole, list_obj)
            self.list_of_lists.addItem(item)
        self.list_of_lists.setCurrentRow(0)
        self.left_vert_layout.addWidget(self.list_of_lists)

        #creates the settings button in the side pannel
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.showSettingsPannel)
        self.left_vert_layout.addWidget(self.settings_button)



        #
        # RIGHT PANNEL LAYOUT
        #

        #
        # TOP BAR LAYOUT
        right_top_bar_layout = QHBoxLayout()

        #Creates the task line editor in the top bar
        self.task_line_editor = QLineEdit()
        self.task_line_editor.returnPressed.connect(self.addTask)
        self.task_line_editor.setPlaceholderText("Type Task Here...")
        right_top_bar_layout.addWidget(self.task_line_editor, 7)

        #creates the calendar date selector button in the top bar 

        self.calendar_button = QPushButton("DueDate")
        self.calendar_button.clicked.connect(self.openDateSelector)
        self.new_task_duedate = None


        right_top_bar_layout.addWidget(self.calendar_button, 1)

        #creates the priority selector in the top bar
        self.priority_selector = QComboBox()
        self.priority_selector.addItems(["None", "Low", "Medium", "High"])
        self.new_task_priority = None
        self.priority_selector.currentTextChanged.connect(self.setNewTaskPriority)
        right_top_bar_layout.addWidget(self.priority_selector, 1)

        #set top bar margins
        right_top_bar_layout.setContentsMargins(10, 10, 10, 10)
        right_top_bar_layout.setSpacing(5)




        
        #
        #TASK DISPLAY LAYOUT



        #
        #COMBINE ALL LAYOUTS INTO ONE
        #

        
        # COMBINES THE LEFT AND RIGHT SIDE OF THE TASK DISPLAY LAYOUT

        # Sidebar panel
        sidebar_panel = QWidget()
        sidebar_panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        sidebar_panel.setObjectName("sidebarPanel")
        sidebar_panel.setLayout(self.left_vert_layout)

        # Right Side panel
        self.task_display.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.task_display.setObjectName("taskDisplay")

        right_top_panel = QWidget()
        right_top_panel.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        right_top_panel.setObjectName("rightTopPanel")
        right_top_panel.setLayout(right_top_bar_layout) 

        # COMBINES THE TOP BAR AND THE TASK DISPLAY LAYOUT
        right_vert_layout.addWidget(right_top_panel)
        right_vert_layout.addWidget(self.task_display)

        #COMBINES THE LEFT AND RIGHT STACK LAYOUTS
        self.full_application.addWidget(sidebar_panel, 1)
        self.full_application.addLayout(right_vert_layout, 3)
        self.full_application.setSpacing(10)


        #
        #UPDATE TODO_MODEL DATA
        #

        
        self.current_list = self.user_lists[0] if self.user_lists else self.addList("My First List!")

        self.title_bar = CustomTitleBar(self)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(8,0,8,8)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(self.title_bar)
        outer_layout.addLayout(self.full_application)

        central_widget = QWidget()
        central_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        central_widget.setObjectName("centralWidget")
        central_widget.setLayout(outer_layout)
        self.setCentralWidget(central_widget)

        #
        #CREATE CUSTOM BORDER WIDGETS
        #
        self.BORDER = 6
        self.edge_left = ResizeHandle(self, Qt.Edge.LeftEdge)
        self.edge_right = ResizeHandle(self, Qt.Edge.RightEdge)
        self.edge_top = ResizeHandle(self, Qt.Edge.TopEdge)
        self.edge_bottom = ResizeHandle(self, Qt.Edge.BottomEdge)
        self.edge_topleft = ResizeHandle(self, Qt.Edge.TopEdge | Qt.Edge.LeftEdge)
        self.edge_topright = ResizeHandle(self, Qt.Edge.TopEdge | Qt.Edge.RightEdge)
        self.edge_bottomleft = ResizeHandle(self, Qt.Edge.BottomEdge | Qt.Edge.LeftEdge)
        self.edge_bottomright = ResizeHandle(self, Qt.Edge.BottomEdge | Qt.Edge.RightEdge)

        style_path = Path(__file__).resolve().parent / "style.qss"
        self.setStyleSheet(style_path.read_text())

        self.reload_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        self.reload_shortcut.activated.connect(self.reloadStylesheet)

    def reloadStylesheet(self):
        style_path = Path(__file__).resolve().parent / "style.qss"
        self.setStyleSheet(style_path.read_text())
        print("Style Sheet Reloaded")


    def resizeEvent(self, event):
        print("starting resize event")
        super().resizeEvent(event)
        w, h, b = self.width(), self.height(), self.BORDER

        self.edge_top.setGeometry(b, 0, w - 2*b, b)
        self.edge_bottom.setGeometry(b, h - b, w - 2*b, b)
        self.edge_left.setGeometry(0, b, b, h - 2*b)
        self.edge_right.setGeometry(w - b, b, b, h - 2*b)

        self.edge_topleft.setGeometry(0, 0, b, b)
        self.edge_topright.setGeometry(w - b, 0, b, b)
        self.edge_bottomleft.setGeometry(0, h - b, b, b)
        self.edge_bottomright.setGeometry(w - b, h - b, b, b)

        for handle in (self.edge_top, self.edge_bottom, self.edge_left, self.edge_right,
                    self.edge_topleft, self.edge_topright, self.edge_bottomleft, self.edge_bottomright):
            handle.raise_()


    def openDateSelector(self):
        print(f"inprogress due date: {self.new_task_duedate}")
        self.date_popup = DateSelectorPopup(self)
        pos = self.calendar_button.mapToGlobal(self.calendar_button.rect().bottomLeft())
        self.date_popup.move(pos)
        self.date_popup.show()
        self.date_popup.dateSelected.connect(lambda date: self.setNewTaskDuedate(date))

    def setNewTaskDuedate(self, date):
        self.new_task_duedate = date

    def setNewTaskPriority(self, priority):
        print(f"New Task Priority: {priority}")
        self.new_task_priority = priority



    def openListAdder(self):
        print("add list")
        self.add_list_popup = CreateListPopup(self)
        self.add_list_popup.adjustSize()

        parent_center = self.mapToGlobal(self.rect().center())
        popup_offset = self.add_list_popup.rect().center()
        self.add_list_popup.move(parent_center - popup_offset)
        self.add_list_popup.show()
        self.add_list_popup.nameSelected.connect(lambda name: self.addList(name))

    def addList(self, name):
        new_list_name = name
    
        self.user_lists.append(todo_list(new_list_name))

        new_list = QListWidgetItem(new_list_name)
        new_list.setData(Qt.UserRole, self.user_lists[-1])
        self.list_of_lists.addItem(new_list)

    def addTask(self):
        print(f"add task {self.task_line_editor.text()}")

        if self.task_line_editor.text().strip() == "":
            print("No task to add")

        else:
            self.current_list.addTask(self.task_line_editor.text(), deadline_date= self.new_task_duedate, priority_level= self.new_task_priority )

            self.task_display.task_list.append(TaskLabel(self.task_display, self.current_list, self.current_list.tasks[-1]))

            #clear old task bar
            self.task_line_editor.clear()
            self.setNewTaskDuedate(None)
            self.priority_selector.setCurrentIndex(0)
            self.setNewTaskPriority(None)

            self.task_display.task_list_layout.addWidget(self.task_display.task_list[-1])

    def updateTaskDisplay(self, current):
        print("Updating task display!!")
        if current is not None:
            self.current_list = current.data(Qt.UserRole)
 
        for task in self.task_display.task_list:
            task.setParent(None)
        self.task_display.task_list = []

        for task in self.current_list.tasks:
            self.task_display.task_list.append(TaskLabel(self.task_display, self.current_list, task))

        for task in self.task_display.task_list:
            self.task_display.task_list_layout.addWidget(task)

        self.task_display.setSelectedTask(self.task_display.task_list[0] if self.task_display.task_list else None)


    def showSettingsPannel(self):
        print("Showing the settings pannel!!")

    def showListContextMenu(self, point):
        print("Showing Custom List Context Menu ")
        item = self.list_of_lists.itemAt(point)
        if item is None:
            return
        list_obj = item.data(Qt.UserRole)

        list_context_menu = ListRightClickMenuPopup(self)
        pos = self.list_of_lists.mapToGlobal(point)
        list_context_menu.move(pos)
        list_context_menu.show()
        list_context_menu.deleteSelected.connect(self.deleteList)

    def deleteList(self):
        # self.list_of_lists.currentItem().data(Qt.UserRole)
        self.current_list.deleteSelf()
        self.user_lists.remove(self.current_list)

        self.list_of_lists.currentItem().setHidden(True)

        self.list_of_lists.removeItemWidget(self.list_of_lists.currentItem())
        self.list_of_lists.setCurrentItem(self.list_of_lists.item(0))


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()