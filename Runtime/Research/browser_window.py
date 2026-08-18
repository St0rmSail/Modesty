"""Visible, user-controlled browser intake for bounded Scribble Hub discovery."""

from urllib.parse import urlparse

from PySide6.QtCore import QDateTime, QObject, QRunnable, Qt, QThreadPool, QUrl, Signal
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from Brain.Team.researcher import Researcher, StoryFinding, StoryPageEvidence
from Runtime.Research.scribblehub import ScribbleHubListingParser, latest_harem_url
from Runtime.Research.story_page import decode_story_evidence
from Runtime.Research.youtube import TranscriptUnavailable, YouTubeTranscriptProvider


class TranscriptWorkerSignals(QObject):
    ready = Signal(object)
    failed = Signal(str)


class TranscriptWorker(QRunnable):
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.signals = TranscriptWorkerSignals()

    def run(self):
        try:
            evidence = YouTubeTranscriptProvider().fetch(self.url)
        except TranscriptUnavailable as error:
            self.signals.failed.emit(str(error))
        else:
            self.signals.ready.emit(evidence)


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
        self.comparison_stories: list[StoryPageEvidence] = []

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
        self.listings = QPushButton("Return to latest listings")
        self.listings.clicked.connect(lambda: self.view.setUrl(QUrl(latest_harem_url())))
        layout.addWidget(self.listings)
        self.add_comparison = QPushButton("Add current story to comparison (0/3)")
        self.add_comparison.clicked.connect(self._add_story_to_comparison)
        layout.addWidget(self.add_comparison)
        self.compare = QPushButton("Prepare comparison briefing")
        self.compare.setEnabled(False)
        self.compare.clicked.connect(self._prepare_comparison_report)
        layout.addWidget(self.compare)
        self.youtube_url = QLineEdit()
        self.youtube_url.setPlaceholderText("Public YouTube video URL for mixed-source research")
        layout.addWidget(self.youtube_url)
        self.research_focus = QLineEdit()
        self.research_focus.setPlaceholderText("Research focus, e.g. How does the Dormammu bargain establish the time-loop premise?")
        layout.addWidget(self.research_focus)
        self.youtube = QPushButton("Add YouTube transcript and prepare mixed-source briefing")
        self.youtube.setEnabled(False)
        self.youtube.clicked.connect(self._prepare_mixed_report)
        layout.addWidget(self.youtube)
        self.transcript_worker = None
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
        self._read_story_page(self._story_result)

    def _add_story_to_comparison(self):
        self._read_story_page(self._comparison_story_result)

    def _read_story_page(self, callback):
        source = self.view.url().toString()
        parsed = urlparse(source)
        if parsed.scheme != "https" or parsed.hostname not in {"scribblehub.com", "www.scribblehub.com"} or "/series/" not in parsed.path:
            self.notice.setText("Navigate visibly to a Scribble Hub story Details page first.")
            return
        self.investigate.setEnabled(False)
        self.add_comparison.setEnabled(False)
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
        self.view.page().runJavaScript(script, lambda page: callback(page, source))

    def _story_result(self, page, source: str):
        try:
            evidence = decode_story_evidence(page)
            body = Researcher().report_story_page(evidence, source, QDateTime.currentDateTime().toString(Qt.DateFormat.ISODate))
        except (TypeError, ValueError) as error:
            self.notice.setText(f"The current story page could not be investigated safely: {error}")
            self.investigate.setEnabled(True)
            self.add_comparison.setEnabled(len(self.comparison_stories) < 3)
            return
        self.report_ready.emit(f"Story investigation — {evidence.get('title', 'Scribble Hub')}", body)
        self.close()

    def _comparison_story_result(self, page, source: str):
        try:
            evidence = decode_story_evidence(page)
            story = Researcher().story_page_evidence(evidence, source)
            if any(existing.source_url == story.source_url for existing in self.comparison_stories):
                raise ValueError("That story is already in the comparison set.")
            self.comparison_stories.append(story)
        except (TypeError, ValueError) as error:
            self.notice.setText(f"The current story page could not be added safely: {error}")
        else:
            self.notice.setText(
                f"Added {story.title}. Navigate to another story page and add it, or prepare the comparison."
            )
        self.investigate.setEnabled(True)
        count = len(self.comparison_stories)
        self.add_comparison.setText(f"Add current story to comparison ({count}/3)")
        self.add_comparison.setEnabled(count < 3)
        self.compare.setEnabled(count >= 2)
        self.youtube.setEnabled(count == 1)

    def _prepare_comparison_report(self):
        try:
            body = Researcher().report_story_comparison(
                self.comparison_stories,
                QDateTime.currentDateTime().toString(Qt.DateFormat.ISODate),
            )
        except ValueError as error:
            self.notice.setText(f"The comparison could not be prepared safely: {error}")
            return
        self.report_ready.emit(
            f"Story comparison — {len(self.comparison_stories)} Scribble Hub candidates",
            body,
        )
        self.close()

    def _prepare_mixed_report(self):
        if len(self.comparison_stories) != 1:
            self.notice.setText("Add exactly one story page before preparing mixed-source research.")
            return
        url = self.youtube_url.text().strip()
        focus = self.research_focus.text().strip()
        if not focus:
            self.notice.setText("State the mixed-source research focus before retrieving the transcript.")
            return
        self.youtube.setEnabled(False)
        self.notice.setText("The Researcher is retrieving one bounded public English YouTube transcript...")
        worker = TranscriptWorker(url)
        worker.signals.ready.connect(self._mixed_transcript_ready)
        worker.signals.failed.connect(self._mixed_transcript_failed)
        self.transcript_worker = worker
        QThreadPool.globalInstance().start(worker)

    def _mixed_transcript_ready(self, transcript):
        story = self.comparison_stories[0]
        body = Researcher().report_mixed_story_youtube(
            story,
            transcript,
            self.research_focus.text().strip(),
            QDateTime.currentDateTime().toString(Qt.DateFormat.ISODate),
        )
        self.report_ready.emit(f"Mixed-source investigation — {story.title}", body)
        self.close()

    def _mixed_transcript_failed(self, message: str):
        self.notice.setText(f"The YouTube transcript could not be used safely: {message}")
        self.youtube.setEnabled(len(self.comparison_stories) == 1)

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
