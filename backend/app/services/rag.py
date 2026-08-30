import re
import datetime
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.memory import Memory
from app.models.message import Message
from app.models.file import File
from app.schemas.context import ContextPackage

# Comprehensive RAG Knowledge Base containing 80+ Grounded QA Pairs
RAG_KNOWLEDGE_BASE: List[Dict[str, str]] = [
    {"topic": "artificial_intelligence", "keywords": "artificial intelligence ai computing human-like language perception reasoning decision", "response": "Artificial intelligence is the field of computing focused on creating systems that can perform tasks that normally require human-like abilities such as perception, language understanding, reasoning, learning, and decision-making."},
    {"topic": "machine_learning", "keywords": "machine learning ml branch data predictions classifications programming", "response": "Machine learning is a branch of artificial intelligence in which computer systems learn patterns from data and use those patterns to make predictions, classifications, or decisions instead of being explicitly programmed for every case."},
    {"topic": "deep_learning", "keywords": "deep learning neural networks layers complex patterns", "response": "Deep learning is a type of machine learning that uses neural networks with multiple layers to learn increasingly complex patterns from data."},
    {"topic": "neural_network", "keywords": "neural network computational model interconnected processing units layers", "response": "A neural network is a computational model made of interconnected processing units, often organized into layers, that learns relationships between inputs and outputs from examples."},
    {"topic": "generative_ai", "keywords": "generative ai create text images audio video code", "response": "Generative AI refers to AI systems that create new content such as text, images, audio, video, or code based on patterns learned from data."},
    {"topic": "llm", "keywords": "llm large language model text predict generate summarizing", "response": "A large language model is a machine-learning model trained on large amounts of text to predict and generate language and perform tasks such as answering questions, summarizing, transforming text, and generating code."},
    {"topic": "rag", "keywords": "rag retrieval augmented generation information retrieval language model grounded answer", "response": "Retrieval-augmented generation combines information retrieval with text generation. A system first retrieves relevant information from a knowledge source and then gives that information to a language model to help produce a grounded answer."},
    {"topic": "api", "keywords": "api application programming interface software components communicate", "response": "An application programming interface is a defined way for software components to communicate with each other."},
    {"topic": "http", "keywords": "http application layer protocol resources messages clients servers web", "response": "HTTP is an application-layer protocol used to transfer resources and messages between clients and servers on the web."},
    {"topic": "database", "keywords": "database system storing retrieving structured unstructured information", "response": "A database is an organized system for storing and retrieving structured or unstructured information."},
    {"topic": "sql", "keywords": "sql language define query manipulate manage relational databases", "response": "SQL is a language used to define, query, manipulate, and manage data in relational databases."},
    {"topic": "python", "keywords": "python programming language syntax web development automation data science machine learning", "response": "Python is a general-purpose programming language known for readable syntax and widely used in web development, automation, data science, machine learning, and artificial intelligence."},
    {"topic": "git", "keywords": "git distributed version control system track changes coordinate development", "response": "Git is a distributed version-control system used to track changes to files and coordinate software development."},
    {"topic": "cloud_computing", "keywords": "cloud computing resources servers storage networking software network", "response": "Cloud computing is the delivery of computing resources such as servers, storage, networking, and software over a network on demand."},
    {"topic": "cybersecurity", "keywords": "cybersecurity protecting systems networks applications data unauthorized misuse attack", "response": "Cybersecurity is the practice of protecting computer systems, networks, applications, and data from unauthorized access, misuse, disruption, or attack."},
    {"topic": "encryption", "keywords": "encryption readable encoded form key recover original information", "response": "Encryption transforms readable information into an encoded form so that only an authorized party with the appropriate key can recover the original information."},
    {"topic": "computer_virus", "keywords": "computer virus malicious software replicate programs harmful behavior", "response": "A computer virus is malicious software that can replicate by attaching itself to other files or programs and can cause unwanted or harmful behavior."},
    {"topic": "internet", "keywords": "internet global network interconnected computer networks tcp ip", "response": "The Internet is a global network of interconnected computer networks that communicate using standardized protocols such as TCP/IP."},
    {"topic": "tcp_ip", "keywords": "tcp ip networking protocols internet addressing routing reliable delivery", "response": "TCP/IP is the family of networking protocols used to communicate across the Internet. IP handles addressing and routing, while TCP provides reliable, ordered delivery for connections that use it."},
    {"topic": "cpu", "keywords": "cpu central processing unit primary processor execute instructions calculations", "response": "A central processing unit is the primary general-purpose processor in a computer that executes program instructions and performs calculations and control operations."},
    {"topic": "ram", "keywords": "ram random access memory temporary memory active programs", "response": "Random access memory is fast, temporary computer memory used to hold data and instructions that active programs need."},
    {"topic": "operating_system", "keywords": "operating system software manages hardware resources interfaces applications", "response": "An operating system is system software that manages hardware resources and provides services and interfaces for applications."},
    {"topic": "mathematics", "keywords": "mathematics quantities structures patterns relationships space logical methods", "response": "Mathematics is the study of quantities, structures, patterns, relationships, space, and change using logical and formal methods."},
    {"topic": "calculus", "keywords": "calculus change rates accumulation limits derivatives integrals", "response": "Calculus is a branch of mathematics concerned with change, rates of change, accumulation, limits, derivatives, and integrals."},
    {"topic": "probability", "keywords": "probability mathematical framework describing quantifying uncertainty", "response": "Probability is a mathematical framework for describing and quantifying uncertainty."},
    {"topic": "statistics", "keywords": "statistics collecting analyzing interpreting communicating data", "response": "Statistics is the field concerned with collecting, analyzing, interpreting, and communicating data."},
    {"topic": "physics", "keywords": "physics matter energy motion forces fields space time interact", "response": "Physics is the study of matter, energy, motion, forces, fields, space, and time and the laws describing how they interact."},
    {"topic": "chemistry", "keywords": "chemistry matter properties structure composition transformations", "response": "Chemistry is the study of matter, its properties, structure, composition, and the transformations it undergoes."},
    {"topic": "biology", "keywords": "biology living organisms processes sustain life", "response": "Biology is the study of living organisms and the processes that sustain life."},
    {"topic": "dna", "keywords": "dna stores genetic information living organisms viruses molecule", "response": "DNA is the molecule that stores genetic information in living organisms and many viruses."},
    {"topic": "photosynthesis", "keywords": "photosynthesis plants light energy convert carbon dioxide water oxygen", "response": "Photosynthesis is the process by which plants, algae, and some microorganisms use light energy to convert carbon dioxide and water into chemical energy, releasing oxygen in oxygenic photosynthesis."},
    {"topic": "gravity", "keywords": "gravity interaction mass energy cause bodies attract one another", "response": "Gravity is the interaction associated with mass and energy that causes bodies to attract one another."},
    {"topic": "solar_system", "keywords": "solar system sun planets dwarf moons asteroids comets", "response": "The solar system consists of the Sun and the objects gravitationally bound to it, including planets, dwarf planets, moons, asteroids, comets, and other smaller bodies."},
    {"topic": "black_hole", "keywords": "black hole spacetime gravity strong event horizon light escape", "response": "A black hole is a region of spacetime where gravity is so strong that within its event horizon nothing, including light, can escape outward."},
    {"topic": "climate_change", "keywords": "climate change earth patterns human activities greenhouse gas", "response": "Climate change refers to long-term changes in Earth's climate patterns. Modern climate change is primarily driven by human activities that increase greenhouse-gas concentrations."},
    {"topic": "renewable_energy", "keywords": "renewable energy sunlight wind flowing water geothermal resources", "response": "Renewable energy comes from naturally replenishing sources such as sunlight, wind, flowing water, geothermal heat, and sustainably managed biological resources."},
    {"topic": "gdp", "keywords": "gdp gross domestic product monetary value goods services economy", "response": "Gross domestic product is the monetary value of final goods and services produced within an economy during a specified period."},
    {"topic": "inflation", "keywords": "inflation sustained increase prices goods services purchasing power", "response": "Inflation is a sustained increase in the general level of prices of goods and services over time, which reduces the purchasing power of money."},
    {"topic": "recession", "keywords": "recession decline economic activity production employment income spending", "response": "A recession is a significant, broad-based decline in economic activity lasting long enough to affect production, employment, income, and spending."},
    {"topic": "stock", "keywords": "stock represents ownership interest company", "response": "A stock represents an ownership interest in a company."},
    {"topic": "bond", "keywords": "bond debt instrument issuer borrows money interest principal", "response": "A bond is a debt instrument through which an issuer borrows money from investors and generally agrees to pay interest and repay principal according to specified terms."},
    {"topic": "supply_and_demand", "keywords": "supply demand sellers offer buyers purchase prices", "response": "Supply describes how much sellers are willing to offer at different prices, while demand describes how much buyers are willing and able to purchase at different prices."},
    {"topic": "democracy", "keywords": "democracy government political authority derived people elections", "response": "Democracy is a form of government in which political authority is derived from the people, typically through participation and elections."},
    {"topic": "constitution_of_india", "keywords": "constitution india supreme legal framework structure powers government rights", "response": "The Constitution of India is the supreme legal framework of India. It establishes the structure and powers of government and sets out fundamental rights, directive principles, and other constitutional provisions."},
    {"topic": "prime_minister_of_india", "keywords": "prime minister india narendra modi officeholder government", "response": "As of August 2026, Narendra Modi is the Prime Minister of India. He began his third term on 9 June 2024. For current officeholder questions, verify against an authoritative current government source because political positions can change."},
    {"topic": "capital_of_india", "keywords": "capital india new delhi", "response": "New Delhi is the capital of India."},
    {"topic": "currency_of_india", "keywords": "currency india indian rupee", "response": "The Indian rupee is the currency of India."},
    {"topic": "states_in_india", "keywords": "states union territories india 28 8", "response": "India has 28 states and 8 union territories."},
    {"topic": "parliament_of_india", "keywords": "parliament india Union legislature president rajya sabha lok sabha", "response": "The Parliament of India is the Union legislature and consists of the President and two houses: the Rajya Sabha and the Lok Sabha."},
    {"topic": "lok_sabha", "keywords": "lok sabha lower house parliament india elected representatives", "response": "The Lok Sabha is the lower house of the Parliament of India and is composed of directly elected representatives."},
    {"topic": "rajya_sabha", "keywords": "rajya sabha upper house parliament india states union territories", "response": "The Rajya Sabha is the upper house of the Parliament of India and represents the states and union territories."},
    {"topic": "president_of_india", "keywords": "president india constitutional head union officeholder", "response": "The President of India is the constitutional head of the Union. The current officeholder should be verified from an authoritative current government source."},
    {"topic": "united_nations", "keywords": "united nations international organization peace security human rights", "response": "The United Nations is an international organization founded in 1945 whose purposes include maintaining international peace and security, developing international cooperation, and promoting human rights."},
    {"topic": "european_union", "keywords": "european union political economic member states trade law", "response": "The European Union is a political and economic union of European member states that cooperate in areas including trade, law, economic policy, and other common policies."},
    {"topic": "geography", "keywords": "geography places environments physical processes human activities relationships", "response": "Geography is the study of Earth's places, environments, physical processes, human activities, and the relationships between people and places."},
    {"topic": "continent", "keywords": "continent continuous defined landmasses earth", "response": "A continent is one of the major continuous or conventionally defined landmasses of Earth."},
    {"topic": "country", "keywords": "country territorial political entity territory government population", "response": "A country is a territorial and political entity with a defined territory, government, and population, although the precise legal and political meaning can vary by context."},
    {"topic": "history", "keywords": "history study past events human societies evidence documents artifacts", "response": "History is the study and interpretation of past events and human societies using evidence such as documents, artifacts, oral traditions, and other sources."},
    {"topic": "industrial_revolution", "keywords": "industrial revolution technological economic social transformation mechanization factories", "response": "The Industrial Revolution was a period of major technological, economic, and social transformation beginning in the eighteenth century, characterized by mechanization, factories, new energy sources, and large-scale changes in production."},
    {"topic": "renaissance", "keywords": "renaissance intellectual artistic cultural European classical learning", "response": "The Renaissance was a period of major intellectual, artistic, and cultural development in Europe, traditionally associated with renewed interest in classical learning and beginning roughly in the fourteenth century."},
    {"topic": "scientific_method", "keywords": "scientific method systematic investigation observation hypothesis testing analysis", "response": "The scientific method is a systematic approach to investigating questions through observation, hypothesis formation, testing, analysis, and revision based on evidence."},
    {"topic": "experiment", "keywords": "experiment controlled investigation test hypothesis factor affects outcome", "response": "An experiment is a controlled investigation designed to test a hypothesis or determine how changing one factor affects an outcome."},
    {"topic": "hypothesis", "keywords": "hypothesis testable proposed explanation prediction phenomenon", "response": "A hypothesis is a testable proposed explanation or prediction about a phenomenon."},
    {"topic": "critical_thinking", "keywords": "critical thinking evaluating evidence assumptions reasoning conclusions claim", "response": "Critical thinking is the process of carefully evaluating evidence, assumptions, reasoning, and conclusions before accepting a claim."},
    {"topic": "fact", "keywords": "fact statement supported verified reliable evidence", "response": "A fact is a statement that can be supported or verified by reliable evidence."},
    {"topic": "opinion", "keywords": "opinion judgment belief interpretation preference factual statement", "response": "An opinion is a person's judgment, belief, interpretation, or preference rather than a directly verifiable factual statement."},
    {"topic": "plagiarism", "keywords": "plagiarism presenting words ideas creative work attribution", "response": "Plagiarism is presenting another person's words, ideas, creative work, or other intellectual contribution as one's own without appropriate attribution."},
    {"topic": "algorithm", "keywords": "algorithm finite sequence steps solve problem computation", "response": "An algorithm is a finite, well-defined sequence of steps used to solve a problem or perform a computation."},
    {"topic": "data_structure", "keywords": "data structure organizing storing data access insertion deletion search", "response": "A data structure is a way of organizing and storing data so that operations such as access, insertion, deletion, and search can be performed efficiently."},
    {"topic": "object_oriented_programming", "keywords": "object oriented programming paradigm software objects data behavior", "response": "Object-oriented programming is a programming paradigm that organizes software around objects containing data and behavior."},
    {"topic": "recursion", "keywords": "recursion function procedure calls itself smaller version problem", "response": "Recursion is a technique in which a function or procedure calls itself on a smaller or simpler version of a problem until a base condition is reached."},
    {"topic": "compiler", "keywords": "compiler translates source code machine code intermediate executable", "response": "A compiler translates source code written in a programming language into another form, often machine code or intermediate code, that can be executed or further processed."},
    {"topic": "interpreter", "keywords": "interpreter executes evaluates program instructions runtime system", "response": "An interpreter executes or evaluates program instructions through a runtime system rather than first producing a standalone machine-code executable in the traditional compiler sense."},
    {"topic": "machine_learning_training", "keywords": "training adjusting parameters data patterns task", "response": "Training is the process of adjusting a machine-learning model's parameters using data so that it learns patterns associated with a task."},
    {"topic": "inference_in_ai", "keywords": "inference prediction classification representation response input", "response": "Inference is the process of using a trained model to generate a prediction, classification, representation, or response for new input."},
    {"topic": "supervised_learning", "keywords": "supervised learning trains model examples target labels outcomes", "response": "Supervised learning trains a model using examples that include target labels or outcomes."},
    {"topic": "unsupervised_learning", "keywords": "unsupervised learning patterns structures target labels", "response": "Unsupervised learning finds patterns or structures in data without predefined target labels."},
    {"topic": "reinforcement_learning", "keywords": "reinforcement learning interaction environment feedback rewards penalties", "response": "Reinforcement learning is a machine-learning approach in which an agent learns through interaction with an environment and feedback such as rewards or penalties."},
    {"topic": "overfitting", "keywords": "overfitting model learns training data noise performs poorly new data", "response": "Overfitting occurs when a model learns training data too closely, including noise or accidental patterns, and consequently performs poorly on new data."},
    {"topic": "underfitting", "keywords": "underfitting model simple insufficiently trained capture patterns", "response": "Underfitting occurs when a model is too simple or insufficiently trained to capture important patterns in the data."},
    {"topic": "transformer_model", "keywords": "transformer neural network architecture attention mechanisms sequence processing", "response": "A transformer is a neural-network architecture based primarily on attention mechanisms that is widely used for language and other sequence-processing tasks."},
    {"topic": "attention_transformer", "keywords": "attention mechanism weigh relationships elements input sequence representations", "response": "Attention is a mechanism that allows a model to weigh relationships between elements of an input sequence when computing representations."},
    {"topic": "token_llm", "keywords": "token unit text processed language model word punctuation fragment", "response": "A token is a unit of text processed by a language model. Depending on the tokenizer, a token may represent a word, part of a word, punctuation, or another text fragment."},
    {"topic": "vector_embedding", "keywords": "vector embedding numerical representation text semantic similarity", "response": "An embedding is a numerical vector representation of an item such as text, designed so that useful relationships such as semantic similarity can be measured mathematically."},
    {"topic": "vector_database", "keywords": "vector database stores representations similarity search rag generation", "response": "A vector database stores vector representations and supports similarity search, often for applications such as retrieval-augmented generation and recommendation systems."}
]

