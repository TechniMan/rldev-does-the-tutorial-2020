from typing import Iterable, List, Reversible, Tuple
import textwrap
import tcod

import colours


class Message:
    def __init__(self, text: str, fg: Tuple[int, int, int]):
        self.plain_text = text
        self.fg = fg
        self.count = 1

    @property
    def full_text(self) -> str:
        """ Returns the text of the message plus the count if more than 1 """
        if self.count > 1:
            return f"{self.plain_text} (x{self.count})"
        return self.plain_text


class MessageLog:
    def __init__(self):
        self.messages: List[Message] = []

    def add_message(self, text: str, fg: Tuple[int, int, int] = colours.DEFAULT,
    *, stack: bool = True) -> None:
        """ Add a message to this log.
        If `stack` is True, then the message can stack with a previous message of the same text.
        """
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text, fg))

    def render(self, console: tcod.Console, x: int, y: int, width: int, height: int) -> None:
        """ Render the message log at the given location """
        self.render_messages(console, x, y, width, height, self.messages)

    @staticmethod
    def wrap(string: str, width: int) -> Iterable[str]:
        """ Returns a wrappedn text message """
        # handle newlines
        for line in string.splitlines():
            yield from textwrap.wrap(line, width, expand_tabs=True)

    @classmethod
    def render_messages(cls, console: tcod.Console,
            x: int, y: int, width: int, height: int, messages: Reversible[Message]) -> None:
        """ Render the given messages within the given area """
        y_offset = height - 1

        # print messages in reverse order (latest to oldest)
        for message in reversed(messages):
            for line in reversed(list(cls.wrap(message.full_text, width))):
                console.print(x, y + y_offset, line, message.fg)
                # adjust offset to print on the next line up
                y_offset -= 1
                # abort if we run out of space
                if y_offset < 0:
                    return
