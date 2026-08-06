"""
noticeboard.py
==============

The Office Noticeboard.

Every member of Modesty's staff communicates
by leaving notes here.
"""


class NoticeBoard:

    def __init__(self):
        self.notes = []

    def post(self, sender, recipient, message):

        note = {
            "from": sender,
            "to": recipient,
            "message": message
        }

        self.notes.append(note)

    def show(self):

        print("\nOffice Noticeboard")
        print("------------------")

        if not self.notes:
            print("No notices posted.")
            return

        for note in self.notes:

            print(
                f"{note['from']} -> {note['to']} : {note['message']}"
            )