from typing import Dict, Any, List
from datetime import datetime, timezone
from app.core.llm import get_llm_response
import json


class BatchSummarizationMemory:
    def __init__(self, db, user_id: str, batch_size: int = 6, cache_minutes: int = 2):
        self.db = db
        self.user_id = user_id
        self.batch_size = batch_size * 2  # Convert pairs to messages
        self.cache_minutes = cache_minutes

        self.recent_messages: List[Dict[str, str]] = []
        self.summary: str = ""
        self.summary_updated_at = None

        print(f"\n BatchSummarizationMemory initialized")
        print(f"   User: {user_id}")
        print(f"   Batch size: {batch_size} pairs ({self.batch_size} messages)")
        print(f"   Cache expiration: {cache_minutes} minutes")

    def load_from_database(self, history: List[Dict[str, Any]]):

        print(f"\n Loading {len(history)} messages from history...")

        if not history:
            self.recent_messages = []
            return

        try:
            from app.logic.user_summary import UserSummary

            print(f"\n Checking summary expiration...")

            existing = self.db.query(UserSummary).filter_by(
                user_id=self.user_id
            ).first()

            print(f"    Query result: {existing}")

            if not existing:
                print(f"  ️ No summary in database")
                self.summary = ""
                self.recent_messages = []

                print(f"   Attempting to load batch...")
                self.load_batch_from_database()

                print(f"   Starting fresh (empty)")
                return

            print(f"    Summary found: {existing.summary[:50]}...")

            if not existing.updated_at:
                print(f"    Summary has NO timestamp!")
                self.summary = ""
                self.recent_messages = []
                print(f"   Attempting to load batch...")
                self.load_batch_from_database()
                return


            now = datetime.now(timezone.utc)
            print(f"   Current time (UTC): {now}")

            summary_time = (
                existing.updated_at
                if existing.updated_at.tzinfo
                else existing.updated_at.replace(tzinfo=timezone.utc)
            )
            print(f"    Summary time: {summary_time}")

            age = now - summary_time
            age_seconds = age.total_seconds()
            age_minutes = age_seconds / 60

            print(f"   Age: {age_seconds:.1f} seconds = {age_minutes:.2f} minutes")
            print(f"    Cache limit: {self.cache_minutes} minutes")
            print(f"   Comparison: {age_minutes:.2f} > {self.cache_minutes}?")

            if age_minutes > self.cache_minutes:
                print(f"\n    YES! EXPIRED!")
                print(f"   DELETING summary from database...")

                self.db.delete(existing)
                self.db.commit()

                print(f"   Summary DELETED from database")

                # Verify deletion
                verify = self.db.query(UserSummary).filter_by(
                    user_id=self.user_id
                ).first()
                print(f"    Verify delete: {verify}")

                self.summary = ""
                self.summary_updated_at = None

                self.recent_messages = []
                print(f"   Attempting to load batch...")
                self.load_batch_from_database()

                print(f"   Starting FRESH batch")
                print(f"   Recent messages: {len(self.recent_messages)}")
                print(f"   Old summary data DISCARDED")
                return

            else:
                print(f"\n   NO! Still fresh!")
                print(f"   Keeping summary...")

                self.summary = existing.summary
                self.summary_updated_at = existing.updated_at

                self.recent_messages = []
                print(f"   Attempting to load batch...")
                self.load_batch_from_database()

                print(f"  Recent messages: {len(self.recent_messages)}")
                return

        except Exception as e:
            print(f"\n    ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.db.rollback()
            self.summary = ""
            self.recent_messages = []

    def load_batch_from_database(self):
        try:
            from app.models.user_batch import UserBatch

            batch = self.db.query(UserBatch).filter_by(
                user_id=self.user_id
            ).first()

            if batch and batch.recent_messages:
                try:
                    self.recent_messages = json.loads(batch.recent_messages)
                    print(f"   Loaded batch from DB: {len(self.recent_messages)} messages")
                    return True
                except json.JSONDecodeError:
                    print(f"    Error parsing batch JSON")
                    return False
            else:
                print(f"    No batch in database")
                return False

        except Exception as e:
            print(f"   Error loading batch: {e}")
            return False

    def save_batch_to_database(self):
        try:
            from app.models.user_batch import UserBatch

            print(f"\n Saving batch to database...")

            existing = self.db.query(UserBatch).filter_by(
                user_id=self.user_id
            ).first()

            if existing:
                existing.recent_messages = json.dumps(self.recent_messages)
                print(f"    Updated batch ({len(self.recent_messages)} messages)")
            else:
                new = UserBatch(
                    user_id=self.user_id,
                    recent_messages=json.dumps(self.recent_messages)
                )
                self.db.add(new)
                print(f"   Created batch ({len(self.recent_messages)} messages)")

            self.db.commit()
            print(f" Batch saved successfully!")

        except Exception as e:
            print(f"   Error: {e}")
            self.db.rollback()

    def add_message(self, user_message: str, bot_response: str):
        print(f"\n Adding message to memory...")

        self.recent_messages.append({"role": "user", "content": user_message})
        self.recent_messages.append({"role": "assistant", "content": bot_response})

        print(f"   Recent messages: {len(self.recent_messages)}/{self.batch_size}")

        self.save_batch_to_database()

        if len(self.recent_messages) >= self.batch_size:
            self._create_batch_summary()

    def _create_batch_summary(self):

        print(f"\n BATCH SUMMARIZATION TRIGGERED!")
        print(f"    Batch size: {len(self.recent_messages)} messages")

        batch_messages = self.recent_messages.copy()

        print(f"   From: '{batch_messages[0]['content'][:40]}...'")
        print(f"   To: '{batch_messages[-1]['content'][:40]}...'")

        batch_summary = self._summarize_batch(batch_messages)

        if self.summary:
            print(f"\n   Merging with existing summary...")
            self.summary = self._merge_summaries(self.summary, batch_summary)
        else:
            print(f"\n Creating first summary...")
            self.summary = batch_summary

        self.recent_messages = []

        print(f"\nBatch summarization complete!")
        print(f"  Summary length: {len(self.summary)} chars")
        print(f"  Recent messages: {len(self.recent_messages)} (cleared)")

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
            print(f" Error merging: {e}")
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
            from app.logic.user_summary import UserSummary

            existing = self.db.query(UserSummary).filter_by(
                user_id=self.user_id
            ).first()

            if existing:
                existing.summary = self.summary
                existing.expired = False
                print(f"  Updated existing summary")
            else:
                new = UserSummary(
                    user_id=self.user_id,
                    summary=self.summary
                )
                self.db.add(new)
                print(f"  Created new summary")

            self.db.commit()

            self.summary_updated_at = datetime.now(timezone.utc)

            print(f"  Cache will expire in {self.cache_minutes} minutes")
            print(f"Summary saved successfully!")

        except Exception as e:
            print(f"  Error saving: {e}")
            import traceback
            traceback.print_exc()
            self.db.rollback()

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        total_chars = len(self.summary)
        for msg in self.recent_messages:
            total_chars += len(msg.get("content", ""))

        age_minutes = None
        if self.summary_updated_at:
            now = datetime.now(timezone.utc)
            summary_time = (
                self.summary_updated_at
                if self.summary_updated_at.tzinfo
                else self.summary_updated_at.replace(tzinfo=timezone.utc)
            )
            age_minutes = int((now - summary_time).total_seconds() / 60)

        return {
            "summary_length": len(self.summary),
            "recent_messages": len(self.recent_messages),
            "total_context_chars": total_chars,
            "summary_age_minutes": age_minutes,
            "cache_limit_minutes": self.cache_minutes,
            "summary_preview": self.summary[:100] if self.summary else "(empty)",
        }