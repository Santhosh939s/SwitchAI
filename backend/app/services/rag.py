import re
import datetime
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.memory import Memory
from app.models.message import Message
from app.models.file import File
from app.schemas.context import ContextPackage

ACRONYM_MAP = {
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "db": "database",
    "api": "application programming interface",
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "nlp": "natural language processing",
    "dl": "deep learning"
}

# Comprehensive Multi-Domain RAG Knowledge Base Architecture
RAG_KNOWLEDGE_BASE: List[Dict[str, str]] = [
    {"topic": "greeting", "keywords": "hello hi hey greetings", "response": "Hello! I am **SwitchAI RAG Engine** — your persistent, provider-independent AI assistant. How can I assist you with your project architecture or code today?"},
    {"topic": "science", "keywords": "science systematic study natural physical world empirical observation evidence hypothesis experiment", "response": "Science is the systematic enterprise that builds and organizes knowledge in the form of testable explanations and predictions about the physical and natural universe using empirical observation, experimentation, and evidence."},
    {"topic": "technology", "keywords": "technology practical application scientific knowledge engineering tools systems innovation", "response": "Technology is the application of scientific knowledge, engineering principles, and technical methods for practical purposes in industry, communication, computing, and everyday life."},
    {"topic": "artificial_intelligence", "keywords": "artificial intelligence ai computing human-like language perception reasoning decision", "response": "Artificial intelligence is the field of computing focused on creating systems that can perform tasks that normally require human-like abilities such as perception, language understanding, reasoning, learning, and decision-making."},
    {"topic": "machine_learning", "keywords": "machine learning ml branch data predictions classifications programming", "response": "Machine learning is a branch of artificial intelligence in which computer systems learn patterns from data and use those patterns to make predictions, classifications, or decisions instead of being explicitly programmed for every case."},
    {"topic": "deep_learning", "keywords": "deep learning neural networks layers complex patterns", "response": "Deep learning is a type of machine learning that uses neural networks with multiple layers to learn increasingly complex patterns from data."},
    {"topic": "neural_network", "keywords": "neural network computational model interconnected processing units layers", "response": "A neural network is a computational model made of interconnected processing units, often organized into layers, that learns relationships between inputs and outputs from examples."},
    {"topic": "generative_ai", "keywords": "generative ai create text images audio video code", "response": "Generative AI refers to AI systems that create new content such as text, images, audio, video, or code based on patterns learned from data."},
    {"topic": "llm", "keywords": "llm large language model text predict generate summarizing", "response": "A large language model is a machine-learning model trained on large amounts of text to predict and generate language and perform tasks such as answering questions, summarizing, transforming text, and generating code."},
    {"topic": "rag", "keywords": "rag retrieval augmented generation information retrieval language model grounded answer", "response": "Retrieval-augmented generation combines information retrieval with text generation. A system first retrieves relevant information from a knowledge source and then gives that information to a language model to help produce a grounded answer."},
    {"topic": "computer_science", "keywords": "computer science computation information processing data structures algorithms architecture", "response": "Computer science is the study of computation, information processing, data structures, algorithms, hardware architecture, and software systems."},
    {"topic": "algorithm", "keywords": "algorithm finite sequence steps solve problem computation", "response": "An algorithm is a finite, well-defined sequence of steps used to solve a problem or perform a computation."},
    {"topic": "data_structure", "keywords": "data structure organizing storing data access insertion deletion search", "response": "A data structure is a way of organizing and storing data so that operations such as access, insertion, deletion, and search can be performed efficiently."},
    {"topic": "compiler", "keywords": "compiler translates source code machine code intermediate executable", "response": "A compiler translates source code written in a programming language into another form, often machine code or intermediate code, that can be executed or further processed."},
    {"topic": "operating_system", "keywords": "operating system software manages hardware resources interfaces applications", "response": "An operating system is system software that manages hardware resources and provides services and interfaces for applications."},
    {"topic": "database", "keywords": "database system storing retrieving structured unstructured information", "response": "A database is an organized system for storing and retrieving structured or unstructured information."},
    {"topic": "programming", "keywords": "programming coding software development logic instructions syntax paradigm", "response": "Programming is the process of writing, testing, debugging, and maintaining the source code of computer programs to implement specific computational tasks."},
    {"topic": "python", "keywords": "python programming language syntax web development automation data science machine learning", "response": "Python is a general-purpose programming language known for readable syntax and widely used in web development, automation, data science, machine learning, and artificial intelligence."},
    {"topic": "object_oriented_programming", "keywords": "object oriented programming paradigm software objects data behavior", "response": "Object-oriented programming is a programming paradigm that organizes software around objects containing data and behavior."},
    {"topic": "recursion", "keywords": "recursion function procedure calls itself smaller version problem", "response": "Recursion is a technique in which a function or procedure calls itself on a smaller or simpler version of a problem until a base condition is reached."},
    {"topic": "mathematics", "keywords": "mathematics quantities structures patterns relationships space logical methods", "response": "Mathematics is the study of quantities, structures, patterns, relationships, space, and change using logical and formal methods."},
    {"topic": "calculus", "keywords": "calculus change rates accumulation limits derivatives integrals", "response": "Calculus is a branch of mathematics concerned with change, rates of change, accumulation, limits, derivatives, and integrals."},
    {"topic": "probability", "keywords": "probability mathematical framework describing quantifying uncertainty", "response": "Probability is a mathematical framework for describing and quantifying uncertainty."},
    {"topic": "statistics", "keywords": "statistics collecting analyzing interpreting communicating data", "response": "Statistics is the field concerned with collecting, analyzing, interpreting, and communicating data."},
    {"topic": "physics", "keywords": "physics matter energy motion forces fields space time interact", "response": "Physics is the study of matter, energy, motion, forces, fields, space, and time and the laws describing how they interact."},
    {"topic": "gravity", "keywords": "gravity interaction mass energy cause bodies attract one another", "response": "Gravity is the interaction associated with mass and energy that causes bodies to attract one another."},
    {"topic": "chemistry", "keywords": "chemistry matter properties structure composition transformations molecules reactions", "response": "Chemistry is the study of matter, its properties, structure, composition, and the transformations it undergoes during chemical reactions."},
    {"topic": "biology", "keywords": "biology living organisms processes sustain life cells genetics evolution", "response": "Biology is the study of living organisms and the processes that sustain life, including cell biology, genetics, physiology, and evolution."},
    {"topic": "dna", "keywords": "dna stores genetic information living organisms viruses molecule", "response": "DNA is the molecule that stores genetic information in living organisms and many viruses."},
    {"topic": "photosynthesis", "keywords": "photosynthesis plants light energy convert carbon dioxide water oxygen", "response": "Photosynthesis is the process by which plants, algae, and some microorganisms use light energy to convert carbon dioxide and water into chemical energy, releasing oxygen in oxygenic photosynthesis."},
    {"topic": "medicine", "keywords": "medicine health healthcare clinical diagnosis treatment disease pathology immunology pharmacology", "response": "Medicine is the science and practice of establishing diagnosis, prognosis, treatment, and prevention of disease, injury, and health disorders."},
    {"topic": "history", "keywords": "history study past events human societies evidence documents artifacts", "response": "History is the study and interpretation of past events and human societies using evidence such as documents, artifacts, oral traditions, and other sources."},
    {"topic": "industrial_revolution", "keywords": "industrial revolution technological economic social transformation mechanization factories", "response": "The Industrial Revolution was a period of major technological, economic, and social transformation beginning in the eighteenth century, characterized by mechanization, factories, new energy sources, and large-scale changes in production."},
    {"topic": "geography", "keywords": "geography places environments physical processes human activities relationships continents maps", "response": "Geography is the study of Earth's places, environments, physical processes, human activities, and the relationships between people and places."},
    {"topic": "world_relations", "keywords": "world international relations geopolitics united nations european union diplomacy global", "response": "World affairs and international relations involve the political, economic, diplomatic, and security interactions between nations, international bodies (such as the UN and EU), and non-state actors."},
    {"topic": "india", "keywords": "india constitution indian government new delhi parliament lok sabha rajya sabha states", "response": "India is a sovereign democratic republic in South Asia with 28 states and 8 union territories, governed under the Constitution of India with its capital at New Delhi."},
    {"topic": "government_civics", "keywords": "government civics democracy political authority elections rights constitution laws separation powers", "response": "Government and civics examine political systems, constitutional law, public administration, fundamental rights, and civic participation in democratic societies."},
    {"topic": "economics", "keywords": "economics macroeconomics microeconomics gdp inflation recession production distribution consumption", "response": "Economics is the social science that studies the production, distribution, and consumption of goods and services, analyzing macroeconomics (GDP, inflation, growth) and microeconomics."},
    {"topic": "business", "keywords": "business enterprise corporate management marketing operations strategy commerce organization", "response": "Business encompasses the activities, organizational structures, strategies, marketing, operations, and management involved in producing and selling goods or services for value."},
    {"topic": "finance", "keywords": "finance investments stocks bonds interest rates capital markets corporate banking", "response": "Finance is the study and management of money, investments, banking, assets, liabilities, stocks, bonds, and capital allocation."},
    {"topic": "environment", "keywords": "environment ecology climate change renewable energy biodiversity sustainability conservation", "response": "Environmental science studies ecological systems, climate change, biodiversity, sustainability, and renewable energy resources."},
    {"topic": "space", "keywords": "space astronomy solar system sun planets black hole astrophysics universe exploration", "response": "Space science and astronomy study the universe beyond Earth's atmosphere, including the solar system, stars, galaxies, black holes, and cosmological phenomena."},
    {"topic": "engineering", "keywords": "engineering mechanical electrical civil systems software design infrastructure structural", "response": "Engineering is the application of scientific, economic, social, and practical knowledge to invent, innovate, design, build, maintain, research, and improve structures, machines, tools, systems, components, materials, processes, solutions, and organizations."},
    {"topic": "education", "keywords": "education learning pedagogy teaching research academic scientific method critical thinking", "response": "Education is the discipline concerned with methods of teaching and learning in schools or school-like environments as opposed to various nonformal and informal means of socialization."},
    {"topic": "literature", "keywords": "literature prose poetry drama novels narrative creative writing analysis themes", "response": "Literature comprises written works of artistic, intellectual, or cultural value, including prose, poetry, drama, and critical narrative analysis."},
    {"topic": "language", "keywords": "language linguistics syntax grammar semantics vocabulary communication etymology", "response": "Language is a structured system of communication that includes syntax, grammar, semantics, phonetics, and vocabulary used by humans to express thought."},
    {"topic": "arts_and_culture", "keywords": "arts culture aesthetics visual performing music heritage painting architecture sculpture", "response": "Arts and culture encompass creative expressions including visual arts, music, dance, theater, architecture, aesthetics, and intangible cultural heritage."},
    {"topic": "sports", "keywords": "sports athletics physical competition training fitness rules tournaments kinesiology", "response": "Sports cover organized physical activities, competitive athletics, kinesiology, fitness training, rules of play, and athletic tournaments."},
    {"topic": "everyday_life", "keywords": "everyday life productivity time management communication practical problem solving daily habits", "response": "Everyday life skills focus on practical problem-solving, effective communication, time management, decision-making, and daily habits for personal and professional effectiveness."},
    {"topic": "general_knowledge", "keywords": "general knowledge encyclopedic facts reference information trivias standards world facts", "response": "General knowledge represents a broad collection of verified factual information across diverse human disciplines, history, geography, science, culture, and foundational concepts."}
]

