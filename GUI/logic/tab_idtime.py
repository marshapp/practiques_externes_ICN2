from PyQt6.QtWidgets import QFileDialog, QWidget
from PyQt6.QtCore import Qt
from ui.file_entry_widget_3 import Ui_Form
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import logic.plot_idtime as plot_idtime
import os

class FileEntryWidget_3(QWidget, Ui_Form):
    def __init__(self, filepath):
        super().__init__()
        self.setupUi(self)
        self.filepath_3 = filepath
        filename = os.path.basename(filepath)
        self.filename_check.setText(filename)
        self.filename_check.setChecked(True)


class Tab3Handler:
    def __init__(self, main_window):
        self.w = main_window
        self.file_entries = []
        self.w.plot_button_3.setEnabled(False)
        self.w.save_plot_button_3.setEnabled(False)
        self.w.plot_mode_combo_3.currentTextChanged.connect(self.plot_mode_change)
        self.w.select_files_button_3.clicked.connect(self.select_files)
        self.w.plot_button_3.clicked.connect(self.plot)
        self.w.save_plot_button_3.clicked.connect(self.save_plot)
        self.w.unify_y_lims_check_3.setChecked(True)

    def update_positions(self):
        self.checked_entries = []
        for file_entry in self.file_entries:
            if file_entry.filename_check.isChecked():
                file_entry.position_combo.setEnabled(True)
                self.checked_entries.append(file_entry)
            else:
                file_entry.position_combo.setCurrentIndex(-1)
                file_entry.position_combo.setEnabled(False)

        self.n = len(self.checked_entries)

        positions = []
        for i in range(self.n):
            positions.append(str(i+1))

        for ix, file_entry in enumerate(self.checked_entries):
            file_entry.position_combo.clear()
            file_entry.position_combo.addItems(positions)
            file_entry.position_combo.setCurrentText(positions[ix])

        if len(self.checked_entries) == 0:
            self.w.plot_button_3.setEnabled(False)
        else:
            self.w.plot_button_3.setEnabled(True)        

    def select_files(self):
        filepaths, _ = QFileDialog.getOpenFileNames(self.w, "Select Data Files", "", "Excel Files (*.xlsx)")
        for filepath in filepaths:
            self.add_file_entry(filepath)
        self.w.plot_button_3.setEnabled(True)

    def add_file_entry(self, filepath):
        file_entry = FileEntryWidget_3(filepath)
        self.file_entries.append(file_entry)
        self.w.file_entries_widget_3.layout().addWidget(file_entry)
        file_entry.remove_button.clicked.connect(lambda: self.remove_file_entry(file_entry))
        file_entry.duplicate_button.clicked.connect(lambda: self.add_file_entry(file_entry.filepath_3))
        file_entry.y_scale_combo.currentTextChanged.connect(lambda text: self.y_scale_change(file_entry, text)) 
        file_entry.filename_check.clicked.connect(self.update_positions)
        self.update_positions()
        file_entry.legend_check.setChecked(True)

    def remove_file_entry(self, file_entry):
        self.w.file_entries_widget_3.layout().removeWidget(file_entry)
        file_entry.deleteLater()
        self.file_entries.remove(file_entry)
        self.update_positions()

    def y_scale_change(self, file_entry, text):
        if text == "log":
            file_entry.absolute_value_check.setChecked(True)
            file_entry.absolute_value_check.setEnabled(False)
        else:
            file_entry.absolute_value_check.setEnabled(True)

    def plot_mode_change(self):
        if self.w.plot_mode_combo_3.currentText() == "One Figure per File":
            self.w.unify_y_lims_check_3.show()
        else:
            self.w.unify_y_lims_check_3.hide()

    def plot(self):
                
        layout = self.w.plotting_widget_3.layout()
        
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        if self.w.plot_mode_combo_3.currentText() == "One Figure per File":
    
            if self.n == 1:
                self.rows, self.cols = 1, 1
            elif self.n == 2:
                self.rows, self.cols = 1, 2
            elif self.n == 3:
                self.rows, self.cols = 1, 3
            elif self.n == 4:
                self.rows, self.cols = 2, 2
            elif self.n in (5, 6):
                self.rows, self.cols = 2, 3
            elif self.n in (7, 8, 9):
                self.rows, self.cols = 3, 3
                
            fig = Figure()
            fig.subplots_adjust(hspace=0.5, wspace=0.5)
            
            canvas = FigureCanvas(fig)
            
            if self.w.saved_format_check_3.isChecked():
                canvas.setFixedSize((6 * self.cols + (self.cols - 1) * 3)*300, (4 * self.rows + (self.rows - 1) * 2)*300)
                layout.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignHCenter)
            else:
                layout.addWidget(canvas)
            
            y_limits = []

            for file_entry in self.checked_entries:
                
                position = int(file_entry.position_combo.currentText())
                ax = fig.add_subplot(self.rows, self.cols, position)
                
                filepath = file_entry.filepath_3
                legend = file_entry.legend_check.isChecked()
                colormap = file_entry.colormap_combo.currentText()
                y_scale= file_entry.y_scale_combo.currentText()
                current = file_entry.current_combo.currentText()
                absolute_value = file_entry.absolute_value_check.isChecked()
                fs = float(self.w.font_size_spin_3.value())
                lw = float(self.w.line_width_spin_3.value())
                ms = float(self.w.marker_size_spin_3.value())
            
                y_min, y_max = plot_idtime.plot(ax, legend, colormap, filepath, y_scale, current, absolute_value, fs, lw, ms)
                
                y_limits.append((y_min, y_max))

            if self.w.unify_y_lims_check_3.isChecked():
                y_mins = []
                y_maxs = []
                for i in y_limits:
                    y_mins.append(i[0])
                    y_maxs.append(i[1])
                    
                global_min = min(y_mins)
                global_max = max(y_maxs)
                
                for ax in fig.axes:
                    ax.set_ylim(global_min, global_max)
                    
        else:
            
            fig = Figure()
            canvas = FigureCanvas(fig)
            
            if self.w.saved_format_check_3.isChecked():
                canvas.setFixedSize(6*300, 4*300)
                layout.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignHCenter)
            else:
                layout.addWidget(canvas)
            
            ax = fig.add_subplot(111)
            
            y_limits = []
            
            for ix, file_entry in enumerate(self.checked_entries):
                  
                filepath = file_entry.filepath_3
                legend = file_entry.legend_check.isChecked()
                colormap = file_entry.colormap_combo.currentText()
                y_scale = file_entry.y_scale_combo.currentText()
                current = file_entry.current_combo.currentText()
                absolute_value = file_entry.absolute_value_check.isChecked()
                fs = float(self.w.font_size_spin_3.value())
                lw = float(self.w.line_width_spin_3.value())
                ms = float(self.w.marker_size_spin_3.value())
            
                y_min, y_max = plot_idtime.plot(ax, legend, colormap, filepath, y_scale, current, absolute_value, fs, lw, ms)
                
                y_limits.append((y_min, y_max))
            
            y_mins = []
            y_maxs = []
            for i in y_limits:
                y_mins.append(i[0])
                y_maxs.append(i[1])
                
            global_min = min(y_mins)
            global_max = max(y_maxs)

            ax.set_ylim(global_min, global_max)
        
        toolbar_layout = self.w.toolbar_widget_3.layout()
        
        while toolbar_layout.count():
            item = toolbar_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                
        toolbar_layout.addWidget(CustomToolbar(canvas, self.w), alignment=Qt.AlignmentFlag.AlignHCenter)
        
        if not self.w.saved_format_check_3.isChecked():
            ax.figure.set_constrained_layout(True)
        
        canvas.draw()
        
        self.w.save_plot_button_3.setEnabled(True)

    def save_plot(self):
        base, _ = QFileDialog.getSaveFileName(self.w, "Save Plot", "", "Images (*.png *.svg)")
        if not base:
            return
        layout = self.w.plotting_widget_3.layout()
        canvas = None
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                canvas = widget
                break
        if canvas:
            fig = canvas.figure
            root, _ = os.path.splitext(base)
            '''if self.w.plot_mode_combo_3.currentText() == "One Figure per File":
                fig.set_size_inches(6 * self.cols + (self.cols - 1) * 3, 4 * self.rows + (self.rows - 1) * 2)
            else:
                fig.set_size_inches(6, 4)'''
            fig.savefig(root + ".png", bbox_inches='tight', dpi=300)
            fig.savefig(root + ".svg", bbox_inches='tight')

class CustomToolbar(NavigationToolbar):
    toolitems = [
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        ('Customize', 'Edit axis, curve, and image parameters', 'qt4_editor_options', 'edit_parameters')
    ]
