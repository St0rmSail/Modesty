"""Visible, user-controlled browser intake for bounded Scribble Hub discovery."""

from urllib.parse import urlparse

from PySide6.QtCore import QUrl, Signal
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from Brain.Team.researcher import Researcher, StoryFinding
from Runtime.Research.scribblehub import ScribbleHubListingParser, latest_harem_url


class ScribbleHubPage(QWebEnginePage):
    """Keep top-level navigation on Scribble Hub without bypassing its controls."""

    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        if is_main_frame and url.scheme() in {"http", "https"}:
            host = url.host().casefold()
            return host == "scribblehub.com" or host.endswith(".scribblehub.com")
        return super().acceptNavigationRequest(url, navigation_type, is_main_frame)


class ScribbleHubResearchWindow(QWidget):
    report_ready = Signal(str, str)
    closed = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modesty — Scribble Hub Research")
        self.resize(1100, 760)

        layout = QVBoxLayout(self)
        self.notice = QLabel(
            "This is a visible local browser. Complete any site verification if requested, "
            "then select Prepare Briefing. No account action or story text will be captured."
        )
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)

        self.view = QWebEngineView()
        self.view.setPage(ScribbleHubPage(self.view))
        layout.addWidget(self.view, stretch=1)

        self.prepare = QPushButton("Prepare Briefing from visible listings")
        self.prepare.clicked.connect(self._prepare_report)
        layout.addWidget(self.prepare)
        self.view.setUrl(QUrl(latest_harem_url()))

    def _prepare_report(self):
        self.prepare.setEnabled(False)
        self.notice.setText("The Researcher is reading bounded public listing metadata...")
        self.view.page().toHtml(self._html_result)

    def _html_result(self, html: str):
        try:
            parser = ScribbleHubListingParser(limit=10)
            parser.feed(html)
            findings = tuple(self._validated_finding(finding) for finding in parser.findings)
            body = Researcher().report_latest_harem(findings)
        except (TypeError, ValueError) as error:
            self.notice.setText(f"The visible listing could not be converted safely: {error}")
            self.prepare.setEnabled(True)
            return
        if not findings:
            self.notice.setText(
                "No listing cards were visible. Complete any site verification or wait for the results, then try again."
            )
            self.prepare.setEnabled(True)
            return
        self.report_ready.emit("Latest Harem offerings on Scribble Hub", body)
        self.close()

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    @staticmethod
    def _validated_finding(finding: StoryFinding):
        source = finding.url
        parsed = urlparse(source)
        if parsed.scheme != "https" or parsed.hostname not in {"scribblehub.com", "www.scribblehub.com"}:
            raise ValueError("A listing contained an unexpected source URL.")
        return finding