def query_rag_engine(db: Session, conversation_id: str, prompt: str, context_package: ContextPackage, web_results: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Learns from live web search results, user chat history, memories, uploaded files, and grounded QA dataset.
    """
    prompt_clean = prompt.lower().strip()
    words = set(re.findall(r'\w+', prompt_clean))

    # 1. Gather retrieved memories & files context
    memory_context_lines = []
    if context_package.user_goal:
        memory_context_lines.append(f"• Goal: {context_package.user_goal}")
    for m in context_package.relevant_memories:
        memory_context_lines.append(f"• [{m.category.upper()}] {m.key}: {m.value}")
    for f in context_package.relevant_files:
        memory_context_lines.append(f"• [FILE] {f.filename}: {f.content_summary}")

    # 2. Prioritize Live Web Search Results if present
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

    # 3. Learn from past conversation messages in this thread
    chat_learned_facts = []
    if db and conversation_id:
        past_messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
        for msg in past_messages[:-1]:
            if msg.sender_role == "assistant" and "RAG" not in msg.content:
                sentences = [s.strip() for s in msg.content.split('\n') if len(s.strip()) > 15]
                for s in sentences[:3]:
                    chat_learned_facts.append(s)

    # 4. Match knowledge base topic (Grounded QA dataset)
    matched_kb: Optional[str] = None
    best_score = 0

    for kb in RAG_KNOWLEDGE_BASE:
        kb_words = set(kb["keywords"].split())
        score = len(words.intersection(kb_words))
        if score >= 1 and score > best_score:
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
