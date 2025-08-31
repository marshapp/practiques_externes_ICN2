from PyQt6.QtWidgets import QFileDialog, QWidget
from PyQt6.QtCore import Qt
from ui.file_entry_widget_2 import Ui_Form
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import logic.plot_idvg as plot_idvg
import os

class FileEntryWidget_2(QWidget, Ui_Form):
    def __init__(self, filepath):
        super().__init__()
        self.setupUi(self)
        self.filepath_2 = filepath
        filename = os.path.basename(filepath)
        self.filename_check.setText(filename)
        self.filename_check.setChecked(True)


class Tab2Handler:
    def __init__(self, main_window):
        self.w = main_window
        self.file_entries = []
        self.w.plot_button_2.setEnabled(False)
        self.w.save_plot_button_2.setEnabled(False)
        self.w.select_files_button_2.clicked.connect(self.select_files)
        self.w.plot_button_2.clicked.connect(self.plot)
        self.w.save_plot_button_2.clicked.connect(self.save_plot)
        self.w.plot_mode_combo_2.currentTextChanged.connect(self.plot_mode_change)
        self.w.fill_between_widget_2.hide()
        self.w.y_scale_combo_fbw.currentTextChanged.connect(self.y_scale_change_fbw)
        self.w.unify_y_lims_check_2.setChecked(True)
    

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
            self.w.plot_button_2.setEnabled(False)
        else:
            self.w.plot_button_2.setEnabled(True)        

    def select_files(self):
        filepaths, _ = QFileDialog.getOpenFileNames(self.w, "Select Data Files", "", "Excel Files (*.xlsx)")
        for filepath in filepaths:
            self.add_file_entry(filepath)
        self.w.plot_button_2.setEnabled(True)

    def add_file_entry(self, filepath):
        file_entry = FileEntryWidget_2(filepath)
        self.file_entries.append(file_entry)
        self.plot_mode_change()
        self.w.file_entries_widget_2.layout().addWidget(file_entry)
        file_entry.remove_button.clicked.connect(lambda: self.remove_file_entry(file_entry))
        file_entry.duplicate_button.clicked.connect(lambda: self.add_file_entry(file_entry.filepath_2))
        file_entry.y_scale_combo.currentTextChanged.connect(lambda text: self.y_scale_change(file_entry, text)) 
        file_entry.current_combo.currentTextChanged.connect(lambda text: self.current_change(file_entry, text))
        file_entry.linear_regression_check.toggled.connect(lambda checked: self.linear_regression_change(file_entry, checked))
        file_entry.filename_check.clicked.connect(self.update_positions)
        self.update_positions()
        file_entry.legend_check.setChecked(True)

    def remove_file_entry(self, file_entry):
        self.w.file_entries_widget_2.layout().removeWidget(file_entry)
        file_entry.deleteLater()
        self.file_entries.remove(file_entry)
        self.update_positions()

    def y_scale_change(self, file_entry, text):
        if text == "log":
            file_entry.absolute_value_check.setChecked(True)
            file_entry.absolute_value_check.setEnabled(False)
        elif text == "linear" and file_entry.linear_regression_check.isChecked() == False:
            file_entry.absolute_value_check.setEnabled(True)
        
        
    
    def y_scale_change_fbw(self, text):
        if text == "log":
            self.w.absolute_value_check_fbw_2.setChecked(True)
            self.w.absolute_value_check_fbw_2.setEnabled(False)
        else:
            self.w.absolute_value_check_fbw_2.setEnabled(True)

    def linear_regression_change(self, file_entry, checked):
        index = file_entry.sweep_combo.findText("hysteresis")
        if checked == True:
            file_entry.absolute_value_check.setChecked(True)
            file_entry.absolute_value_check.setEnabled(False)
            if file_entry.sweep_combo.currentText() == "hysteresis":
                file_entry.sweep_combo.setCurrentText("forward")
            file_entry.sweep_combo.model().item(index).setEnabled(False)
        elif checked == False:
            file_entry.sweep_combo.model().item(index).setEnabled(True)
            if file_entry.y_scale_combo.currentText() == "linear":
                file_entry.absolute_value_check.setEnabled(True)
        
    def current_change(self, file_entry, text):
        if text == "Igs":
            file_entry.smoothing_check.setChecked(False)
            file_entry.smoothing_check.setEnabled(False)
            file_entry.linear_regression_check.setChecked(False)
            file_entry.linear_regression_check.setEnabled(False)
        else:
            file_entry.smoothing_check.setEnabled(True)
            file_entry.linear_regression_check.setEnabled(True)


    def plot_mode_change(self):
        if self.w.plot_mode_combo_2.currentText() == "Mean":
            for fe in self.file_entries:
                fe.duplicate_button.hide()
                fe.y_scale_combo.hide()
                fe.colormap_combo.hide()
                fe.sweep_combo.hide()
                fe.current_combo.hide()
                fe.legend_check.hide()
                fe.smoothing_check.hide()
                fe.absolute_value_check.hide()
                fe.normalized_check.hide()
                fe.position_combo.hide()
                fe.linear_regression_check.hide()
                fe.label.hide()
                fe.label_2.hide()
                fe.label_4.hide()
                fe.label_6.hide()
                fe.label_8.hide()
                
            self.w.fill_between_widget_2.show()
        else:
            self.w.fill_between_widget_2.hide()
            for fe in self.file_entries:
                fe.duplicate_button.show()
                fe.y_scale_combo.show()
                fe.colormap_combo.show()
                fe.sweep_combo.show()
                fe.current_combo.show()
                fe.smoothing_check.show()
                fe.legend_check.show()
                fe.position_combo.show()
                fe.absolute_value_check.show()
                fe.normalized_check.show()
                fe.linear_regression_check.show()
                fe.label.show()
                fe.label_2.show()
                fe.label_4.show()
                fe.label_6.show()
                fe.label_8.show()

        if self.w.plot_mode_combo_2.currentText() == "One Figure per File":
            self.w.unify_y_lims_check_2.show()
        else:
            self.w.unify_y_lims_check_2.hide()
    
    def plot(self):
                
        layout = self.w.plotting_widget_2.layout()
        
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        if self.w.plot_mode_combo_2.currentText() == "One Figure per File":
    
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
            
            if self.w.saved_format_check_2.isChecked():
                canvas.setFixedSize((6 * self.cols + (self.cols - 1) * 3)*300, (4 * self.rows + (self.rows - 1) * 2)*300)
                layout.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignHCenter)
            else:
                layout.addWidget(canvas)
            
            y_limits = []

            for file_entry in self.checked_entries:
                
                position = int(file_entry.position_combo.currentText())
                ax = fig.add_subplot(self.rows, self.cols, position)
                
                filepath = file_entry.filepath_2
                legend = True
                colormap = file_entry.colormap_combo.currentText()
                s = file_entry.sweep_combo.currentText()
                ysc = file_entry.y_scale_combo.currentText()
                Igs_plot = file_entry.current_combo.currentText()
                nrm = file_entry.normalized_check.isChecked()
                linreg = file_entry.linear_regression_check.isChecked()
                ab = file_entry.absolute_value_check.isChecked()
                fs = float(self.w.font_size_spin_2.value())
                lw = float(self.w.line_width_spin_2.value())
                ms = float(self.w.marker_size_spin_2.value())
                smoothing = file_entry.smoothing_check.isChecked()
            
                y_min, y_max = plot_idvg.idvg_plot(ax, filepath, s, ab, ysc, nrm, linreg, Igs_plot, fs, lw, ms,colormap, legend, smoothing)
                
                y_limits.append((y_min, y_max))

            if self.w.unify_y_lims_check_2.isChecked():
                y_mins = []
                y_maxs = []
                for i in y_limits:
                    y_mins.append(i[0])
                    y_maxs.append(i[1])
                    
                global_min = min(y_mins)
                global_max = max(y_maxs)
                
                for ax in fig.axes:
                    ax.set_ylim(global_min, global_max)

        elif self.w.plot_mode_combo_2.currentText() == "Mean":
            fig = Figure()
            canvas = FigureCanvas(fig)
            if self.w.saved_format_check_2.isChecked():
                canvas.setFixedSize(6*300, 4*300)
                layout.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignHCenter)
            else:
                layout.addWidget(canvas)
            
            ax = fig.add_subplot(111)
            
            filepaths = []
            for i in self.checked_entries:
                filepaths.append(i.filepath_2)
                  
            filepaths = filepaths
            colormap = self.w.colormap_combo_fbw_2.currentText()
            s = self.w.sweep_combo_fbw_2.currentText()
            ysc = self.w.y_scale_combo_fbw_2.currentText()
            ab = self.w.absolute_value_check_fbw_2.isChecked()
            fs = float(self.w.font_size_spin_2.value())
            lw = float(self.w.line_width_spin_2.value())
            ms = float(self.w.marker_size_spin_2.value())
        
            plot_idvg.idvg_alldevs_mean_plot(ax, filepaths, s, ab, ysc, fs, lw, ms, colormap)
                    
        else:
            
            fig = Figure()
            canvas = FigureCanvas(fig)
            
            if self.w.saved_format_check_2.isChecked():
                canvas.setFixedSize(6*300, 4*300)
                layout.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignHCenter)
            else:
                layout.addWidget(canvas)
            
            ax = fig.add_subplot(111)
            
            y_limits = []

            
            for ix, file_entry in enumerate(self.checked_entries):
                  
                filepath = file_entry.filepath_2
                legend = file_entry.legend_check.isChecked()
                colormap = file_entry.colormap_combo.currentText()
                s = file_entry.sweep_combo.currentText()
                ysc = file_entry.y_scale_combo.currentText()
                Igs_plot = file_entry.current_combo.currentText()
                nrm = file_entry.normalized_check.isChecked()
                linreg = file_entry.linear_regression_check.isChecked()
                ab = file_entry.absolute_value_check.isChecked()
                fs = float(self.w.font_size_spin_2.value())
                lw = float(self.w.line_width_spin_2.value())
                ms = float(self.w.marker_size_spin_2.value())
                smoothing = file_entry.smoothing_check.isChecked()
            
                y_min, y_max = plot_idvg.idvg_plot(ax, filepath, s, ab, ysc, nrm, linreg, Igs_plot, fs, lw, ms, colormap, legend, smoothing)
                
                y_limits.append((y_min, y_max))
            
            y_mins = []
            y_maxs = []
            for i in y_limits:
                y_mins.append(i[0])
                y_maxs.append(i[1])
                
            global_min = min(y_mins)
            global_max = max(y_maxs)

            ax.set_ylim(global_min, global_max)
        
        toolbar_layout = self.w.toolbar_widget_2.layout()
        
        while toolbar_layout.count():
            item = toolbar_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                
        toolbar_layout.addWidget(CustomToolbar(canvas, self.w), alignment=Qt.AlignmentFlag.AlignHCenter)
        
        if not self.w.saved_format_check_2.isChecked():
            ax.figure.set_constrained_layout(True)
        
        canvas.draw()
        
        self.w.save_plot_button_2.setEnabled(True)

    def save_plot(self):
        base, _ = QFileDialog.getSaveFileName(self.w, "Save Plot", "", "Images (*.png *.svg)")
        if not base:
            return
        layout = self.w.plotting_widget_2.layout()
        canvas = None
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, FigureCanvas):
                canvas = widget
                break
        if canvas:
            fig = canvas.figure
            root, _ = os.path.splitext(base)
            '''if self.w.plot_mode_combo_2.currentText() == "One Figure per File":
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
