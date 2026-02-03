from typing import Dict, Any, List, Optional
from app.core.llm import get_llm_response
from datetime import datetime

class SummarizationMemory:
    def __init__(self, db, user_id: str, max_recent: int = 10):
        self.db = db
        self.user_id = user_id
        self.max_recent = max_recent
        self.recent_messages = []
        self.summary = ""
        self.batch_size = max_recent

        print(f" BatchSummarizationMemory initialized")
        print(f"   User: {user_id}")
        print(f"   Max recent messages: {max_recent}")
        print(f"   Batch size: {self.batch_size}")

    def load_from_database(self, history: List[Dict[str, Any]]):
        print(f"\n Loading {len(history)} messages from history...")

        if not history:
            print("   No history to load")
            return

        total_messages = len(history)

        if total_messages <= self.max_recent:
            print(f" All {total_messages} messages fit in recent")
            self.recent_messages = history
            return

        old_messages = history[:-self.max_recent]
        recent_messages = history[-self.max_recent:]

        print(f" Old messages to summarize: {len(old_messages)}")
        print(f" Recent messages to keep: {len(recent_messages)}")

        self.summary = self._summarize_batch(old_messages)
        self.recent_messages = recent_messages

        print(f"History loaded!")
        print(f"   Summary length: {len(self.summary)} characters")
        print(f"   Recent messages: {len(self.recent_messages)}")

    def _summarize_batch(self, messages: List[Dict[str, Any]]) -> str:
        if not messages:
            return ""

        print(f"\n Summarizing {len(messages)} messages as batch...")

        conversation = ""
        for msg in messages:
            role = "User" if msg['role'] == 'user' else "Assistant"
            conversation += f"{role}: {msg['content']}\n"

        prompt = f"""Summarize this medical conversation into 2-3 sentences.
Keep only the most important health-related information.

Conversation:
{conversation}

Summary:"""

        try:
            summary = get_llm_response(prompt).strip()
            print(f" Batch summary created: '{summary[:80]}...'")
            return summary
        except Exception as e:
            print(f"  Error summarizing batch: {e}")
            return f"Discussed {len(messages)} messages"

    def add_message(self, user_message: str, bot_response: str):
        print(f"\n Adding new message to memory...")

        self.recent_messages.append({
            "role": "user",
            "content": user_message
        })
        self.recent_messages.append({
            "role": "assistant",
            "content": bot_response
        })

        print(f"Message count: {len(self.recent_messages)}")

        if len(self.recent_messages) > self.max_recent:
            self._batch_summarize_and_trim()

    def _batch_summarize_and_trim(self):
        print(f"\n Exceeded {self.max_recent} messages! Batch summarizing...")

        messages_to_summarize = self.recent_messages[:self.batch_size]

        print(f"Taking batch of {len(messages_to_summarize)} messages")

        batch_summary = self._summarize_batch(messages_to_summarize)

        if self.summary:
            print(f" Merging with existing summary...")
            merge_prompt = f"""Merge these two summaries into one concise summary:

Summary 1 (older conversations): {self.summary}

Summary 2 (recent batch): {batch_summary}

Merged summary (keep it concise, 2-3 sentences):"""

            try:
                self.summary = get_llm_response(merge_prompt).strip()
                print(f" Summaries merged!")
            except Exception as e:
                print(f" Error merging: {e}")
                self.summary = f"{self.summary} {batch_summary}"
        else:

            print(f" Creating first summary...")
            self.summary = batch_summary

        self.recent_messages = self.recent_messages[self.batch_size:]

        print(f" Batch summarization complete!")
        print(f" Summary: '{self.summary[:100]}...'")
        print(f" Recent messages remaining: {len(self.recent_messages)}")

    def get_memory_context(self) -> str:
        context = ""

        if self.summary:
            context += f"[Previous conversation summary]:\n{self.summary}\n\n"

        if self.recent_messages:
            context += "[Recent conversation]:\n"
            for msg in self.recent_messages:
                if msg['role'] == 'user':
                    context += f"User: {msg['content']}\n"
                else:
                    context += f"Assistant: {msg['content']}\n"

        return context.strip()

    def save_to_database(self):
        if not self.summary:
            return

        print(f"\nSaving summary to database...")

        try:
            from app.logic.user_summary import UserSummary
            existing = self.db.query(UserSummary).filter_by(
                user_id=self.user_id
            ).first()

            if existing:
                existing.summary = self.summary
                print(f"Updated existing summary")
            else:
                new_summary = UserSummary(
                    user_id=self.user_id,
                    summary=self.summary
                )
                self.db.add(new_summary)
                print(f"Created new summary")

            self.db.commit()
            print(f"Summary saved!")

        except Exception as e:
            print(f"Error saving summary: {e}")
            self.db.rollback()

    def get_stats(self) -> Dict[str, Any]:
        context = self.get_memory_context()

        return {
            "summary_length": len(self.summary),
            "recent_messages": len(self.recent_messages),
            "batch_size": self.batch_size,
            "total_characters": len(context),
            "summary_preview": self.summary[:100] if self.summary else "(empty)",
            "memory_preview": context[:200] + "..." if context else "(empty)"
        }