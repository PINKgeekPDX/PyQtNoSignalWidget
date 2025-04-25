# PyQt6 No Signal Widget

A customizable PyQt6 widget displaying a retro 'No Signal' TV animation using embedded HTML/CSS/JS within a `QWebEngineView`.

## Features

*   Retro "No Signal" animation with color bars.
*   Floating message box with customizable text, scaling with widget size.
*   Customizable colors for all animation elements (color bars, text) using:
    *   Predefined color names (e.g., `'bright_red'`, `'original_blue'`).
    *   Standard CSS color strings (e.g., `'#FF0000'`, `'rgba(0,255,0,0.5)'`).
*   Start/Stop controls for the animation with fade-to-black/fade-in effects, including a '⛔️' indicator when stopped.
*   Self-contained widget code (`src/pyqt_no_signal_widget/no_signal_widget.py`).
*   Comprehensive example application (`example/NoSignalExampleWindow.py`) for testing and demonstration.
*   Standard Python packaging setup using `pyproject.toml`.

## Project Structure

```
PyQtNoSignalWidget/
├── src/
│   └── pyqt_no_signal_widget/
│       ├── __init__.py             # Exports NoSignalWidget
│       └── no_signal_widget.py     # Widget source code
├── example/
│   └── NoSignalExampleWindow.py  # Example GUI
├── pyproject.toml                # Build system and package definition
├── README.md                     # This file
└── requirements.txt              # Optional: For development dependencies
```

## Installation

**Option 1: From PyPI (Recommended)**

```bash
pip install pyqt-no-signal-widget
```

**Option 2: From Source (for development)**

1.  Clone this repository.
2.  Navigate to the project root directory (the one containing `pyproject.toml`) in your terminal.
3.  Install in editable mode:
    ```bash
    pip install -e .
    ```

## Basic Usage

```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

# Import the widget from the installed package
from pyqt_no_signal_widget import NoSignalWidget

app = QApplication(sys.argv)
window = QMainWindow()
central_widget = QWidget()
layout = QVBoxLayout(central_widget)

# Create the widget
no_signal = NoSignalWidget(
    initial_text="LOADING...",
    initial_colors={'--text-color': 'lime', '--red': 'orange'}, # Use names or CSS values
    start_active=True # Start animation immediately after load
)

layout.addWidget(no_signal)
window.setCentralWidget(central_widget)
window.setWindowTitle("Basic No Signal Widget")
window.setGeometry(200, 200, 600, 400)
window.show()

# Example interaction after widget loads
def on_load():
    print("Widget loaded, stopping in 2s")
    QTimer.singleShot(2000, no_signal.stop)
    QTimer.singleShot(4000, lambda: no_signal.setText("STOPPED!"))
    QTimer.singleShot(6000, no_signal.start)
    QTimer.singleShot(8000, lambda: no_signal.setColors({'--text-color': 'white'}))

no_signal.loadFinished.connect(on_load)

sys.exit(app.exec())
```

## Running the Example Application

1.  Ensure the package is installed (preferably using Option 2: `pip install -e .`).
2.  Run the example script from the project root:
    ```bash
    python example/NoSignalExampleWindow.py
    ```

## Dependencies

*   PyQt6 >= 6.4.0
*   PyQt6-WebEngine >= 6.4.0

## Notes

*   **Rendering Issues:** This widget uses `QWebEngineView`. If you encounter rendering glitches or C++/GPU-related errors in the console (e.g., `shared_image_factory`, `skia_output_surface_impl_on_gpu`), it might be related to graphics drivers or hardware acceleration compatibility. As a workaround, try disabling GPU acceleration by setting the environment variable `QTWEBENGINE_CHROMIUM_FLAGS` to `--disable-gpu` before running your application.
    *   PowerShell: `$env:QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu"`
    *   cmd.exe: `set QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu`
    *   Bash/Zsh: `export QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu"`
*   **Customization:** Explore the `NoSignalWidget` class methods (`setText`, `setColors`, `start`, `stop`) and the `PREDEFINED_COLORS` and `DEFAULT_COLORS` dictionaries within `no_signal_widget.py` for customization options.

## License

*(Specify your chosen license here, e.g., MIT License)*

## Files

*   `PyQTNoSignalAnimation.py`: The source code for the `NoSignalWidget` class.
*   `NoSignalExampleWindow.py`: A comprehensive example application showcasing widget features.
*   `requirements-widget.txt`: Dependencies needed to *use* the widget as a library.
*   `requirements-example.txt`: Dependencies needed to *run* the example application.
*   `pyproject.toml`: Configuration file for building the Python package.
*   `build_package.py`: Helper script to build the installable package (`.whl`, `.tar.gz`).
*   `README.md`: This documentation file.
*   `LICENSE` (Optional): Add your chosen license file (e.g., MIT).

## Widget Usage (`NoSignalWidget`)

### Installation

**Option 1: From Source (using the build script)**

1.  Navigate to the `PyQtNoSignalWidget` directory in your terminal.
2.  Run the build script: `python build_package.py`
3.  Install the generated wheel file: `pip install dist/*.whl`

**Option 2: Directly (if not packaging)**

Ensure `PyQTNoSignalAnimation.py` is in your Python path or the same directory as your application script.

### Basic Example

```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

# Assuming the widget is installed or PyQTNoSignalAnimation.py is accessible
from PyQTNoSignalAnimation import NoSignalWidget

app = QApplication(sys.argv)
window = QMainWindow()
central_widget = QWidget()
layout = QVBoxLayout(central_widget)

# Create the widget
no_signal = NoSignalWidget(
    initial_text="LOADING...",
    initial_colors={'--text-color': 'lime', '--red': 'orange'}, # Use names or CSS values
    start_active=True # Start animation immediately after load
)

layout.addWidget(no_signal)
window.setCentralWidget(central_widget)
window.setWindowTitle("Basic No Signal Widget")
window.setGeometry(200, 200, 600, 400)
window.show()

# Example interaction after widget loads
def on_load():
    print("Widget loaded, stopping in 2s")
    QTimer.singleShot(2000, no_signal.stop)
    QTimer.singleShot(4000, lambda: no_signal.setText("STOPPED!"))
    QTimer.singleShot(6000, no_signal.start)
    QTimer.singleShot(8000, lambda: no_signal.setColors({'--text-color': 'white'}))

no_signal.loadFinished.connect(on_load)

sys.exit(app.exec())