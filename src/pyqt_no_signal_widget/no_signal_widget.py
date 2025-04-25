# PyQTNoSignalAnimation.py -> Renamed to no_signal_widget.py

import sys
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QLabel # Added QLabel
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PyQt6.QtCore import Qt, pyqtSlot, QUrl, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QFont # Added QFont

# Helper class for the fade overlay
class OverlayWidget(QWidget):
    """a simple overlay widget for fade effects."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # make it click-through
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True) # needed for background-color
        self._background_color = QColor(0, 0, 0, 0) # start fully transparent
        self.setStyleSheet("background-color: rgba(0,0,0,0);") # initial stylesheet

    def setBackgroundColor(self, color):
        """sets the background color and updates stylesheet."""
        if self._background_color != color:
            self._background_color = color
            self.setStyleSheet(f"background-color: {color.name(QColor.NameFormat.HexArgb)};")
            self.update() # trigger repaint

    def backgroundColor(self):
        """gets the current background color."""
        return self._background_color

    # define a qproperty for animation (targets the background color)
    color = pyqtProperty(QColor, fget=backgroundColor, fset=setBackgroundColor)

    def paintEvent(self, event):
        """overrides paintevent to ensure background is drawn if needed (though stylesheet usually handles it)."""
        # stylesheet should handle painting, but this can be a fallback
        # if self._background_color.alpha() > 0:
        #     painter = QPainter(self)
        #     painter.fillRect(self.rect(), self._background_color)
        super().paintEvent(event) # allow default painting


class NoSignalWidget(QWidget):
    """
    a custom pyqt6 widget that displays a retro 'no signal' tv animation
    using embedded html/css/js in a qwebengineview. allows customization
    of text and colors (using predefined names or css values), and provides
    start/stop controls with fade effects.

    attributes:
        predefined_colors (dict): maps simple color names to css rgba strings.
        default_colors (dict): maps the widget's internal css variables to their default css color strings.
    """

    # signal emitted when the web content has finished loading successfully
    loadFinished = pyqtSignal()
    # signal emitted if the web content fails to load
    loadFailed = pyqtSignal()

    # --- predefined color names ---
    PREDEFINED_COLORS = {
        "original_yellow":      "rgba(245, 240, 69, 1)",
        "original_light_blue":  "rgba(39, 239, 244, 1)",
        "original_green":       "rgba(35, 233, 59, 1)",
        "original_purple":      "rgba(240, 80, 241, 1)",
        "original_red":         "rgba(235, 41, 32, 1)",
        "original_blue":        "rgba(14, 67, 240, 1)",
        "original_dark_purple": "rgba(74, 31, 135, 1)",
        "original_white":       "rgba(255, 255, 255, 1)",
        "original_black":       "rgba(0, 0, 0, 1)",
        "original_navy":        "rgba(14, 79, 107, 1)",
        "original_gray":        "rgba(52, 52, 52, 1)",
        "white":          "rgba(255, 255, 255, 1)",
        "black":          "rgba(0, 0, 0, 1)",
        "transparent":    "rgba(0, 0, 0, 0)",
        "bright_red":     "rgba(255, 0, 0, 1)",
        "bright_green":   "rgba(0, 255, 0, 1)",
        "bright_blue":    "rgba(0, 0, 255, 1)",
        "bright_yellow":  "rgba(255, 255, 0, 1)",
        "bright_cyan":    "rgba(0, 255, 255, 1)",
        "bright_magenta": "rgba(255, 0, 255, 1)",
        "dark_red":       "rgba(139, 0, 0, 1)",
        "dark_green":     "rgba(0, 100, 0, 1)",
        "dark_blue":      "rgba(0, 0, 139, 1)",
        "orange":         "rgba(255, 165, 0, 1)",
        "purple":         "rgba(128, 0, 128, 1)",
        "pink":           "rgba(255, 192, 203, 1)",
        "brown":          "rgba(165, 42, 42, 1)",
        "gold":           "rgba(255, 215, 0, 1)",
        "silver":         "rgba(192, 192, 192, 1)",
        "gray":           "rgba(128, 128, 128, 1)",
        "light_gray":     "rgba(211, 211, 211, 1)",
        "dark_gray":      "rgba(169, 169, 169, 1)",
        "slate_gray":     "rgba(112, 128, 144, 1)",
        "olive":          "rgba(128, 128, 0, 1)",
        "lime":           "rgba(50, 205, 50, 1)",
        "teal":           "rgba(0, 128, 128, 1)",
        "aqua":           "rgba(0, 255, 255, 1)",
        "fuchsia":        "rgba(255, 0, 255, 1)",
    }

    # --- html/css/js template ---
    HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>No Signal Animation</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        /* reset and basic styles */
        html, body, div, span, applet, object, iframe, h1, h2, h3, h4, h5, h6, p, blockquote, pre, a, abbr, acronym, address, big, cite, code, del, dfn, em, img, ins, kbd, q, s, samp, small, strike, strong, sub, sup, tt, var, b, u, i, center, dl, dt, dd, ol, ul, li, fieldset, form, label, legend, table, caption, tbody, tfoot, thead, tr, th, td, article, aside, canvas, details, embed, figure, figcaption, footer, header, hgroup, menu, nav, output, ruby, section, summary, time, mark, audio, video {{ margin: 0; padding: 0; border: 0; font-size: 100%; font: inherit; vertical-align: baseline; }}
        article, aside, details, figcaption, figure, footer, header, hgroup, menu, nav, section {{ display: block; }}
        body {{ line-height: 1; }}
        ol, ul {{ list-style: none; }}
        blockquote, q {{ quotes: none; }}
        blockquote:before, blockquote:after, q:before, q:after {{ content: ""; content: none; }}
        table {{ border-collapse: collapse; border-spacing: 0; }}

        /* default color variables (must match keys in default_colors) */
        :root {{
            --yellow: rgba(245, 240, 69, 1);
            --light-blue: rgba(39, 239, 244, 1);
            --green: rgba(35, 233, 59, 1);
            --purple: rgba(240, 80, 241, 1);
            --red: rgba(235, 41, 32, 1);
            --blue: rgba(14, 67, 240, 1);
            --dark-purple: rgba(74, 31, 135, 1);
            --white: rgba(255, 255, 255, 1);
            --black: rgba(0, 0, 0, 1);
            --navy: rgba(14, 79, 107, 1);
            --gray: rgba(52, 52, 52, 1);
            --text-color: rgba(255, 255, 255, 1);
        }}

        /* font and box sizing */
        @font-face {{
            font-family: "Michroma";
            src: url("https://assets.codepen.io/1149983/Michroma-Regular.ttf") format("truetype");
            font-weight: normal; font-style: normal; font-display: swap;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        /* main layout */
        body {{ overflow: hidden; background-color: var(--black); }}
        main {{
            display: grid; grid-template-columns: repeat(6, 1fr);
            grid-template-rows: 4fr 1fr 1fr; place-items: center;
            grid-auto-flow: column dense; height: 100vh; width: 100vw;
            position: relative; overflow: hidden;
        }}
        main span {{
            z-index: 1; display: flex; flex-flow: column wrap;
            height: 100%; width: 100%; filter: brightness(0.95);
        }}
        /* color bars */
        main span:nth-child(-n+6) {{ grid-row: 1; }}
        main span:nth-of-type(1) {{ background-color: var(--yellow); }}
        main span:nth-of-type(2) {{ background-color: var(--light-blue); }}
        main span:nth-of-type(3) {{ background-color: var(--green); }}
        main span:nth-of-type(4) {{ background-color: var(--purple); }}
        main span:nth-of-type(5) {{ background-color: var(--red); }}
        main span:nth-of-type(6) {{ background-color: var(--blue); }}
        main span:nth-child(n+7) {{ grid-row: 2; }}
        main span:nth-of-type(7) {{ background-color: var(--blue); }}
        main span:nth-of-type(8) {{ background-color: var(--purple); }}
        main span:nth-of-type(9) {{ background-color: var(--black); }}
        main span:nth-of-type(10) {{ background-color: var(--light-blue); }}
        main span:nth-of-type(11) {{ background-color: var(--black); }}
        main span:nth-of-type(12) {{ background-color: var(--white); }}
        main span:nth-child(n+13) {{ grid-row: 3; }}
        main span:nth-of-type(13) {{ background-color: var(--navy); }}
        main span:nth-of-type(14) {{ background-color: var(--white); }}
        main span:nth-of-type(15) {{ background-color: var(--dark-purple); }}
        main span:nth-of-type(16) {{ background-color: var(--black); }}
        main span:nth-of-type(17) {{ background-color: var(--gray); }}
        main span:nth-of-type(18) {{ background-color: var(--black); }}

        /* floating message box */
        main div.message-box {{
            display: inline-grid; place-items: center; left: 0; top: 0;
            z-index: 2; position: absolute; width: 30vw;
            background: rgba(19, 20, 23, 0.35); box-shadow: 0 8px 32px 0 rgba(19, 20, 23, 0.35);
            backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
            border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.18);
            visibility: hidden; opacity: 0;
            transition: visibility 0s linear 0.3s, opacity 0.3s ease-in-out;
        }}
        main.animation-active div.message-box {{
            animation: moveX 7.05s linear 0s infinite alternate, moveY 7.4s linear 0s infinite alternate;
            visibility: visible; opacity: 1;
            transition: visibility 0s linear 0s, opacity 0.3s ease-in-out;
        }}

        /* message text */
        main h1#messageText {{
            font-family: "Michroma", sans-serif; padding: 3vmin 1vmin;
            font-size: 3.5vmin;
            text-transform: uppercase; color: var(--text-color);
            filter: drop-shadow(5px 5px 8px var(--black)); text-align: center;
            word-wrap: break-word; animation: none;
        }}
        main.animation-active h1#messageText {{ /* optional: add text animation here if desired */ }}

        /* keyframes for movement */
        @keyframes moveX {{ from {{ left: 0; }} to {{ left: calc(100vw - 30vw); }} }}
        @keyframes moveY {{ from {{ top: 0; }} to {{ top: calc(100vh - 10vmin); }} }}
    </style>
</head>
<body>
<main id="mainContainer"> <!-- start without animation-active, controlled by js -->
    <span></span><span></span><span></span><span></span><span></span><span></span>
    <span></span><span></span><span></span><span></span><span></span><span></span>
    <span></span><span></span><span></span><span></span><span></span><span></span>
    <div class="message-box"> <h1 id="messageText">{initial_text}</h1> </div>
</main>
<script>
    const messageElement = document.getElementById('messageText');
    const mainContainer = document.getElementById('mainContainer');
    const rootStyle = document.documentElement.style;

    function updateText(newText) {{
        if (messageElement) messageElement.innerText = newText;
    }}

    function updateColors(colorMap) {{
        console.debug("js updatecolors received:", colorMap);
        if (typeof colorMap === 'object' && colorMap !== null) {{
            for (const [key, value] of Object.entries(colorMap)) {{
                if (key.startsWith('--')) {{ // basic validation
                    rootStyle.setProperty(key, value);
                    // console.debug(`js set ${{key}} to ${{value}}`);
                }}
            }}
        }} else {{ console.error("js invalid colormap:", colorMap); }}
    }}

    function startAnimation() {{
        if (mainContainer) mainContainer.classList.add('animation-active');
        console.debug("js animation started");
    }}

    function stopAnimation() {{
        if (mainContainer) mainContainer.classList.remove('animation-active');
        console.debug("js animation stopped");
    }}

    // initial state is set by python after load
</script>
</body>
</html>
    """

    # --- default colors (must match css :root variables) ---
    DEFAULT_COLORS = {
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

    def __init__(self, initial_text="NO SIGNAL", initial_colors=None, start_active=True, parent=None):
        """
        initializes the nosignalwidget.

        args:
            initial_text (str): the text to display initially.
            initial_colors (dict, optional): a dictionary mapping css variables
                (e.g., '--text-color') to color values (css strings or predefined names).
                defaults to none, using default_colors.
            start_active (bool): if true, the animation starts automatically after loading.
                                 if false, it starts in the 'stopped' (faded black) state.
            parent (qwidget, optional): parent widget. defaults to none.
        """
        super().__init__(parent)

        self._is_page_loaded = False
        self._is_active = start_active # store initial desired state
        self._current_text = initial_text
        self._current_widget_colors = self.DEFAULT_COLORS.copy() # start with defaults

        # process initial_colors *before* loading html if provided
        if initial_colors:
             self.setColors(initial_colors, _update_internal_state_only=True)

        # --- widget setup ---
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Widget)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: transparent;")

        # --- web engine view setup ---
        self.web_view = QWebEngineView(self)
        self.web_page = QWebEnginePage(self)
        self.web_view.setPage(self.web_page)
        self.web_view.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        settings = self.web_page.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, False)
        self.web_page.setBackgroundColor(Qt.GlobalColor.transparent)

        # --- layout ---
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.web_view)
        self.setLayout(self.layout)

        # --- overlay for fade effect ---
        self.overlay = OverlayWidget(self)
        self.overlay.setGeometry(self.rect())
        self.overlay.hide() # initially hidden

        # --- animation for fade ---
        self._fade_animation = QPropertyAnimation(self.overlay, b"color", self)
        self._fade_animation.setDuration(500)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # --- Stop Indicator Label ---
        self._stop_indicator_label = QLabel("⛔️", self)
        self._stop_indicator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(48) # Adjust size as needed
        self._stop_indicator_label.setFont(font)
        self._stop_indicator_label.setStyleSheet("color: lightgray; background-color: transparent;")
        self._stop_indicator_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._stop_indicator_label.hide() # Initially hidden

        # --- load initial content ---
        self._load_html()

        # --- connections ---
        self.web_page.loadFinished.connect(self._on_load_finished)
        # optional: connect console messages for debugging
        # self.web_page.javaScriptConsoleMessage = self._handle_js_console_message

    def _handle_js_console_message(self, level, message, lineNumber, sourceID):
        """(optional) prints javascript console messages to python console."""
        print(f"js console ({sourceid}:{linenumber}): {message}")

    def _load_html(self):
        """generates and loads the html content."""
        # use the text stored in _current_text for initial load
        html_content = self.HTML_TEMPLATE.format(initial_text=self._current_text)
        base_url = QUrl("https://local.nosignal.widget/") # use a dummy local base url
        self.web_view.setHtml(html_content, base_url)
        self._is_page_loaded = False

    def _on_load_finished(self, ok):
        """handles the web page load finished signal."""
        print(f"nosignalwidget: page load finished: {'ok' if ok else 'failed'}")
        self._is_page_loaded = ok
        if ok:
            # apply the resolved initial colors stored in _current_widget_colors
            css_colors_to_apply = self._current_widget_colors
            if css_colors_to_apply:
                 colors_json = json.dumps(css_colors_to_apply)
                 self._run_javascript(f"updateColors({colors_json});")

            # set initial animation state based on _is_active flag
            if self._is_active:
                print("nosignalwidget: starting animation on load.")
                self.start(_immediate=True) # start immediately without fade-in
            else:
                print("nosignalwidget: setting initial state to stopped.")
                self.stop(_immediate=True) # stop immediately without fade-out

            self.loadFinished.emit() # emit success signal
        else:
            print("error: nosignalwidget failed to load html content.")
            self.loadFailed.emit() # emit failure signal

    def _run_javascript(self, script):
        """safely runs javascript, checking if the page is loaded."""
        if self._is_page_loaded:
            self.web_page.runJavaScript(script)
        else:
            # optionally queue or log warning
            print("warning: attempted to run javascript before page finished loading.")

    @pyqtSlot(str)
    def setText(self, text):
        """
        sets the text displayed in the floating message box.

        args:
            text (str): the text to display.
        """
        self._current_text = text
        escaped_text = json.dumps(text)
        self._run_javascript(f"updateText({escaped_text});")

    @pyqtSlot(dict)
    def setColors(self, colors_dict, _update_internal_state_only=False):
        """
        sets the colors used in the animation via css variables.

        expects a dictionary mapping css variable names (e.g., '--text-color')
        to color values. color values can be:
        1. standard css color strings (e.g., 'rgba(255,0,0,1)', '#ff0000', 'red').
        2. predefined simple color name strings (e.g., 'bright_red', 'original_blue')
           which are keys in `nosignalwidget.predefined_colors`.

        args:
            colors_dict (dict): dictionary mapping css variable names to color values/names.
            _update_internal_state_only (bool): internal flag used during init.
        """
        processed_colors_for_js = {}
        updated_any_internal = False

        for key, value in colors_dict.items():
            if not isinstance(key, str) or not key.startswith('--'):
                print(f"warning: invalid color key '{key}'. must be a string starting with '--'. skipping.")
                continue

            css_color_value = None
            if isinstance(value, str):
                if value in self.PREDEFINED_COLORS:
                    css_color_value = self.PREDEFINED_COLORS[value]
                else:
                    css_color_value = value
            else:
                 print(f"warning: color value for key '{key}' is not a string: {value}. skipping.")
                 continue

            if css_color_value is not None:
                 current_internal_value = self._current_widget_colors.get(key)
                 if current_internal_value != css_color_value:
                     self._current_widget_colors[key] = css_color_value
                     updated_any_internal = True
                 processed_colors_for_js[key] = css_color_value

        if not _update_internal_state_only and processed_colors_for_js:
            if self._is_page_loaded:
                colors_json = json.dumps(processed_colors_for_js)
                self._run_javascript(f"updateColors({colors_json});")
            else:
                print("info: setcolors called before load; changes queued.")
        elif updated_any_internal:
             pass # internal state updated (e.g., during init), js will run on load

    @pyqtSlot()
    def start(self, _immediate=False):
        """
        starts or resumes the animation and fades out the black overlay.
        if _immediate is true, starts instantly without fade (used on initial load).
        """
        if not self._is_active or _immediate: # allow immediate start even if already active
            self._is_active = True
            self._run_javascript("startAnimation();")

            # fade out the overlay
            self.overlay.show()
            self.overlay.raise_() # ensure it's on top during animation

            if _immediate:
                self.overlay.setBackgroundColor(QColor(0, 0, 0, 0))
                self.overlay.hide()
            else:
                self._fade_animation.setDirection(QPropertyAnimation.Direction.Backward) # alpha -> 0
                if self._fade_animation.state() == QPropertyAnimation.State.Running:
                    self._fade_animation.stop()
                # start from current color (might be partially faded) or full black
                start_alpha = self.overlay.backgroundColor().alpha()
                self._fade_animation.setStartValue(self.overlay.backgroundColor())
                self._fade_animation.setEndValue(QColor(0, 0, 0, 0))
                self._fade_animation.start()
                # hide overlay after animation finishes if still active
                QTimer.singleShot(self._fade_animation.duration() + 50, # add slight delay
                                  lambda: self.overlay.hide() if self._is_active else None)

            # Hide stop indicator when starting
            self._stop_indicator_label.hide()

    @pyqtSlot()
    def stop(self, _immediate=False):
        """
        stops the animation and fades the widget to black.
        if _immediate is true, stops instantly without fade (used on initial load).
        """
        if self._is_active or _immediate: # allow immediate stop even if already stopped
            self._is_active = False
            self._run_javascript("stopAnimation();")

            # fade in the overlay
            self.overlay.show()
            self.overlay.raise_() # ensure it's on top

            if _immediate:
                 if self._fade_animation.state() == QPropertyAnimation.State.Running:
                     self._fade_animation.stop()
                 self.overlay.setBackgroundColor(QColor(0, 0, 0, 255)) # set immediately
            else:
                self._fade_animation.setDirection(QPropertyAnimation.Direction.Forward) # alpha -> 255
                if self._fade_animation.state() == QPropertyAnimation.State.Running:
                    self._fade_animation.stop()
                # start from current color (might be partially faded) or transparent
                start_alpha = self.overlay.backgroundColor().alpha()
                self._fade_animation.setStartValue(self.overlay.backgroundColor())
                self._fade_animation.setEndValue(QColor(0, 0, 0, 255))
                self._fade_animation.start()

            # Show and raise stop indicator when stopping
            self._update_stop_indicator_geometry()
            self._stop_indicator_label.show()
            self._stop_indicator_label.raise_()

    def _update_stop_indicator_geometry(self):
        """Updates the geometry of the stop indicator label to match the widget."""
        self._stop_indicator_label.setGeometry(self.rect())

    def resizeEvent(self, event):
        """ensure overlay covers the widget on resize."""
        self.overlay.setGeometry(self.rect())
        self._update_stop_indicator_geometry() # Keep indicator centered
        super().resizeEvent(event)

    def showEvent(self, event):
        """ensure overlay state is correct when widget is shown."""
        if not self._is_active:
             # if meant to be stopped, ensure overlay is fully opaque black
             self.overlay.setBackgroundColor(QColor(0, 0, 0, 255))
             self.overlay.show()
             self.overlay.raise_()
             # Also show and raise indicator if stopped
             self._update_stop_indicator_geometry()
             self._stop_indicator_label.show()
             self._stop_indicator_label.raise_()
        else:
             # if meant to be active, ensure overlay is hidden
             self.overlay.hide()
             self._stop_indicator_label.hide()
        super().showEvent(event)

# minimal self-run test (better testing in nosignalexamplewindow.py)
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # test with initial state set to stopped
    widget = NoSignalWidget(initial_text="testing...", start_active=False)
    widget.setGeometry(100, 100, 500, 300)
    widget.show()
    # example: start it after 3 seconds
    QTimer.singleShot(3000, widget.start)
    # example: change text after 5 seconds
    QTimer.singleShot(5000, lambda: widget.setText("text changed!"))
    # example: change colors after 7 seconds using names
    QTimer.singleShot(7000, lambda: widget.setColors({'--text-color': 'lime', '--red': 'orange'}))
    # example: stop after 10 seconds
    QTimer.singleShot(10000, widget.stop)
    sys.exit(app.exec()) 