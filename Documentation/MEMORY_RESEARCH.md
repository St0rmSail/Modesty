# Modesty Memory Research

**Status:** Research recommendation, not implementation approval

**Prepared:** 2026-08-09
**Primary question:** What should Modesty adopt from the “six levels of memory” model without losing her local-first boundaries or building machinery before it is justified?

## Executive conclusion

The six levels are best understood as six increasingly capable **recall architectures**, not as a game in which the highest number automatically wins. Each level solves a different failure:

1. Important context was never written down.
2. Written context is not loaded reliably.
3. Exact words differ, so keyword search misses relevant memories.
4. Summaries omit wording or detail that later proves important.
5. Retrieved fragments do not become organized, connected knowledge.
6. Memory remains trapped inside one AI application.

Modesty already has pieces from several levels:

- persistent SQLite conversation history and verbatim messages;
- explicitly approved personal memories;
- a private Filing Cabinet and curated shared Bookshelf;
- an Archivist with provenance, hashing, staged curation, and stale-file handling;
- SQLite FTS5 passage retrieval across both stores.

Her central weakness is not storage. It is **recall orchestration**. Personal memories are all injected into every ordinary model request, only the latest 30 messages from the active conversation are supplied, older conversations are not searchable through ordinary dialogue, and Bookshelf/Filing Cabinet retrieval happens only when Drew uses an explicit deterministic command. Modesty therefore owns several good memory components but lacks one governed process that decides what kind of memory is relevant, retrieves a bounded amount, cites it, and falls back to exact history when needed.

### Recommendation in one sentence

Build a **local, source-linked recall assembler** on top of the systems already present; add conversation search and summaries with verbatim fallback; then add selective wiki-style curation. Do **not** adopt a cloud “universal brain,” a vector database, or automatic self-writing memory merely to claim a higher level.

The sensible target is:

- Level 2 reliability now;
- Level 3 semantic retrieval only after measured FTS5 failures justify it;
- Level 4 verbatim fallback using Modesty’s existing conversation database;
- selected Level 5 curation inside the existing Bookshelf;
- Level 6 portability later through a narrow, permissioned interface—not by moving the Filing Cabinet into a cloud database.

## Research basis and limitations

This report uses the supplied video chapter map and brief, an indexed summary of the presentation, and the primary documentation or repositories for the systems it discusses. Direct automated access to the YouTube transcript was unavailable, so claims about individual products were checked against their current primary sources rather than inferred solely from the video.

