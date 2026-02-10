from typing import Any, Dict, List
import json
from datetime import datetime, timezone
from app.core.llm import get_llm_response
from app.models.user_batch import UserBatch
from app.logic.user_summary import UserSummary


class LangChainBatchMemory:
    def __init__(self, db, user_id, batch_size=6, cache_minutes=2):
        self.db = db
        self.user_id = user_id
        self.batch_size = batch_size
        self.cache_minutes = cache_minutes
        self.recent_messages = []
        self.summary = ""
        self.summary_updated_at = None

    def load_from_database(self):
        print(f"\n Loading from database...")

        if not self.user_id:
            return

        try:
            print(f"\n Checking summary expiration...")

            existing = self.db.query(UserSummary).filter_by(
                user_id=self.user_id
            ).first()

            if not existing:
                print(f"  No summary in database")
                self.summary = ""
                self.recent_messages = []
                self.load_batch_from_database()
                print(f"  Starting fresh (empty)")
                return

            print(f"  Summary found")

            if not existing.updated_at:
                print(f"   Summary has NO timestamp!")
                self.summary = ""
                self.recent_messages = []
                self.load_batch_from_database()
                return

            now = datetime.now(timezone.utc)
            summary_time = (
                existing.updated_at
                if existing.updated_at.tzinfo
                else existing.updated_at.replace(tzinfo=timezone.utc)
            )

            age = now - summary_time
            age_minutes = age.total_seconds() / 60

            print(f"   Age: {age_minutes:.2f} minutes (limit: {self.cache_minutes})")

            # EXPIRED
            if age_minutes > self.cache_minutes:
                print(f"\n    EXPIRED! Deleting summary...")

                self.db.delete(existing)
                self.db.commit()

                self.summary = ""
                self.summary_updated_at = None
                self.recent_messages = []
                self.load_batch_from_database()

                print(f"  Starting FRESH batch")
                return

            else:
                print(f"\n  Still fresh! Keeping summary...")

                self.summary = existing.summary
                self.summary_updated_at = existing.updated_at

                self.recent_messages = []
                self.load_batch_from_database()

                print(f"  Recent messages: {len(self.recent_messages)}")
                return

        except Exception as e:
            print(f"\n   ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.db.rollback()
            self.summary = ""
            self.recent_messages = []

    def load_batch_from_database(self):
        try:
            batch = self.db.query(UserBatch).filter_by(
                user_id=self.user_id
            ).first()

            if batch and batch.recent_messages:
                try:
                    self.recent_messages = json.loads(batch.recent_messages)
                    print(f"   Loaded batch: {len(self.recent_messages)} messages")
                    return True
                except json.JSONDecodeError:
                    print(f"    Error parsing batch JSON")
                    return False
            else:
                print(f"   No batch in database")
                return False

        except Exception as e:
            print(f"  Error loading batch: {e}")
            return False

    def save_batch_to_database(self):
        try:
            print(f"\ Saving batch to database...")

            existing = self.db.query(UserBatch).filter_by(
                user_id=self.user_id
            ).first()

            if existing:
                existing.recent_messages = json.dumps(self.recent_messages)
                print(f"  Updated batch ({len(self.recent_messages)} messages)")
            else:
                new = UserBatch(
                    user_id=self.user_id,
                    recent_messages=json.dumps(self.recent_messages)
                )
                self.db.add(new)
                print(f" Created batch ({len(self.recent_messages)} messages)")

            self.db.commit()
            print(f"Batch saved!")

        except Exception as e:
            print(f"  Error: {e}")
            self.db.rollback()

    def add_message(self, user_message, bot_response):
        print(f"\n Adding message to memory...")

        self.recent_messages.append({"role": "user", "content": user_message})
        self.recent_messages.append({"role": "assistant", "content": bot_response})

        print(f"  Recent messages: {len(self.recent_messages)}/{self.batch_size}")

        self.save_batch_to_database()

        if len(self.recent_messages) >= self.batch_size:
            self._create_batch_summary()

    def _create_batch_summary(self):
        print(f"\n BATCH SUMMARIZATION TRIGGERED!")
        print(f"  Batch size: {len(self.recent_messages)} messages")

        batch_messages = self.recent_messages.copy()

        batch_summary = self._summarize_batch(batch_messages)

        if self.summary:
            print(f"\n  Merging with existing summary...")
            self.summary = self._merge_summaries(self.summary, batch_summary)
        else:
            print(f"\n  Creating first summary...")
            self.summary = batch_summary

        self.recent_messages = []

        print(f"\n Batch summarization complete!")

        self.save_to_database()
        self.save_batch_to_database()

    def _summarize_batch(self, messages: List[Dict[str, Any]]) -> str:
        conversation = ""
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation += f"{role}: {msg['content']}\n"

        prompt = f"""Summarize this medical conversation in 5–10 sentences.
Keep only clinically relevant information.

Conversation:
{conversation}

Summary:"""

        try:
            return get_llm_response(prompt).strip()
        except Exception as e:
            print(f"  Error summarizing: {e}")
            return f"Discussed {len(messages)} messages"

    def _merge_summaries(self, old: str, new: str) -> str:
        prompt = f"""Merge these two medical conversation summaries into one concise summary (5–10 sentences max).
Keep clinically relevant information.

Older summary:
{old}

Recent summary:
{new}

Merged summary:"""

        try:
            return get_llm_response(prompt).strip()
        except Exception as e:
            print(f"   Error merging: {e}")
            return f"{old} {new}"

    def get_memory_context(self) -> str:
        context = ""

        if self.summary:
            context += f"[Summary of earlier conversation]\n{self.summary}\n\n"

        if self.recent_messages:
            context += "[Recent conversation]\n"
            for msg in self.recent_messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                context += f"{role}: {msg['content']}\n"

        return context.strip()

    def save_to_database(self):
        if not self.summary:
            print(f"\n No summary to save")
            return

        print(f"\n Saving summary to database...")

        try:
            existing = self.db.query(UserSummary).filter_by(
                user_id=self.user_id
            ).first()

            if existing:
                existing.summary = self.summary
                existing.expired = False
                print(f" Updated existing summary")
            else:
                new = UserSummary(
                    user_id=self.user_id,
                    summary=self.summary
                )
                self.db.add(new)
                print(f"  Created new summary")

            self.db.commit()

            self.summary_updated_at = datetime.now(timezone.utc)

            print(f" Cache will expire in {self.cache_minutes} minutes")
            print(f"Summary saved!")

        except Exception as e:
            print(f"  Error saving: {e}")
            import traceback
            traceback.print_exc()
            self.db.rollback()