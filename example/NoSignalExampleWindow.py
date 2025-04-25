# NoSignalExampleWindow.py

import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QGroupBox, QFormLayout,
    QSizePolicy, QColorDialog, QScrollArea, QMessageBox,
    QCheckBox, QFrame # Added QFrame
)
from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt, QTimer

# --- Try importing the widget ---
# This now imports from the package structure.
# For this to work during development, install the package in editable mode:
# pip install -e .
try:
    # Import directly from the package name defined in pyproject.toml
    from pyqt_no_signal_widget import NoSignalWidget
except ImportError as e:
    # More specific error message
    QMessageBox.critical(None, "Import Error",
                         f"Could not import NoSignalWidget from 'pyqt_no_signal_widget'.\n\n"
                         f"Error: {e}\n\n"
                         f"Make sure you have installed the package, ideally in editable mode for development:\n"
                         f"cd /path/to/your/project/root\n"
                         f"pip install -e ."
                         )
    sys.exit(1)
except Exception as e:
    # Catch other potential errors during import
    QMessageBox.critical(None, "Import Error", f"An unexpected error occurred during import: {e}")
    sys.exit(1)

class NoSignalExampleWindow(QWidget):
    """
    An example application window demonstrating the features
    of the NoSignalWidget.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Try to get defaults directly from the imported class
        try:
            self._current_ui_colors = NoSignalWidget.DEFAULT_COLORS.copy()
        except AttributeError:
            # Fallback if DEFAULT_COLORS isn't accessible for some reason
            print("Warning: Could not access NoSignalWidget.DEFAULT_COLORS. Using hardcoded fallback.")
            self._current_ui_colors = {
                "--yellow":       "rgba(245, 240, 69, 1)",
                "--light-blue":   "rgba(39, 239, 244, 1)",
                "--green":        "rgba(35, 233, 59, 1)",
                "--purple":       "rgba(240, 80, 241, 1)",
                "--red":          "rgba(235, 41, 32, 1)",
                "--blue":         "rgba(14, 67, 240, 1)",
                "--dark-purple":  "rgba(74, 31, 135, 1)",
                "--white":        "rgba(255, 255, 255, 1)",
                "--black":        "rgba(0, 0, 0, 1)",
                "--navy":         "rgba(14, 79, 107, 1)",
                "--gray":         "rgba(52, 52, 52, 1)",
                "--text-color":   "rgba(255, 255, 255, 1)",
            }
        self._current_ui_text = "PyQt6 No Signal"
        self._current_ui_start_active = True # Default for UI checkbox

        self._init_ui()
        self._connect_widget_signals()

        # Create the initial widget instance *after* UI is set up
        self._create_widget_instance()

    def _init_ui(self):
        self.setWindowTitle("No Signal Widget - Comprehensive Example")
        self.setGeometry(100, 100, 1150, 750) # Adjusted size

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)

        # --- Left Side: Placeholder for NoSignalWidget ---
        self.widget_container = QFrame() # Use a frame to easily replace content
        self.widget_container.setFrameShape(QFrame.Shape.StyledPanel)
        self.widget_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.widget_container_layout = QVBoxLayout(self.widget_container)
        self.widget_container_layout.setContentsMargins(0,0,0,0)
        self.no_signal_widget = None # Will be created later
        main_layout.addWidget(self.widget_container, stretch=2)

        # --- Right Side: Controls ---
        controls_container = QWidget()
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setContentsMargins(5, 5, 5, 5)
        controls_layout.setSpacing(10)

        # -- Instance Control --
        instance_group = QGroupBox("Widget Instance")
        instance_layout = QVBoxLayout()
        self.start_active_checkbox = QCheckBox("Create Widget Initially Active")
        self.start_active_checkbox.setChecked(self._current_ui_start_active)
        self.start_active_checkbox.toggled.connect(self._update_ui_start_active)
        self.recreate_widget_btn = QPushButton("Recreate Widget Instance")
        self.recreate_widget_btn.setToolTip("Creates a new widget instance with current settings")
        self.recreate_widget_btn.clicked.connect(self._create_widget_instance)
        instance_layout.addWidget(self.start_active_checkbox)
        instance_layout.addWidget(self.recreate_widget_btn)
        instance_group.setLayout(instance_layout)
        controls_layout.addWidget(instance_group)

        # -- Text Control --
        text_group = QGroupBox("Text Control")
        text_layout = QHBoxLayout()
        self.text_input = QLineEdit(self._current_ui_text)
        self.text_apply_btn = QPushButton("Apply Text")
        self.text_apply_btn.clicked.connect(self._apply_text)
        text_layout.addWidget(self.text_input)
        text_layout.addWidget(self.text_apply_btn)
        text_group.setLayout(text_layout)
        controls_layout.addWidget(text_group)

        # -- Animation Control --
        anim_group = QGroupBox("Animation Control")
        anim_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start / Fade In")
        self.stop_btn = QPushButton("Stop / Fade Out")
        self.start_btn.clicked.connect(self._start_widget)
        self.stop_btn.clicked.connect(self._stop_widget)
        anim_layout.addWidget(self.start_btn)
        anim_layout.addWidget(self.stop_btn)
        anim_group.setLayout(anim_layout)
        controls_layout.addWidget(anim_group)

        # -- Color Control --
        color_group = QGroupBox("Color Control (All Variables)")
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        color_widget_internal = QWidget()
        internal_layout_container = QVBoxLayout(color_widget_internal) # Main layout for scroll content
        internal_layout_container.setContentsMargins(5, 5, 5, 5)

        color_form_layout = QFormLayout() # Form for the colors
        color_form_layout.setContentsMargins(10, 10, 10, 10)
        color_form_layout.setSpacing(8)
        color_form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows) # Better wrapping

        self.color_inputs = {}
        self.color_buttons = {}
        self.color_previews = {}
        self.predefined_buttons = {}

        # Try to get defaults directly from the imported class for UI generation
        try:
            default_widget_colors = NoSignalWidget.DEFAULT_COLORS
        except AttributeError:
             # Use the already fetched/fallback colors
             default_widget_colors = self._current_ui_colors
             print("Warning: Using fallback default colors for UI generation.")

        # Dynamically create rows for ALL default colors
        sorted_color_keys = sorted(default_widget_colors.keys())

        for variable_name in sorted_color_keys:
            container = QWidget()
            row_layout = QHBoxLayout(container)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(5)

            preview_label = QLabel()
            preview_label.setFixedSize(20, 20)
            preview_label.setAutoFillBackground(True)
            preview_label.setFrameStyle(QLabel.Shape.Box | QLabel.Shadow.Sunken)
            self.color_previews[variable_name] = preview_label
            self.update_color_preview(variable_name, default_widget_colors.get(variable_name, "#000000"))

            line_edit = QLineEdit(default_widget_colors.get(variable_name, ""))
            line_edit.setToolTip("Current CSS color value. Use '...' button or type a predefined name/CSS value.")
            line_edit.editingFinished.connect(lambda vn=variable_name: self._color_text_edited(vn)) # Update on edit finish
            self.color_inputs[variable_name] = line_edit

            # Button for Color Dialog
            button_dialog = QPushButton("...")
            button_dialog.setFixedWidth(30)
            button_dialog.setToolTip("Open Color Picker")
            button_dialog.clicked.connect(lambda checked=False, vn=variable_name: self.select_color_dialog(vn))
            self.color_buttons[variable_name] = button_dialog

            # Button for Predefined Colors (Optional, could be a dropdown later)
            button_predefined = QPushButton("P")
            button_predefined.setFixedWidth(30)
            button_predefined.setToolTip("Cycle Predefined Colors (Example)")
            # Simple cycle for demo - replace with dropdown for many colors
            button_predefined.clicked.connect(lambda checked=False, vn=variable_name: self._cycle_predefined_color(vn))
            self.predefined_buttons[variable_name] = button_predefined


            row_layout.addWidget(preview_label)
            row_layout.addWidget(line_edit)
            row_layout.addWidget(button_dialog)
            # row_layout.addWidget(button_predefined) # Uncomment to add predefined cycle button

            label_widget = QLabel(f"{variable_name}:")
            label_widget.setFont(QFont("Arial", 9)) # Smaller font for labels
            label_widget.setWordWrap(True)
            color_form_layout.addRow(label_widget, container)

        # Add the form layout to the container
        internal_layout_container.addLayout(color_form_layout)

        # Add the "Apply All" button
        self.color_apply_btn = QPushButton("Apply All Color Changes to Widget")
        self.color_apply_btn.clicked.connect(self._apply_colors)
        apply_button_layout = QHBoxLayout()
        apply_button_layout.addStretch(1)
        apply_button_layout.addWidget(self.color_apply_btn)
        apply_button_layout.addStretch(1)
        internal_layout_container.addLayout(apply_button_layout) # Add below form

        scroll_area.setWidget(color_widget_internal)
        color_group_layout = QVBoxLayout()
        color_group_layout.addWidget(scroll_area)
        color_group.setLayout(color_group_layout)
        controls_layout.addWidget(color_group)

        # -- Status Label --
        self.status_label = QLabel("Status: Initializing...")
        self.status_label.setWordWrap(True)
        controls_layout.addWidget(self.status_label)
        controls_layout.addStretch(1) # Push controls up

        controls_container.setLayout(controls_layout)
        controls_container.setFixedWidth(450) # Adjusted width

        main_layout.addWidget(controls_container)
        self.setLayout(main_layout)

    def _update_ui_start_active(self, checked):
        """Stores the state of the 'start active' checkbox."""
        self._current_ui_start_active = checked
        self.status_label.setText("Status: 'Start Active' set to {}. Recreate instance to apply.".format(checked))


    def _create_widget_instance(self):
        """Removes the old widget (if any) and creates a new one."""
        self.status_label.setText("Status: Creating widget instance...")
        QApplication.processEvents() # Update UI

        # Clear old widget
        if self.no_signal_widget:
            self.no_signal_widget.loadFinished.disconnect()
            self.no_signal_widget.loadFailed.disconnect()
            self.widget_container_layout.removeWidget(self.no_signal_widget)
            self.no_signal_widget.deleteLater() # Important for cleanup
            self.no_signal_widget = None

        # Create new widget with current UI settings
        try:
            import traceback # Import traceback module
            print("--- Attempting to create NoSignalWidget ---")
            print(f"Initial Text: {self._current_ui_text}")
            # print(f"Initial Colors: {self._current_ui_colors}") # Keep commented out for now
            print(f"Start Active: {self._current_ui_start_active}")

            self.no_signal_widget = NoSignalWidget(
                initial_text=self._current_ui_text,
                initial_colors=self._current_ui_colors, # TEMP: Comment out to test creation without initial colors -> RE-ENABLED
                start_active=self._current_ui_start_active,
                parent=self.widget_container # Set parent
            )
            self.widget_container_layout.addWidget(self.no_signal_widget)
            self._connect_widget_signals()
            self.status_label.setText(f"Status: New widget created (Active: {self._current_ui_start_active}). Loading...")
            print("--- NoSignalWidget created successfully ---")
        except Exception as e:
            # Print the full traceback
            tb_str = traceback.format_exc()
            print(f"!!! Error creating NoSignalWidget:\n{tb_str}")
            self.status_label.setText(f"Status: Error creating widget: {e}")
            # Show the error type and message in the dialog
            QMessageBox.critical(self, "Widget Creation Error", f"Failed to create NoSignalWidget:\n\n{type(e).__name__}: {e}\n\nCheck console for details.")


    def _connect_widget_signals(self):
        """Connects signals from the current widget instance."""
        if self.no_signal_widget:
            self.no_signal_widget.loadFinished.connect(self._on_widget_load_finished)
            self.no_signal_widget.loadFailed.connect(self._on_widget_load_failed)

    def _on_widget_load_finished(self):
        """Handles successful load of the widget's content."""
        self.status_label.setText(f"Status: Widget content loaded (Active: {self.no_signal_widget._is_active}). Ready.")
        print("ExampleApp: Widget Load Finished signal received.")

    def _on_widget_load_failed(self):
        """Handles failure to load the widget's content."""
        self.status_label.setText("Status: Widget content FAILED to load.")
        QMessageBox.warning(self, "Load Error", "The NoSignalWidget's internal web content failed to load.")
        print("ExampleApp: Widget Load Failed signal received.")

    def _apply_text(self):
        """Applies text from input field to the widget."""
        if self.no_signal_widget:
            self._current_ui_text = self.text_input.text()
            self.no_signal_widget.setText(self._current_ui_text)
            self.status_label.setText(f"Status: Applied text: '{self._current_ui_text[:20]}...'")
        else:
            self.status_label.setText("Status: No widget instance to apply text to.")

    def _start_widget(self):
        """Calls the widget's start method."""
        if self.no_signal_widget:
            self.no_signal_widget.start()
            self.status_label.setText("Status: Start command sent.")
        else:
            self.status_label.setText("Status: No widget instance to start.")

    def _stop_widget(self):
        """Calls the widget's stop method."""
        if self.no_signal_widget:
            self.no_signal_widget.stop()
            self.status_label.setText("Status: Stop command sent.")
        else:
            self.status_label.setText("Status: No widget instance to stop.")

    def _color_text_edited(self, variable_name):
        """Called when a color LineEdit is edited and loses focus or Enter is pressed."""
        if variable_name in self.color_inputs:
            new_value = self.color_inputs[variable_name].text().strip()
            # Basic validation: check if it's a known predefined name or looks like CSS
            resolved_value = new_value
            if new_value in NoSignalWidget.PREDEFINED_COLORS:
                resolved_value = NoSignalWidget.PREDEFINED_COLORS[new_value]
                print(f"Resolved predefined name '{new_value}' to '{resolved_value}'")
            elif not (any(c in new_value for c in ['(', '#']) or new_value in ['transparent', 'white', 'black', 'red']): # Very basic CSS check
                 # If it doesn't look like CSS and isn't predefined, maybe warn or revert?
                 # For now, we accept it but update the preview based on the raw input
                 print(f"Warning: Input '{new_value}' might not be a valid CSS color or predefined name.")
                 pass # Allow user to type anything, apply button does the real work

            # Update internal UI state and preview immediately
            self._current_ui_colors[variable_name] = new_value # Store the *raw* input for setColors
            self.update_color_preview(variable_name, resolved_value) # Update preview based on resolved/raw value
            self.status_label.setText(f"Status: UI color {variable_name} changed. Press 'Apply All' to update widget.")


    def select_color_dialog(self, variable_name):
        """Opens a QColorDialog to select a color."""
        current_color_str = self._current_ui_colors.get(variable_name, "#FFFFFF")
        try:
            # Attempt to parse rgba/hex for initial dialog color
            if current_color_str.startswith("rgba"):
                parts = current_color_str.replace('rgba(', '').replace(')', '').split(',')
                if len(parts) == 4:
                    r, g, b = [int(p.strip()) for p in parts[:3]]
                    a = int(float(parts[3].strip()) * 255)
                    initial_color = QColor(r, g, b, a)
                else: initial_color = QColor(current_color_str)
            else: initial_color = QColor(current_color_str)
        except ValueError: initial_color = QColor("#FFFFFF")

        color = QColorDialog.getColor(initial_color, self, f"Select Color for {variable_name}",
                                      options=QColorDialog.ColorDialogOption.ShowAlphaChannel)

        if color.isValid():
            rgba_string = f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alphaF():.2f})"
            # Update the UI immediately
            self.color_inputs[variable_name].setText(rgba_string)
            self.update_color_preview(variable_name, rgba_string)
            self._current_ui_colors[variable_name] = rgba_string # Store the CSS value
            self.status_label.setText(f"Status: UI color {variable_name} changed. Press 'Apply All' to update widget.")

    def _cycle_predefined_color(self, variable_name):
         """Cycles through predefined colors (simple demo)."""
         # Try to get predefined colors from the class
         try:
             predefined_colors = NoSignalWidget.PREDEFINED_COLORS
         except AttributeError:
             print("Warning: Could not access NoSignalWidget.PREDEFINED_COLORS for cycling.")
             self.status_label.setText(f"Status: Cannot cycle predefined colors for {variable_name}.")
             return

         keys = list(predefined_colors.keys())
         if not keys:
            self.status_label.setText(f"Status: No predefined colors found for {variable_name}.")
            return # Nothing to cycle

         current_value_or_name = self._current_ui_colors.get(variable_name)
         current_name = None

         # Check if the current UI value is a predefined name
         if current_value_or_name in predefined_colors:
            current_name = current_value_or_name
         else:
            # Check if the current UI value is a predefined *value*
            for name, value in predefined_colors.items():
                if value == current_value_or_name:
                    current_name = name
                    break

         try:
             current_index = keys.index(current_name) if current_name in keys else -1
             next_index = (current_index + 1) % len(keys)
             next_name = keys[next_index]
         except ValueError:
             next_name = keys[0] # Default to first if not found

         next_value = predefined_colors[next_name]
         self.color_inputs[variable_name].setText(next_name) # Show the name in input
         self.update_color_preview(variable_name, next_value) # Update preview with actual value
         self._current_ui_colors[variable_name] = next_name # Store the name for setColors
         self.status_label.setText(f"Status: UI color {variable_name} changed. Press 'Apply All' to update widget.")


    def update_color_preview(self, variable_name, color_string_or_name):
        """Updates the background of the preview QLabel."""
        if variable_name in self.color_previews:
            label = self.color_previews[variable_name]
            palette = label.palette()
            try:
                # Try to resolve predefined name first for preview
                resolved_color_string = NoSignalWidget.PREDEFINED_COLORS.get(color_string_or_name, color_string_or_name)

                if resolved_color_string.startswith("rgba"):
                    parts = resolved_color_string.replace('rgba(', '').replace(')', '').split(',')
                    if len(parts) == 4:
                        r, g, b = [int(p.strip()) for p in parts[:3]]
                        a = int(float(parts[3].strip()) * 255)
                        qcolor = QColor(r, g, b, a)
                    else: qcolor = QColor(resolved_color_string)
                else: qcolor = QColor(resolved_color_string)

                if qcolor.isValid():
                    palette.setColor(QPalette.ColorRole.Window, qcolor)
                else: palette.setColor(QPalette.ColorRole.Window, QColor("black")) # Invalid color preview
            except Exception: # Catch broader errors during parsing/conversion
                 palette.setColor(QPalette.ColorRole.Window, QColor("red")) # Error preview
            label.setPalette(palette)

    def _apply_colors(self):
        """Applies all colors currently set in the UI controls to the widget."""
        if self.no_signal_widget:
            # Update _current_ui_colors from all input fields just before applying
            for vn, input_field in self.color_inputs.items():
                self._current_ui_colors[vn] = input_field.text().strip()

            print("ExampleApp: Applying colors to widget:", self._current_ui_colors)
            # Pass the dictionary containing names or CSS strings to the widget
            self.no_signal_widget.setColors(self._current_ui_colors)
            self.status_label.setText("Status: Applied all UI color changes to widget.")
        else:
            self.status_label.setText("Status: No widget instance to apply colors to.")

# --- Application Entry Point ---
if __name__ == "__main__":
    # Enable High DPI scaling if available
    try:
        if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    except Exception as e:
        print(f"Could not set High DPI attributes: {e}")

    app = QApplication(sys.argv)
    example_window = NoSignalExampleWindow()
    example_window.show()
    sys.exit(app.exec())