The original presentation is [Every Claude Code Memory System Compared](https://www.youtube.com/watch?v=UHVFcUzAGlM&t=1s). The chapter sequence supplied by Drew is:

- 00:00 — Introduction
- 01:37 — Level 1: Native memory
- 06:31 — Level 2: Reliable recall
- 16:55 — Level 3: Search by meaning
- 23:45 — Level 4: Verbatim conversations
- 28:46 — Level 5: Self-organizing knowledge base
- 35:13 — Level 6: One brain for multiple AI tools

Claude-specific details should not be copied blindly into Modesty. Claude Code’s current documentation distinguishes user-authored instruction files from agent-authored auto memory, loads a bounded `MEMORY.md` entrypoint at session start, and reads topic files on demand. Those are useful design principles, but Modesty is an application with her own runtime, permissions, storage, and identity—not a Claude Code configuration. See [Claude Code memory documentation](https://code.claude.com/docs/en/memory).

## The six levels

### Level 1 — Native files and explicit memory

**Problem solved:** The next session starts without stable context.

**Mechanism:** Put durable instructions and remembered learnings in plain, inspectable files. A small entrypoint or index is loaded at startup; detailed topic files are read only when needed.

In the Claude-specific example, `CLAUDE.md` contains human-authored instructions while auto memory contains learnings written by Claude. Current Claude documentation recommends concise instruction files and uses a bounded `MEMORY.md` index plus optional topic files. Both are context, not hard security controls. [Claude Code memory documentation](https://code.claude.com/docs/en/memory)

**Conceptual advance over no memory:** Persistence becomes explicit and inspectable.

**Limitation:** Saving a fact does not guarantee that the correct fact will be recalled at the correct moment. Large always-loaded files also consume attention and context.

**Modesty analogue:**

- repository canon and architecture documents;
- SQLite `personal_memories` approved by Drew;
- Filing Cabinet and Bookshelf Markdown;
- explicit system prompt and deterministic Team routes.

Modesty exceeds a basic Level 1 system in storage discipline, but she does not yet have a concise, user-readable **memory entrypoint** that explains where personal facts, decisions, project briefs, transcripts, and knowledge belong.

### Level 2 — Structured memory and reliable injection

**Problem solved:** The memory exists, but the agent forgets to load it.

**Mechanism:** Separate a compact index from detailed topic files and introduce deterministic recall triggers. The referenced structured approach uses `general.md`, `tools/`, and `domain/`, with an index loaded early and topic files loaded only when relevant. It also recommends explicit maintenance—deduplicate, split oversized topics, update the index, and show changes. [How I Finally Sorted My Claude Code Memory](https://www.youngleaders.tech/p/how-i-finally-sorted-my-claude-code-memory)

Hooks are a Claude Code implementation detail, not the principle itself. The principle is: **critical recall should be a lifecycle action performed by code, not a hope expressed in a prompt**. Claude’s official guidance similarly distinguishes instructions from hooks, noting that hooks execute at fixed lifecycle points. [Claude Code hooks](https://code.claude.com/docs/en/hooks-guide)

**Conceptual difference from Level 1:**

- Level 1 asks, “Where is memory stored?”
- Level 2 asks, “What guarantees that the right memory is considered?”

**Limitation:** Routing still depends mainly on categories, filenames, trigger rules, or keyword logic. It may miss conceptually related material whose vocabulary differs.

**Modesty analogue:** Personal memories are deterministically added to the system context, and Archivist/Library commands deterministically invoke local tools. However, all personal memories are injected rather than selected, document recall is command-dependent, and there is no unified budget or recall trace.

### Level 3 — Search by meaning

**Problem solved:** Keyword mismatch. A memory may discuss “grounding the character” while the new question asks about “keeping her feet fixed.”

**Mechanism:** Split material into chunks, create embeddings representing meaning, and retrieve semantically similar chunks. Mature systems often combine vector similarity with lexical search rather than replacing keywords entirely.

MemSearch currently describes Markdown as the source of truth, a rebuildable Milvus shadow index, and hybrid BM25 plus dense retrieval combined through reciprocal-rank fusion. It also provides progressive recall: ranked chunk, expanded Markdown section, then raw transcript if needed. [MemSearch repository](https://github.com/zilliztech/memsearch)

**Conceptual difference from Level 2:**

- Level 2 chooses memory through explicit routing.
- Level 3 computes relevance from the meaning of the current request.

**Limitation:** Semantic relevance is probabilistic. Embeddings can return plausible but wrong context, introduce dependencies, complicate privacy, and obscure why a result was chosen. A vector index should remain rebuildable; it should never become the only copy of memory.

**Modesty analogue:** Build 0.11 added FTS5 full-text passage search with BM25 ranking, provenance, changed-file refresh, and stale removal. That is strong lexical retrieval but not semantic retrieval. The roadmap correctly says not to select a vector database until FTS5 demonstrates a real limitation.

### Level 4 — Verbatim conversational recall

**Problem solved:** Summaries compress away exact wording, qualifications, chronology, tone, or the evidence required to resolve a dispute.

**Mechanism:** Retain original conversations and make them searchable. A summarized or indexed result acts as the locator; the system can then expand to the exact conversation passage.

MemPalace describes itself as local-first, stores conversation history verbatim rather than summarizing or paraphrasing it, organizes scope through wings/rooms/drawers, and currently uses a pluggable retrieval backend. [MemPalace repository](https://github.com/MemPalace/mempalace)

**Conceptual difference from Level 3:**

- Level 3 improves discovery, usually over chunks or summaries.
- Level 4 preserves an evidentiary record and permits exact fallback.

Level 4 is not “better than summaries” for every question. Exact transcripts are noisy and expensive to load. The useful pattern is progressive disclosure:

1. concise result or summary;
2. relevant exchange;
3. full conversation only when truly required.

**Modesty analogue:** Every user and assistant message is already stored verbatim in `Data/modesty.db`. Drew can reopen conversations, but ordinary recall uses only the last 30 messages from the active conversation. There is no cross-conversation FTS index, no conversation summary layer, and no citation back to message IDs or dates. The storage portion of Level 4 exists; the recall portion does not.

### Level 5 — Self-organizing knowledge base

**Problem solved:** Retrieval returns fragments, but knowledge does not compound. Contradictions, entities, decisions, and links remain scattered.

**Mechanism:** Separate immutable sources from an LLM-maintained wiki and a schema governing ingestion and maintenance. Karpathy’s LLM Wiki proposal describes:

- raw sources as immutable source of truth;
- interlinked Markdown wiki pages maintained by the LLM;
- a schema file defining conventions and workflows;
- `index.md` for content navigation;
- `log.md` for chronological operations;
- ingest, query, and lint workflows.

The core value is that synthesis is performed once and refined when sources change, rather than being reconstructed from scratch for every question. [Karpathy’s LLM Wiki proposal](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

**Conceptual difference from Level 4:**

- Level 4 remembers what was said.
- Level 5 maintains what is currently known, how ideas connect, and where sources disagree.

**Limitation:** Automatic organization can silently convert inference into “fact,” overwrite nuance, or spread one error through many linked pages. Modesty therefore needs staging, provenance, supersession, and human approval rather than unrestricted self-editing.

**Modesty analogue:** The Bookshelf already has Inbox, Workbench, curated collections, metadata, provenance, and an Archivist. This is an excellent Level 5 foundation. What is missing is a disciplined synthesis layer: explicit source links between notes, contradiction/supersession records, topic pages, and a lint pass for orphans, stale claims, and missing provenance.

### Level 6 — A universal brain for multiple AI tools

**Problem solved:** Each AI client develops an isolated memory of the same person and work.

**Mechanism:** Put governed memory behind a shared protocol or service so multiple clients can capture and retrieve it. Open Brain describes a shared database with vector search and MCP access; Mem0 describes a universal memory layer supporting user, session, and agent state. [Open Brain repository](https://github.com/NateBJones-Projects/OB1), [Mem0 repository](https://github.com/mem0ai/mem0)

MCP is an open standard through which AI applications connect to external systems, tools, and workflows. It can provide portability, but the protocol itself does not decide what a client should be allowed to read or write. [Model Context Protocol introduction](https://modelcontextprotocol.io/introduction)

**Conceptual difference from Level 5:**

- Level 5 organizes one durable knowledge environment.
- Level 6 makes governed parts of that environment available across tools.

**Limitation:** Centralization increases the blast radius of a bad credential, over-broad tool, poisoned write, or privacy mistake. “Universal” must not mean “every tool sees everything.”

**Modesty analogue:** The local Bookshelf is conceptually portable and could later expose narrow read/search/submit operations. The Filing Cabinet must remain private and local. The Grand Library is an online exchange mode, not a universal private-memory server. Modesty should therefore pursue **selective interoperability**, not a cloud replica of her entire mind.

## Levels compared at a glance

| Level | Primary question | Source of truth | Recall method | New capability over the previous level | Principal risk |
|---|---|---|---|---|---|
| 1 | What must survive a restart? | Plain files or explicit records | Startup load/manual read | Persistence | Bloat and stale context |
| 2 | How is recall made reliable? | Indexed topic files/records | Deterministic routing or injection | Recall lifecycle | Wrong routing or over-injection |
| 3 | What if the words differ? | Human-readable source plus shadow index | Semantic or hybrid retrieval | Meaning-based discovery | Opaque false relevance |
| 4 | What exactly was said? | Verbatim transcript | Search, then exact expansion | Evidentiary recall | Noise, privacy, token cost |
| 5 | What do we currently know? | Immutable sources plus curated synthesis | Linked pages, indexes, linting | Compounding knowledge | Automated distortion |
| 6 | How do multiple tools share memory? | Governed service/database | API or MCP | Portability | Expanded security boundary |

## Glossary

### Agent memory

Persistent state made available to an AI agent beyond the current prompt. It may include user facts, prior events, learned procedures, task state, or retrieved knowledge.

### Audit trail

An append-only record of who or what performed a memory operation, when it happened, what source was involved, and whether the operation succeeded.

### Automatic memory

Memory selected or written by an AI system without the user manually creating every entry. Automatic does not mean trustworthy; it requires review, provenance, and deletion controls.

### BM25

A lexical ranking algorithm used by full-text search. It rewards terms that occur in a relevant document but are not common throughout the collection. Modesty’s FTS5 search uses BM25 ranking.

### Brief

A concise, current operating snapshot for a project or task: purpose, state, constraints, decisions, and next step. A brief is not a transcript and should not become an everything-file. It answers “What must I know to resume useful work now?”

### Capture

The act of recording information for possible future use. Capture may be manual, approval-gated, event-triggered, or automatic.

### Chunk

A bounded segment of a larger document used for indexing and retrieval. Chunks should be large enough to preserve meaning and small enough to avoid returning irrelevant surrounding text.

### Context window

The finite working material visible to a model during one request: instructions, recent messages, retrieved memories, tool descriptions, and source text. Stored memory outside this window has no effect until retrieved.

### Context rot

The practical decline in relevance or instruction-following when too much stale, conflicting, or weakly related material occupies the context window.

### Curation

Reviewing, classifying, linking, correcting, superseding, or rejecting captured material so that retained knowledge becomes more useful rather than merely larger.

### Dense retrieval

Retrieval using embedding vectors rather than exact word matches. It is commonly called semantic search.

### Embedding

A numeric vector representing features of text or another object. Similar vectors are treated as conceptually related. An embedding is an index representation, not the original memory.

### Episodic memory

Memory of events situated in time: a conversation, test, decision meeting, failure, or completed task.

### FTS / full-text search

Search across the actual words in documents. SQLite FTS5 is Modesty’s current local document-search engine.

### Hook

Code executed at a defined lifecycle event, such as session start or prompt submission. In this research, its conceptual value is deterministic timing. Modesty need not copy Claude Code’s hook implementation.

### Hybrid search

A retrieval method combining lexical search such as BM25 with dense semantic search and sometimes other signals such as entities or recency.

### Index

Either a human-readable navigation document or a machine-generated structure that speeds retrieval. A machine index should be rebuildable from authoritative sources.

### Injection

Adding selected memory to the model’s current context. Injection is where stored memory becomes active influence.

### Knowledge base

An organized collection of durable facts, sources, concepts, procedures, and relationships. It differs from raw memory because it has been curated for reuse.

### Knowledge graph

Entities and concepts represented as nodes with explicit relationships as edges. Useful when relationships matter, but not required merely to store linked Markdown.

### Lexical search

Search based on actual terms and token patterns. It is explainable and inexpensive but can miss synonyms or paraphrases.

### Long-term memory

Durable information retained beyond the current conversation or restart.

### Memory policy

Deterministic rules deciding what may be captured, retrieved, injected, changed, shared, archived, or deleted.

### MCP / Model Context Protocol

An open standard for exposing data and tools to compatible AI applications. MCP is transport and interface; it is not a privacy policy or memory model.

### Ontology

A formal description of types of things and their permitted relationships. It is more rigorous than a folder taxonomy and should be introduced only if Modesty needs machine reasoning across stable entity types.

### Progressive disclosure

Returning the smallest useful representation first, then expanding only when needed: result summary → source passage → full document or verbatim conversation.

### Procedural memory

Knowledge of how to perform an action: a workflow, command sequence, troubleshooting procedure, or curation rule.

### Provenance

Where information came from and how it entered the system. Good provenance includes source type, source identifier, capture time, and transformation history.

### RAG / retrieval-augmented generation

Retrieving relevant external material and supplying it to a generative model for an answer. Retrieval does not guarantee truth; citations and source evaluation remain necessary.

### Recall

The act of selecting stored memory for a present request. Memory that cannot be recalled is only storage.

### Recall trace

A record of what was retrieved, why, with what score or rule, what was injected, and what was omitted due to limits. It makes memory behavior inspectable.

### Reranking

Reordering initial search results using another relevance signal or model. It can improve precision but adds cost and another source of opaque judgment.

### RRF / reciprocal-rank fusion

A simple method for combining ranked result lists from different retrievers, such as BM25 and vector search.

### Schema

The contract describing how memory is structured and maintained. It may define record types, required metadata, naming rules, privacy classes, source fields, lifecycle states, and allowed operations. A schema is not merely a database table; a Markdown convention can also be a schema.

### Semantic memory

Durable knowledge expressed as facts and concepts, without requiring replay of the event in which it was learned.

### Semantic search

Search based on conceptual similarity, normally using embeddings. It is valuable when vocabulary differs but needs lexical and provenance safeguards.

### Shadow index

A machine-generated index that can be destroyed and rebuilt from the real source of truth. Modesty’s FTS database should remain a shadow of her Markdown stores, not their replacement.

### Source of truth

The authoritative representation from which derived indexes, summaries, or views can be rebuilt. Modesty’s source-of-truth hierarchy also depends on privacy and approval status.

### Supersession

Marking a memory or knowledge item as replaced by a newer one without erasing history. This is safer than silent overwrite.

### Taxonomy

A controlled classification hierarchy, such as Personal / Decisions / Projects or Reference / Procedures / Research. It answers where something belongs; it does not express every relationship.

### Token budget

A maximum amount of model context allocated to a source category. Budgets keep memory helpful and prevent one store from overwhelming the current conversation.

### Vector database

A database optimized for storing and searching embedding vectors. It is infrastructure for semantic retrieval, not a prerequisite for memory.

### Verbatim memory

Original text retained without summarization. It preserves evidence but should normally be accessed through bounded search and expansion.

### Working memory

The current conversational and task context actively available to the model. For Modesty this currently includes her system context, approved personal memories, and the latest active-conversation messages.

## Modesty’s current memory model

### Current flow

```text
Approved personal memories ───────────────┐
                                         │ all injected
Latest 30 active-conversation messages ──┼──> local Ollama request
                                         │
System identity and capability prompt ───┘

Explicit "Ask the Library" command
    -> Archivist inventory
    -> FTS5 search across Filing Cabinet + Bookshelf
    -> bounded passages with source paths
    -> deterministic response (not fed into ordinary model dialogue)

All conversations
    -> stored verbatim in Data/modesty.db
    -> reopenable through the UI
    -> not searched across conversations during ordinary recall
```

### Honest capability assessment

| Memory function | Current state | Strength | Gap |
|---|---|---|---|
| Active conversation | Latest 30 messages sent to Ollama | Simple, bounded | Abrupt cutoff; no summary of older active context |
| Conversation archive | All messages stored verbatim in SQLite | Exact and local | No cross-conversation search, citations, or progressive expansion |
| Personal facts | Explicit add/edit/delete with source | Human-controlled | Every fact is injected every time; no relevance filtering, expiry, confidence, or supersession |
| Private documents | Filing Cabinet Markdown plus FTS5 | Local, inspectable, provenance-preserving | Retrieval is explicit rather than naturally orchestrated |
| Shared knowledge | Bookshelf with Inbox/Workbench/collections | Strong curation boundary | Few synthesis/linking/lint capabilities yet |
| Search | FTS5 BM25 passages | Fast, local, explainable | No semantic similarity; no measured failure corpus yet |
| Project instructions | Repository canon, architecture, decisions, roadmap | Strong public project record | Not automatically transformed into Modesty’s runtime project brief |
| Recall policy | Split across UI and deterministic commands | Safe in bounded duties | No single selector, budget, trace, or conflict rule |
| Portability | Human-readable Markdown stores | Tool-independent at file level | No narrow multi-client interface; appropriately no universal private brain |

### Where Modesty sits in the six-level model

Calling Modesty “Level 3” or “Level 5” would be misleading because the levels describe architectures, not a single maturity score.

The most accurate description is:

- **Level 2 foundation:** explicit memories and deterministic routes exist, but recall selection is incomplete.
- **Level 3 lexical retrieval:** FTS5 exists; semantic retrieval does not.
- **Level 4 storage without recall:** verbatim conversations exist but are not searchable across sessions.
- **Early Level 5 governance:** the Bookshelf/Archivist workflow is strong, but synthesis and linking are limited.
- **No Level 6 service:** this is correct for now; privacy boundaries are more important than portability.

## Recommended changes

### Priority 0 — Write the memory contract before adding machinery

Create one concise policy defining memory types, sources, privacy, lifecycle, and recall priority. The contract should answer:

- Is this an instruction, personal fact, event, decision, task state, source document, or synthesized knowledge?
- Which store owns it?
- Who may create or change it?
- Must Drew approve it?
- Is it always loaded, retrieved on demand, or never injected automatically?
- How is it corrected, superseded, archived, or deleted?

This avoids mixing “how Modesty should behave” with “what Drew once said” and “what a source claims.”

### Priority 1 — Add a local recall assembler

Before an ordinary Ollama request, deterministic code should assemble a bounded context packet:

1. identity and non-negotiable rules;
2. a compact active project/task brief when relevant;
3. only relevant approved personal memories;
4. recent conversational turns;
5. an active-conversation rolling summary for older turns;
6. relevant local Library passages when the question is knowledge-seeking;
7. visible source labels and a recall trace.

Suggested initial budgets—not permanent constants—are:

| Source | Initial budget |
|---|---:|
| Identity and hard boundaries | always present, concise |
| Personal memories | top 3–5 relevant records |
| Recent messages | 12–20 turns |
| Active conversation summary | 1 compact block |
| Local document passages | top 3 passages |
| Prior conversation matches | top 2 exchanges, only when indicated |

Selection must happen locally. Security rules remain code, not model suggestions.

### Priority 2 — Make existing verbatim history searchable

Add an FTS5 shadow index over conversation messages before introducing embeddings. Search results should preserve:

- conversation ID and title;
- message ID;
- role;
- timestamp;
- exact excerpt.

Recall should be progressive:

```text
conversation summary
    -> matching exchange
        -> surrounding messages
            -> whole conversation only on explicit request
```

This gives Modesty the practical benefit of Level 4 using data she already stores.

### Priority 3 — Add summaries, but never replace transcripts

Create a rolling summary for long active conversations and a closing summary for inactive conversations. Store summaries as derived records with:

- source conversation ID;
- covered message range;
- generated timestamp and model;
- version;
- explicit statement that the transcript remains authoritative.

The summary should extract decisions, unresolved questions, commitments, and stable facts—not retell every exchange.

### Priority 4 — Improve personal-memory records

Extend `personal_memories` beyond category/content/source with fields such as:

- `status`: active, superseded, disputed, archived;
- `privacy`: private, shareable-summary, public;
- `confidence`: user-confirmed, inferred, imported;
- `valid_from` and optional `valid_until`;
- `supersedes_id`;
- `last_used_at` and `use_count` for inspection—not automatic deletion.

Never silently “learn” a sensitive personal fact from ordinary conversation. Automatic capture should create a candidate requiring approval.

### Priority 5 — Add a selective Level 5 synthesis layer

Do not give an LLM unrestricted ownership of the Bookshelf. Instead, extend the Archivist workflow:

```text
immutable or cited source
    -> Inbox
    -> Workbench extraction proposal
    -> proposed links / contradictions / topic update
    -> Drew approval when important
    -> curated Reference, Research, Procedure, or Project page
```

Add bounded lint checks for:

- missing provenance;
- broken links;
- orphan pages;
- likely duplicates;
- contradictory active claims;
- superseded material still presented as current;
- pages whose source has disappeared.

### Priority 6 — Measure before adding semantic search

Build a small recall evaluation set from real Modesty questions:

- exact keyword matches;
- synonyms and paraphrases;
- date-sensitive questions;
- conflicting facts;
- irrelevant but lexically similar passages;
- private versus shareable results.

Only add local embeddings if FTS5 repeatedly fails meaningful cases. If added:

- retain FTS5;
- use hybrid ranking;
- keep Markdown/SQLite records authoritative;
- keep embeddings local unless Drew explicitly approves otherwise;
- log why each result was selected;
- make the vector index disposable and rebuildable.

### Priority 7 — Defer the universal brain

When multiple AI tools genuinely need shared access, expose a narrow interface over approved Bookshelf material and perhaps user-approved portable profile facts. Do not expose the Filing Cabinet database or raw conversation archive.

Possible future operations:

- `search_bookshelf(query)` — read-only;
- `get_bookshelf_source(id)` — read-only and bounded;
- `submit_bookshelf_candidate(packet)` — writes only to Inbox;
- `get_public_profile()` — approved fields only;
- no generic filesystem read;
- no generic memory write;
- no delete without local confirmation.

This is Level 6 **governance**, not merely Level 6 connectivity.

## What not to implement now

- Do not replace SQLite with a hosted memory service.
- Do not move private memories or transcripts into the Grand Library.
- Do not install Milvus, ChromaDB, pgvector, Mem0, MemSearch, or MemPalace wholesale.
- Do not auto-save every conversation statement as a fact.
- Do not allow a model to silently merge, delete, or “correct” memory.
- Do not inject the entire Filing Cabinet, Bookshelf, transcript archive, or personal-memory table into every prompt.
- Do not create a knowledge graph until questions require relationships that Markdown links and metadata cannot express.
- Do not treat embedding similarity as truth.

## Proposed file tree

This tree builds on the existing repository, Filing Cabinet, Bookshelf, and SQLite files. It does not create a new fourth memory kingdom.

```text
E:\Modesty\
├── Documentation\
│   └── MEMORY_CONTRACT.md                 # public architecture and rules
├── Config\
│   └── memory_policy.json                 # deterministic runtime budgets/policy
└── Data\                                  # generated, local, ignored by Git
    ├── modesty.db                         # conversations, messages, personal facts, summaries
    └── knowledge_catalog.db               # rebuildable document/passages FTS index

E:\Modesty Filing Cabinet\
├── index.md                               # short private-memory map
├── Personal\
│   ├── profile.md                         # stable Drew-approved facts
│   └── preferences.md                     # interaction and workflow preferences
├── Projects\
│   └── Modesty\
│       └── brief.md                       # current private operating snapshot
├── Decisions\
│   ├── index.md                           # decision catalogue
│   └── D-001-local-first-memory.md        # one durable decision
├── Conversations\
│   └── Summaries\
│       └── 2026-08-09-memory-research.md  # derived summary; transcript stays in SQLite
└── Archive\                               # superseded private material

E:\Modesty Bookshelf\
├── index.md                               # shared collection map
├── Reference\
│   └── Memory\
│       └── glossary.md                    # reusable shared definitions
├── Procedures\
│   └── memory-curation.md                 # approved repeatable workflow
├── Research\
│   └── Memory\
│       └── six-levels-assessment.md       # sourced research outcome
├── Inbox\                                 # new/imported candidates
├── Workbench\                             # validation, linking, reconciliation
└── Archive\                               # superseded shared knowledge
```

## Sample content for every proposed file

The samples are intentionally short. They demonstrate structure, not finished policy.

### `Documentation/MEMORY_CONTRACT.md`

```markdown
# Modesty Memory Contract

## Authority

1. Drew's explicit current statement.
2. User-approved active memory.
3. Verified project decision.
4. Sourced local knowledge.
5. Derived summary.

## Memory classes

- Instruction: how Modesty must behave; repository-owned.
- Personal fact: Drew-approved private semantic memory.
- Event: time-bound episodic memory with source.
- Decision: durable conclusion with status and supersession.
- Conversation: verbatim evidence stored in SQLite.
- Knowledge: cited material in Filing Cabinet or Bookshelf.

## Non-negotiable rules

- The Filing Cabinet never goes online.
- Derived indexes are rebuildable shadows.
- Summaries never replace transcripts.
- Inferred personal facts require approval.
- Deletion and supersession are distinct operations.
```

### `Config/memory_policy.json`

```json
{
  "version": 1,
  "recent_message_limit": 20,
  "personal_memory_limit": 5,
  "document_passage_limit": 3,
  "prior_exchange_limit": 2,
  "automatic_personal_capture": false,
  "conversation_search": "fts5",
  "semantic_search": "disabled",
  "recall_trace": true,
  "private_store_online_access": false
}
```

### `Data/modesty.db`

This is generated SQLite, not a hand-edited text file. An illustrative derived-summary record would logically contain:

```text
conversation_id: 42
first_message_id: 801
last_message_id: 936
summary: "Drew approved source-linked recall and rejected echoed Library results."
model: gemma4:e2b
generated_at: 2026-08-09T08:30:00Z
authoritative: false
```

### `Data/knowledge_catalog.db`

This is also generated SQLite. An illustrative indexed passage would logically contain:

```text
store: bookshelf
relative_path: Research/Memory/six-levels-assessment.md
title: Six Levels of Memory Assessment
passage: "Modesty should add governed recall before semantic infrastructure."
sha256: <content hash>
```

### `Filing Cabinet/index.md`

```markdown
# Modesty's Filing Cabinet

Private local memory. Never available to online agents.

## Map

- [[Personal/profile]] — stable Drew-approved facts
- [[Personal/preferences]] — interaction and workflow preferences
- [[Projects/Modesty/brief]] — current private project snapshot
- [[Decisions/index]] — durable decisions and supersession
- `Conversations/Summaries/` — derived navigation into verbatim SQLite history

Detailed files are loaded only when relevant.
```

### `Filing Cabinet/Personal/profile.md`

```markdown
---
type: personal-profile
privacy: private
status: active
authority: user-approved
updated: 2026-08-09
---

# Drew

- Preferred name: Drew
- Modesty runs on Drew's single-user Windows machine.
- Do not infer who is typing solely from the Windows account.
```

### `Filing Cabinet/Personal/preferences.md`

```markdown
---
type: preferences
privacy: private
status: active
authority: user-approved
updated: 2026-08-09
---

# Interaction preferences

- Explain operational steps without assuming programming knowledge.
- Preserve concise curated records rather than raw brainstorming.
- Ask before a decision that materially changes scope or privacy.
- Visual changes require Drew's live acceptance before build closure.
```

### `Filing Cabinet/Projects/Modesty/brief.md`

```markdown
---
type: project-brief
privacy: private
status: active
updated: 2026-08-09
---

# Modesty — Current Brief

## Purpose

Build a useful local-first assistant whose Study truthfully represents capability.

## Current state

Build 0.11, Ask the Library, is complete.

## Current focus

Build 0.12, Library Gateway: explicit bounded online mode.

## Hard boundaries

- Filing Cabinet never goes online.
- Online returns enter Bookshelf Inbox.
- Permission decisions remain deterministic and local.
```

### `Filing Cabinet/Decisions/index.md`

```markdown
# Private Decision Index

| Decision | Status | Summary |
|---|---|---|
| [[D-001-local-first-memory]] | Active | Private memory remains local and user-governed |

Superseded decisions remain listed and point to their replacements.
```

### `Filing Cabinet/Decisions/D-001-local-first-memory.md`

```markdown
---
type: decision
privacy: private
status: active
decided: 2026-08-09
authority: drew
supersedes: []
---

# Private memory remains local

## Decision

Modesty may expose approved Bookshelf knowledge through bounded interfaces, but
the Filing Cabinet and raw conversation archive remain local-only.

## Reason

Portability does not justify expanding the privacy boundary of personal memory.
```

### `Filing Cabinet/Conversations/Summaries/2026-08-09-memory-research.md`

```markdown
---
type: conversation-summary
privacy: private
status: derived
source_conversation_id: 42
source_message_range: 801-936
authoritative: false
---

# Memory research discussion

## Decisions

- Evaluate memory as layered capabilities, not a race to Level 6.
- Preserve local-first boundaries.

## Open questions

- Which recall failures does FTS5 demonstrate in real use?

## Evidence

The verbatim conversation remains authoritative in `Data/modesty.db`.
```

### `Bookshelf/index.md`

```markdown
# Modesty's Bookshelf

A living, curated shared collection.

## Memory knowledge

- [Glossary](Reference/Memory/glossary.md)
- [Memory curation procedure](Procedures/memory-curation.md)
- [Six-level assessment](Research/Memory/six-levels-assessment.md)

New material enters Inbox and is validated in Workbench before promotion.
```

### `Bookshelf/Reference/Memory/glossary.md`

```markdown
---
type: Reference
title: AI Memory Glossary
modesty_trust: normal
created_by: archivist
verified: reviewed-by-drew
provenance: Documentation/MEMORY_RESEARCH.md
---

# AI Memory Glossary

## Recall

Selecting stored memory for a present request.

## Provenance

The origin and transformation history of information.

## Shadow index

A machine-generated index rebuildable from authoritative sources.
```

### `Bookshelf/Procedures/memory-curation.md`

```markdown
---
type: Procedure
title: Curate a Memory Candidate
modesty_trust: important
created_by: archivist
verified: approved-by-drew
---

# Curate a Memory Candidate

1. Identify its class: instruction, fact, event, decision, conversation, or knowledge.
2. Confirm its source and privacy.
3. Check for an existing active or superseded record.
4. Propose destination and links.
5. Require Drew's approval for personal inference, important replacement, or private-to-shared movement.
6. Update the index and audit log.
7. Never erase the authoritative transcript or source.
```

### `Bookshelf/Research/Memory/six-levels-assessment.md`

```markdown
---
type: Research
title: Six Levels of AI Memory — Modesty Assessment
modesty_trust: normal
created_by: archivist
verified: reviewed-by-drew
sources:
  - https://www.youtube.com/watch?v=UHVFcUzAGlM
  - https://github.com/zilliztech/memsearch
  - https://github.com/MemPalace/mempalace
  - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
---

# Six Levels of AI Memory — Modesty Assessment

## Finding

Modesty's next memory improvement should be governed recall across her existing
stores and verbatim conversation history. Semantic infrastructure should follow
measured retrieval failures, not precede them.

## Consequence

Implement a local recall assembler, conversation FTS5, derived summaries with
verbatim fallback, and explicit supersession before considering vector search.
```

## Suggested implementation sequence

This sequence deliberately avoids colliding with Build 0.12 unless Drew chooses to reprioritize.

### Memory Build A — Contract and recall trace

- Canonize memory classes and authority.
- Add `memory_policy.json`.
- Record what context was selected for each model request.
- Do not change retrieval quality yet.

### Memory Build B — Conversation retrieval

- Add FTS5 over messages.
- Search across conversation titles, roles, dates, and content.
- Return exact cited exchanges.
- Add regression tests for deletion and privacy.

### Memory Build C — Bounded context assembly

- Select relevant personal memories rather than injecting all.
- Combine recent turns, rolling summary, conversation matches, and document passages.
- Enforce category budgets and visible provenance.
- Test conflicts and irrelevant retrieval.

### Memory Build D — Curated synthesis

- Add candidate summaries, topic links, contradiction and supersession proposals.
- Add Bookshelf linting.
- Keep promotion approval-gated.

### Memory Build E — Semantic retrieval experiment

- Create a real evaluation set.
- Establish FTS5 baseline.
- Trial one local embedding model only if baseline failures matter.
- Retain the experiment only if it materially improves precision without unacceptable latency or privacy cost.

### Memory Build F — Selective portability

- Expose approved Bookshelf operations through a narrow interface if a second client genuinely needs them.
- Keep Filing Cabinet, personal-memory database, and raw transcripts inaccessible.

## Acceptance tests for a future memory build

1. **Relevant fact:** “What name should you use for me?” retrieves the approved fact and cites its source.
2. **Irrelevant fact exclusion:** A coding question does not inject unrelated personal facts.
3. **Supersession:** A new approved preference replaces an old one without deleting history.
4. **Verbatim fallback:** “What exactly did I say?” returns an exact message with conversation and timestamp.
5. **Summary honesty:** A summary is visibly derived and never presented as a quotation.
6. **Cross-conversation recall:** A prior decision can be found without reopening conversations manually.
7. **Knowledge boundary:** A Bookshelf query may be shareable; a Filing Cabinet result remains local.
8. **Deletion:** Deleting a conversation removes its FTS results and derived summaries according to policy.
9. **Conflict:** Contradictory active facts are surfaced rather than arbitrarily chosen.
10. **Context budget:** Recall stays within configured limits and reports omitted excess.
11. **Offline operation:** All ordinary recall works without internet access.
12. **Rebuild:** Generated indexes can be deleted and rebuilt from authoritative sources.

## Final recommendation

Modesty does not need a fashionable memory package. She needs her existing memories to act as one disciplined system.

The design worth preserving is already visible:

- SQLite for local structured records and verbatim evidence;
- Markdown for human-readable private and shared knowledge;
- FTS5 for explainable local retrieval;
- the Archivist for curation and provenance;
- the Filing Cabinet/Bookshelf boundary for privacy;
- explicit approval for consequential change.

The next improvement is the connective tissue: a memory contract, a recall assembler, conversation search, progressive disclosure, supersession, and recall traces. This reaches the useful parts of Levels 2–5 while remaining unmistakably Modesty rather than becoming a copy of Claude Code, MemSearch, MemPalace, or Open Brain.

Level 6 should remain a future interface question. If and when multiple tools need shared memory, Modesty should lend them the smallest approved slice—not hand them the keys to the Filing Cabinet.

## Sources

- [Every Claude Code Memory System Compared — video](https://www.youtube.com/watch?v=UHVFcUzAGlM&t=1s)
- [Claude Code: How Claude remembers your project](https://code.claude.com/docs/en/memory)
- [Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide)
- [How I Finally Sorted My Claude Code Memory](https://www.youngleaders.tech/p/how-i-finally-sorted-my-claude-code-memory)
- [MemSearch](https://github.com/zilliztech/memsearch)
- [MemPalace](https://github.com/MemPalace/mempalace)
- [Karpathy’s LLM Wiki proposal](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [Open Brain / OB1](https://github.com/NateBJones-Projects/OB1)
- [Mem0](https://github.com/mem0ai/mem0)
- [Model Context Protocol introduction](https://modelcontextprotocol.io/introduction)
