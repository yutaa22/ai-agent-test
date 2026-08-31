
class SessionMemory:
    """
    Lightweight session-level conversation memory.

    Keeps only the information required to resolve
    follow-up questions during the current conversation.
    """

    def __init__(self):
        self.messages = []
        self.active_order_id = None
        self.active_topic = None

    def add_message(self, role, content):
        """
        Add a conversation message and keep memory bounded.
        """

        self.messages.append(
            {
                "role": role,
                "content": content,
            }
        )

        # Keep only the most recent 12 messages.
        if len(self.messages) > 12:
            self.messages = self.messages[-12:]

    def set_order(self, order_id):
        """Set the active order for conversation follow-ups."""

        self.active_order_id = order_id

    def set_topic(self, topic):
        """Set the active conversation topic."""

        self.active_topic = topic

    def get_context(self):
        """Return the current session context."""

        return {
            "active_order_id": self.active_order_id,
            "active_topic": self.active_topic,
            "messages": self.messages[-6:],
        }

    def clear(self):
        """Clear all session state."""

        self.messages = []
        self.active_order_id = None
        self.active_topic = None

