"""Visible, user-controlled browser intake for bounded Scribble Hub discovery."""

from urllib.parse import urlparse

from PySide6.QtCore import QDateTime, Qt, QUrl, Signal
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from Brain.Team.researcher import Researcher, StoryFinding
from Runtime.Research.scribblehub import ScribbleHubListingParser, latest_harem_url
from Runtime.Research.story_page import decode_story_evidence


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
        self.investigate = QPushButton("Investigate current story page")
        self.investigate.clicked.connect(self._prepare_story_report)
        layout.addWidget(self.investigate)
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

    def _prepare_story_report(self):
        source = self.view.url().toString()
        parsed = urlparse(source)
        if parsed.scheme != "https" or parsed.hostname not in {"scribblehub.com", "www.scribblehub.com"} or "/series/" not in parsed.path:
            self.notice.setText("Navigate visibly to a Scribble Hub story Details page first.")
            return
        self.investigate.setEnabled(False)
        self.notice.setText("The Researcher is reading bounded public story metadata and visible review evidence...")
        script = """(() => JSON.stringify({
          title: (document.querySelector('.fic_title')?.innerText || '').trim(),
          synopsis: (document.querySelector('.wi_fic_desc')?.innerText || '').trim(),
          genres: [...document.querySelectorAll('a.fic_genre')].map(e => e.innerText.trim()).filter(Boolean),
          tags: [...document.querySelectorAll("a[href*='/tag/']")].map(e => e.innerText.trim()).filter(Boolean),
          stats: (document.querySelector('.fic_stats')?.innerText || '').trim(),
          reviews: [...document.querySelectorAll('.w-comments-item')].slice(0, 5).map(e =>
            [...e.querySelectorAll('p')].map(p => p.innerText.trim()).filter(Boolean).join(' ')
          ).filter(Boolean)
        }))()"""
        self.view.page().runJavaScript(script, lambda page: self._story_result(page, source))

    def _story_result(self, page, source: str):
        try:
            evidence = decode_story_evidence(page)
            body = Researcher().report_story_page(evidence, source, QDateTime.currentDateTime().toString(Qt.DateFormat.ISODate))
        except (TypeError, ValueError) as error:
            self.notice.setText(f"The current story page could not be investigated safely: {error}")
            self.investigate.setEnabled(True)
            return
        self.report_ready.emit(f"Story investigation — {evidence.get('title', 'Scribble Hub')}", body)
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
