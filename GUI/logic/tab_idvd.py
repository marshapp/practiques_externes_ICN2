from PyQt6.QtWidgets import QFileDialog, QWidget
from PyQt6.QtCore import Qt
from ui.file_entry_widget import Ui_file_entry_widget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import logic.plot_idvd as plot_idvd
import os

class FileEntryWidget(QWidget, Ui_file_entry_widget):
    def __init__(self, filepath):
        super().__init__()
        self.setupUi(self)
        self.filepath = filepath
        filename = os.path.basename(filepath)
        self.filename_check.setText(filename)
        self.filename_check.setChecked(True)

class Tab1Handler:
    def __init__(self, main_window):
        self.w = main_window
        self.file_entries = []
        self.w.plot_button.setEnabled(False)
        self.w.save_plot_button.setEnabled(False)
        self.w.select_files_button.clicked.connect(self.select_files)
        self.w.plot_button.clicked.connect(self.plot)
        self.w.save_plot_button.clicked.connect(self.save_plot)
        self.w.plot_mode_combo.currentTextChanged.connect(self.plot_mode_change)
        self.w.fill_between_widget.hide()
        self.w.y_scale_combo_fbw.currentTextChanged.connect(self.y_scale_change_fbw)
        self.w.unify_y_lims_check.setChecked(True)

    def update_positions(self): #para canviar la posicion de las figuras en el one figure per file
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
            self.w.plot_button.setEnabled(False)
        else:
            self.w.plot_button.setEnabled(True)

    def select_files(self):
        filepaths, _ = QFileDialog.getOpenFileNames(self.w, "Select Data Files", "", "Excel Files (*.xlsx)")
        for filepath in filepaths:
            self.add_file_entry(filepath)
        self.w.plot_button.setEnabled(True)

    def add_file_entry(self, filepath):
        file_entry = FileEntryWidget(filepath)
        self.file_entries.append(file_entry)
        self.plot_mode_change()
        self.w.file_entries_widget.layout().addWidget(file_entry)
        file_entry.remove_button.clicked.connect(lambda: self.remove_file_entry(file_entry))
        file_entry.duplicate_button.clicked.connect(lambda: self.add_file_entry(file_entry.filepath))
        file_entry.y_scale_combo.currentTextChanged.connect(lambda text: self.y_scale_change(file_entry, text))
        file_entry.x_scale_combo.currentTextChanged.connect(lambda text: self.x_scale_change(file_entry, text))
        file_entry.filename_check.clicked.connect(self.update_positions)
        self.update_positions()
        file_entry.legend_check.setChecked(True)

    def remove_file_entry(self, file_entry):
        self.w.file_entries_widget.layout().removeWidget(file_entry)
        file_entry.deleteLater()
        self.file_entries.remove(file_entry)
        self.update_positions()

    def y_scale_change(self, file_entry, text):
        if text == "log":
            file_entry.absolute_value_check.setChecked(True)
            file_entry.absolute_value_check.setEnabled(False)
        else:
            file_entry.absolute_value_check.setEnabled(True)

            
    def y_scale_change_fbw(self, text):
        if text == "log":
            self.w.absolute_value_check_fbw.setChecked(True)
            self.w.absolute_value_check_fbw.setEnabled(False)
        else:
            self.w.absolute_value_check_fbw.setEnabled(True)
        

    def x_scale_change(self, file_entry, text):
        index = file_entry.vd_region_combo.findText("both")
        if text == "log":
            if file_entry.vd_region_combo.currentText() == "both":
                file_entry.vd_region_combo.setCurrentText("pos")
            file_entry.vd_region_combo.model().item(index).setEnabled(False)
        else:
            file_entry.vd_region_combo.model().item(index).setEnabled(True)

    def plot_mode_change(self):
        if self.w.plot_mode_combo.currentText() == "Mean":
            for fe in self.file_entries:
                fe.duplicate_button.hide()
                fe.y_scale_combo.hide()
                fe.x_scale_combo.hide()
                fe.vd_region_combo.hide()
                fe.vg_format_combo.hide()
                fe.legend_check.hide()
                fe.colormap_combo.hide()
                fe.sweep_combo.hide()
                fe.current_combo.hide()
                fe.position_combo.hide()
                fe.absolute_value_check.hide()
                fe.label.hide()
                fe.label_2.hide()
                fe.label_3.hide()
                fe.label_4.hide()
                fe.label_5.hide()
                fe.label_6.hide()
                fe.label_7.hide()
                fe.label_8.hide()
            self.w.fill_between_widget.show()
        else:
            self.w.fill_between_widget.hide()
            for fe in self.file_entries:
                fe.duplicate_button.show()
                fe.y_scale_combo.show()
                fe.x_scale_combo.show()
                fe.vd_region_combo.show()
                fe.vg_format_combo.show()
                fe.colormap_combo.show()
                fe.legend_check.show()
                fe.sweep_combo.show()
                fe.current_combo.show()
                fe.position_combo.show()
                fe.absolute_value_check.show()
                fe.label.show()
                fe.label_2.show()
                fe.label_3.show()
                fe.label_4.show()
                fe.label_5.show()
                fe.label_6.show()
                fe.label_7.show()
                fe.label_8.show()

        if self.w.plot_mode_combo.currentText() == "One Figure per File":
            self.w.unify_y_lims_check.show()
        else:
            self.w.unify_y_lims_check.hide()

    def plot(self):

        layout = self.w.plotting_widget.layout()
        
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        if self.w.plot_mode_combo.currentText() == "One Figure per File":
    
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
            """self.rows = 1
            self.cols = self.n"""
                
            fig = Figure()
            fig.subplots_adjust(hspace=0.5, wspace=0.5)
            
            canvas = FigureCanvas(fig)
            
            if self.w.saved_format_check.isChecked():
                canvas.setFixedSize((6 * self.cols + (self.cols - 1) * 3)*300, (4 * self.rows + (self.rows - 1) * 2)*300)
                layout.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignHCenter)
            else:
                layout.addWidget(canvas)
            
            y_limits = []
            
            for file_entry in self.checked_entries:

                position = int(file_entry.position_combo.currentText())
                ax = fig.add_subplot(self.rows, self.cols, position)
                
                filepath = file_entry.filepath
                legend = file_entry.legend_check.isChecked()
                vg_format = file_entry.vg_format_combo.currentText()
                colormap = file_entry.colormap_combo.currentText()
                sweep = file_entry.sweep_combo.currentText()
                x_scale = file_entry.x_scale_combo.currentText()
                y_scale = file_entry.y_scale_combo.currentText()
                current = file_entry.current_combo.currentText()
                vd_region = file_entry.vd_region_combo.currentText()
                absolute_value = file_entry.absolute_value_check.isChecked()
                fs = float(self.w.font_size_spin.value())
                lw = float(self.w.line_width_spin.value())
                ms = float(self.w.marker_size_spin.value())
                
                y_min, y_max = plot_idvd.plot(ax, legend, colormap, filepath, sweep, x_scale, y_scale,
                                 current, vg_format, vd_region, absolute_value, fs, lw, ms)
                
                y_limits.append((y_min, y_max))
                
                
            
            if self.w.unify_y_lims_check.isChecked():
                y_mins = []
                y_maxs = []
                for i in y_limits:
                    y_mins.append(i[0])
                    y_maxs.append(i[1])
                    
                global_min = min(y_mins)
                global_max = max(y_maxs)
                
                for ax in fig.axes:
                    ax.set_ylim(global_min, global_max)  

        elif self.w.plot_mode_combo.currentText() == "Mean":
            fig = Figure()
            canvas = FigureCanvas(fig)
            if self.w.saved_format_check.isChecked():
                canvas.setFixedSize(6*300, 4*300)
                layout.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignHCenter)
            else:
                layout.addWidget(canvas)
            
            ax = fig.add_subplot(111)
            
            filepaths = []
            for i in self.checked_entries:
                filepaths.append(i.filepath)
                  
            filepaths = filepaths
            colormap = self.w.colormap_combo_fbw.currentText()
            legend = True
            sweep = self.w.sweep_combo_fbw.currentText()
            y_scale = self.w.y_scale_combo_fbw.currentText()
            absolute_value = self.w.absolute_value_check_fbw.isChecked()
            vg_format = self.w.vg_format_combo_fbw.currentText()
            fs = float(self.w.font_size_spin.value())
            lw = float(self.w.line_width_spin.value())
            ms = float(self.w.marker_size_spin.value())
        
            plot_idvd.mean(ax, filepaths, sweep, vg_format, colormap, y_scale, fs, lw, ms, legend, absolute_value)
                    
        else: # one figure
            
            fig = Figure()
            canvas = FigureCanvas(fig)
            
            if self.w.saved_format_check.isChecked():
                canvas.setFixedSize(6*300, 4*300)
                layout.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignHCenter)
            else:
                layout.addWidget(canvas)
            
            ax = fig.add_subplot(111)
            
            y_limits = []
            
            for ix, file_entry in enumerate(self.checked_entries):
                  
                filepath = file_entry.filepath
                legend = file_entry.legend_check.isChecked()
                vg_format = file_entry.vg_format_combo.currentText()
                colormap = file_entry.colormap_combo.currentText()
                sweep = file_entry.sweep_combo.currentText()
                x_scale = file_entry.x_scale_combo.currentText()
                y_scale = file_entry.y_scale_combo.currentText()
                current = file_entry.current_combo.currentText()
                vd_region = file_entry.vd_region_combo.currentText()
                absolute_value = file_entry.absolute_value_check.isChecked()
                fs = float(self.w.font_size_spin.value())
                lw = float(self.w.line_width_spin.value())
                ms = float(self.w.marker_size_spin.value())
            
                y_min, y_max = plot_idvd.plot(ax, legend, colormap, filepath, sweep, x_scale, y_scale,
                                 current, vg_format, vd_region, absolute_value, fs, lw, ms)
                
                y_limits.append((y_min, y_max))
                
            y_mins = []
            y_maxs = []
            for i in y_limits:
                y_mins.append(i[0])
                y_maxs.append(i[1])
                
            global_min = min(y_mins)
            global_max = max(y_maxs)

            ax.set_ylim(global_min, global_max)
                
        toolbar_layout = self.w.toolbar_widget.layout()
        
        while toolbar_layout.count():
            item = toolbar_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                
        toolbar_layout.addWidget(CustomToolbar(canvas, self.w), alignment=Qt.AlignmentFlag.AlignHCenter)
        
        if not self.w.saved_format_check.isChecked():
            ax.figure.set_constrained_layout(True)
        
        canvas.draw()
        
        self.w.save_plot_button.setEnabled(True)

    def save_plot(self):
        base, _ = QFileDialog.getSaveFileName(self.w, "Save Plot", "", "Images (*.png *.svg)")
        if not base:
            return
        layout = self.w.plotting_widget.layout()
        canvas = None
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                canvas = widget
                break
        if canvas:
            fig = canvas.figure
            root, _ = os.path.splitext(base)
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


