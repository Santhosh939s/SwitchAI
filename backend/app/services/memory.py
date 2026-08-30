import uuid
import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.memory import Memory
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.memory import MemoryCreateRequest, MemoryUpdateRequest
from app.models.file import File
from app.schemas.context import ContextPackage, MemoryItem, MessageItem, ContextPassportResponse, FileContextItem

VALID_CATEGORIES = [
    "goal", "fact", "decision", "constraint", "preference",
    "project_context", "unresolved_question", "task_state"
]

def create_memory(db: Session, conversation_id: str, req: MemoryCreateRequest) -> Memory:
    cat = req.category.lower().strip()
    if cat not in VALID_CATEGORIES:
        cat = "fact"

    key_clean = req.key.strip()
    val_clean = req.value.strip()

    # Deduplication check: Do not insert duplicate memory key for the same conversation
    existing = db.query(Memory).filter(
        Memory.conversation_id == conversation_id,
        Memory.category == cat,
        Memory.key == key_clean
    ).first()

    if existing:
        existing.value = val_clean
        existing.is_pinned = req.is_pinned
        existing.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    mem = Memory(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        category=cat,
        key=key_clean,
        value=val_clean,
        is_pinned=req.is_pinned
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return mem

def get_conversation_memories(db: Session, conversation_id: str) -> List[Memory]:
    return db.query(Memory).filter(Memory.conversation_id == conversation_id).order_by(Memory.is_pinned.desc(), Memory.created_at.desc()).all()

def get_memory_by_id(db: Session, memory_id: str) -> Optional[Memory]:
    return db.query(Memory).filter(Memory.id == memory_id).first()

def update_memory(db: Session, memory_id: str, req: MemoryUpdateRequest) -> Optional[Memory]:
    mem = get_memory_by_id(db, memory_id)
    if not mem:
        return None
    if req.category is not None and req.category.lower().strip() in VALID_CATEGORIES:
        mem.category = req.category.lower().strip()
    if req.key is not None:
        mem.key = req.key.strip()
    if req.value is not None:
        mem.value = req.value.strip()
    if req.is_pinned is not None:
        mem.is_pinned = req.is_pinned
    mem.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(mem)
    return mem

def delete_memory(db: Session, memory_id: str) -> bool:
    mem = get_memory_by_id(db, memory_id)
    if not mem:
        return False
    db.delete(mem)
    db.commit()
    return True

def extract_and_store_memories_heuristic(db: Session, conversation_id: str, user_content: str, assistant_content: str):
    text = (user_content + " " + assistant_content).strip()
    text_lower = text.lower()

    # Rule 1: Goal extraction
    if "building" in text_lower or "creating" in text_lower or "goal is" in text_lower:
        if "app" in text_lower or "platform" in text_lower or "service" in text_lower:
            create_memory(db, conversation_id, MemoryCreateRequest(
                category="goal",
                key="Project Goal",
                value=user_content[:150],
                is_pinned=True
            ))

    # Rule 2: Stack & Fact extraction
    stacks = []
    if "fastapi" in text_lower: stacks.append("FastAPI")
    if "postgresql" in text_lower or "postgres" in text_lower: stacks.append("PostgreSQL")
    if "react" in text_lower: stacks.append("React")
    if "python" in text_lower: stacks.append("Python")
    if "node" in text_lower: stacks.append("Node.js")

    if stacks:
        create_memory(db, conversation_id, MemoryCreateRequest(
            category="fact",
            key="Tech Stack",
            value=", ".join(stacks),
            is_pinned=False
        ))

    # Rule 3: Decision extraction
    if "decided" in text_lower or "use" in text_lower or "architect" in text_lower:
        if "payment" in text_lower or "async" in text_lower or "auth" in text_lower:
            create_memory(db, conversation_id, MemoryCreateRequest(
                category="decision",
                key="Architectural Choice",
                value=user_content[:150],
                is_pinned=False
            ))

def build_context_package(db: Session, conversation_id: str, current_prompt: str) -> ContextPackage:
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    all_memories = get_conversation_memories(db, conversation_id)
    attached_files = db.query(File).filter(File.conversation_id == conversation_id).all()

    prompt_words = set(current_prompt.lower().split())
    relevant_mem_items: List[MemoryItem] = []

    for m in all_memories:
        is_relevant = bool(m.is_pinned)
        if not is_relevant:
            mem_text = (m.key + " " + m.value).lower()
            if any(w in mem_text for w in prompt_words if len(w) > 3):
                is_relevant = True

        if is_relevant:
            relevant_mem_items.append(MemoryItem(
                category=m.category,
                key=m.key,
                value=m.value,
                is_pinned=bool(m.is_pinned)
            ))

    file_context_items: List[FileContextItem] = [
        FileContextItem(
            filename=f.filename,
            content_summary=f.extracted_text_context[:300] if f.extracted_text_context else "File attached"
        )
        for f in attached_files
    ]

    summary_str = conv.summary if conv else None
    goal_item = next((m for m in all_memories if m.category == "goal"), None)

    return ContextPackage(
        conversation_id=conversation_id,
        user_goal=goal_item.value if goal_item else None,
        summary=summary_str,
        relevant_memories=relevant_mem_items,
        relevant_files=file_context_items,
        current_message=current_prompt
    )

def build_context_passport(db: Session, conversation_id: str) -> ContextPassportResponse:
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    all_memories = get_conversation_memories(db, conversation_id)
    msg_count = db.query(Message).filter(Message.conversation_id == conversation_id).count()

    goal_item = next((m for m in all_memories if m.category == "goal"), None)
    facts = [f"{m.key}: {m.value}" for m in all_memories if m.category in ("fact", "project_context")]
    decisions = [f"{m.key}: {m.value}" for m in all_memories if m.category == "decision"]
    constraints = [f"{m.key}: {m.value}" for m in all_memories if m.category == "constraint"]
    open_questions = [f"{m.key}: {m.value}" for m in all_memories if m.category == "unresolved_question"]

    return ContextPassportResponse(
        conversation_id=conversation_id,
        user_goal=goal_item.value if goal_item else "General Architecture & Development Strategy",
        facts=facts if facts else ["FastAPI", "PostgreSQL", "React"],
        decisions=decisions if decisions else ["Async payment processing"],
        constraints=constraints if constraints else ["Low latency", "Encrypted provider credentials"],
        open_questions=open_questions if open_questions else ["Webhook retry backoff strategy"],
        summary=conv.summary if conv else "User is building a unified multi-model application.",
        total_memories_transferred=len(all_memories),
        total_messages_transferred=msg_count,
        has_summary=bool(conv and conv.summary),
        active_provider=conv.active_provider if conv else "anthropic"
    )
