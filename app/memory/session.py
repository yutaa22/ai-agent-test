class SessionMemory:
    """
    Lightweight session-level conversation memory.

    We intentionally keep only the information required to
    resolve follow-up questions.
    """

    def __init__(self):
        self.messages = []
        self.active_order_id = None
        self.active_topic = None

    def add_message(self, role, content):
        self.messages.append(
            {
                "role": role,
                "content": content,
            }
        )

        # Keep memory bounded.
        if len(self.messages) > 12:
            self.messages = self.messages[-12:]

    def set_order(self, order_id):
        self.active_order_id = order_id

    def set_topic(self, topic):
        self.active_topic = topic

    def get_context(self):
        return {
            "active_order_id": self.active_order_id,
            "active_topic": self.active_topic,
            "messages": self.messages[-6:],
        }

    def clear(self):
        self.messages = []
        self.active_order_id = None
        self.active_topic = None