def query_rag_engine(db: Session, conversation_id: str, prompt: str, context_package: ContextPackage, web_results: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Learns from live web search results, user chat history, memories, uploaded files, and 28-domain RAG dataset.
    """
    prompt_clean = prompt.lower().strip()
    words = set(re.findall(r'\w+', prompt_clean))

    # Acronym expansion
    expanded_prompt = prompt_clean
    for ac, full in ACRONYM_MAP.items():
        if ac in words:
            expanded_prompt += f" {full}"
    words = set(re.findall(r'\w+', expanded_prompt.lower()))

    # 1. Gather retrieved memories & files context
    memory_context_lines = []
    if context_package.user_goal:
        memory_context_lines.append(f"• Goal: {context_package.user_goal}")
    for m in context_package.relevant_memories:
        memory_context_lines.append(f"• [{m.category.upper()}] {m.key}: {m.value}")
    for f in context_package.relevant_files:
        memory_context_lines.append(f"• [FILE] {f.filename}: {f.content_summary}")

    # 2. Prioritize Live Web Search Results if present, or auto-fetch if empty and prompt needs current info
    if not web_results:
        from app.services.search import search_web_ddg
        web_results = search_web_ddg(prompt, max_results=3)

    if web_results and len(web_results) > 0:
        header = "🌐 **[SwitchAI Live Web Search & RAG Engine]**\n*Retrieved live search results & parsed facts for your query.*\n\n"
        body = f"Here are the latest live web search answers for: **\"{prompt}\"**\n\n"
        for i, item in enumerate(web_results, 1):
            title = item.get("title", "Web Fact").strip()
            snippet = item.get("snippet", "").strip()
            url = item.get("url", "#").strip()
            body += f"### {i}. [{title}]({url})\n{snippet}\n\n"

        if memory_context_lines:
            body += "---\n### Retained Project Context:\n" + "\n".join(memory_context_lines)

        return header + body

    # 3. Learn from past conversation messages (Filter out error logs)
    chat_learned_facts = []
    if db and conversation_id:
        past_messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
        for msg in past_messages[:-1]:
            if msg.sender_role == "assistant" and "RAG" not in msg.content and "Error" not in msg.content and "failed" not in msg.content:
                sentences = [s.strip() for s in msg.content.split('\n') if len(s.strip()) > 15]
                for s in sentences[:3]:
                    chat_learned_facts.append(s)

    # 4. Match knowledge base topic
    matched_kb: Optional[str] = None
    best_score = 0
    min_threshold = 1 if len(prompt_clean.split()) <= 2 else 2

    for kb in RAG_KNOWLEDGE_BASE:
        kb_words = set(kb["keywords"].split())
        score = len(words.intersection(kb_words))
        if score >= min_threshold and score > best_score:
            best_score = score
            matched_kb = kb["response"]

    offline_header = "🤖 **[SwitchAI Offline RAG Knowledge Engine]**\n*Cloud APIs temporarily unavailable/exhausted. Generating response from local RAG Knowledge Base & Shared Memory.*\n\n"

    if matched_kb:
        body = matched_kb
    else:
        body = f"### Response for: **\"{prompt}\"**\n\n"
        if memory_context_lines or chat_learned_facts:
            body += "Based on what I learned from your project context and chat history:\n"
        else:
            body += "I received your query. You can connect new provider API keys in **Settings → Providers** or run a local AI server to resume full LLM generation.\n"

    # Attach learned chat facts if relevant
    if chat_learned_facts and not matched_kb:
        body += "\n### Learned Chat History Insights:\n"
        for fact in chat_learned_facts[:3]:
            body += f"> {fact}\n"

    # Attach retained shared memory context
    if memory_context_lines:
        body += "\n---\n### Retained Shared Memory Context:\n" + "\n".join(memory_context_lines)

    return offline_header + body
