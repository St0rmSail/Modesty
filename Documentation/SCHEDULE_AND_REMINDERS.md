# Schedule and Reminders

**Status:** Build 0.16 implemented and demonstrated

Modesty's first schedule is local, persistent, and deterministic. Reminder dates use the machine's local timezone and are stored as UTC in `Data/modesty.db`. Explicit `YYYY-MM-DD` dates and 24-hour times prevent the language model from guessing what phrases such as “next Friday” mean.

Each reminder has a stable ID, due time, text, pending/completed state, creation time, and optional completion time. Completion retains the record; deletion is permanent and requires confirmation in the visible Schedule window.

The opening address reports only pending reminders that are overdue or due today, with bounded detail. Future reminders remain quiet until relevant. The Schedule window shows pending and completed records and permits explicit completion or deletion.

Calendar accounts, recurrence, natural-language date interpretation, background notifications, and notification delivery while Modesty is offline are not implemented. No reminder may imply that work happened merely because its due time passed.

Live acceptance demonstrated command creation, restart persistence, overdue greeting, readable controls, visible review, and confirmed deletion. Eighty-nine automated tests passed in `E:\Modesty`.
