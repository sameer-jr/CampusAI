import os
import json
import streamlit as st

from dotenv import load_dotenv

from google import genai
from google.genai import types

from retriever import retrieve


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="CampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

MODEL_NAME = os.getenv(
    "GEMINI_MODEL"
)


if not API_KEY:

    st.error(
        "GEMINI_API_KEY is missing."
    )

    st.stop()


if not MODEL_NAME:

    st.error(
        "GEMINI_MODEL is missing from .env."
    )

    st.stop()


client = genai.Client(
    api_key=API_KEY
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


if "pending_question" not in st.session_state:

    st.session_state.pending_question = None


# ============================================================
# UI
# ============================================================

st.html("""
<style>

html,
body,
.stApp {

    background: #ffffff !important;

    color: #202123 !important;
}


html,
body,
.stApp {

    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Inter,
        Arial,
        sans-serif !important;
}


.block-container {

    max-width: 850px !important;

    padding-top: 18px !important;

    padding-bottom: 140px !important;
}


#MainMenu,
footer {

    visibility: hidden;
}


header[data-testid="stHeader"] {

    background: transparent;
}


section[data-testid="stSidebar"] {

    background: #f7f7f8 !important;

    border-right:
        1px solid #ececec;
}


.brand {

    display: flex;

    align-items: center;

    gap: 10px;

    margin-bottom: 20px;
}


.brand-logo {

    width: 36px;

    height: 36px;

    border-radius: 10px;

    display: flex;

    align-items: center;

    justify-content: center;

    background: #111827;

    color: white;

    font-size: 13px;

    font-weight: 800;
}


.brand-name {

    color: #202123;

    font-weight: 700;

    font-size: 16px;
}


.brand-small {

    color: #969696;

    font-size: 11px;
}


.side-title {

    margin-top: 25px;

    margin-bottom: 8px;

    color: #999;

    font-size: 10px;

    text-transform: uppercase;

    letter-spacing: .6px;

    font-weight: 700;
}


.side-text {

    color: #636363;

    font-size: 12px;

    line-height: 1.8;
}


.app-header {

    display: flex;

    justify-content: space-between;

    align-items: center;

    height: 44px;

    border-bottom:
        1px solid #eeeeee;
}


.app-title {

    font-weight: 650;

    font-size: 15px;

    color: #202123;
}


.app-status {

    font-size: 11px;

    color: #969696;
}


.home {

    margin:
        90px auto 35px auto;

    text-align: center;
}


.home-logo {

    width: 54px;

    height: 54px;

    margin:
        auto auto 20px auto;

    border-radius: 16px;

    background: #111827;

    color: #ffffff;

    display: flex;

    align-items: center;

    justify-content: center;

    font-weight: 800;
}


.home-title {

    color: #202123;

    font-size: 30px;

    font-weight: 650;

    letter-spacing: -0.7px;
}


.home-text {

    max-width: 520px;

    margin:
        10px auto 0 auto;

    color: #6c6c6c;

    font-size: 14px;

    line-height: 1.7;
}


.try-label {

    text-align: center;

    color: #999;

    font-size: 11px;

    margin-bottom: 10px;
}


.st-key-question_library button,
.st-key-question_assignment button,
.st-key-question_class button,
.st-key-question_it button {

    min-height: 62px !important;

    border-radius: 13px !important;

    border:
        1px solid #e3e3e3 !important;

    background:
        white !important;

    color:
        #343434 !important;

    font-size:
        13px !important;

    font-weight:
        500 !important;

    box-shadow:
        none !important;
}


.st-key-question_library button:hover,
.st-key-question_assignment button:hover,
.st-key-question_class button:hover,
.st-key-question_it button:hover {

    background:
        #f5f5f5 !important;
}


[data-testid="stChatMessage"] {

    background:
        transparent !important;

    border:
        none !important;

    padding:
        19px 4px !important;

    box-shadow:
        none !important;
}


[data-testid="stChatMessage"]
+
[data-testid="stChatMessage"] {

    border-top:
        1px solid #f0f0f0 !important;
}


[data-testid="stChatMessage"] p {

    color:
        #292929 !important;

    font-size:
        14.5px !important;

    line-height:
        1.75 !important;
}


[data-testid="stBottom"] {

    background:

        linear-gradient(
            to top,
            #ffffff 78%,
            rgba(255,255,255,0)
        )

        !important;
}


[data-testid="stChatInput"] {

    max-width:
        810px;

    margin:
        auto;

    background:
        #f4f4f4 !important;

    border:
        1px solid #dedede !important;

    border-radius:
        22px !important;

    box-shadow:
        0 2px 7px rgba(0,0,0,.05) !important;
}


[data-testid="stChatInput"] textarea {

    color:
        #202123 !important;
}


[data-testid="stChatInputSubmitButton"] {

    background:
        #111827 !important;

    color:
        white !important;

    border-radius:
        50% !important;
}


.disclaimer {

    margin-top: 30px;

    text-align: center;

    color: #aaa;

    font-size: 10.5px;

    line-height: 1.5;
}


</style>
""")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html("""
    <div class="brand">

        <div class="brand-logo">
            CA
        </div>

        <div>

            <div class="brand-name">
                CampusAI
            </div>

            <div class="brand-small">
                Student Support
            </div>

        </div>

    </div>
    """)


    if st.button(
        "＋ New chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.pending_question = None

        st.rerun()


    st.html("""
    <div class="side-title">
        Knowledge
    </div>

    <div class="side-text">

        Courses<br>
        Assignments<br>
        Library<br>
        Student services<br>
        Policies<br>
        Campus contacts

    </div>


    <div class="side-title">
        Languages
    </div>

    <div class="side-text">

        English<br>
        தமிழ்<br>
        සිංහල

    </div>
    """)


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are CampusAI.

You are a multilingual student support assistant for a
higher-education institution.

You will receive only selected institutional records retrieved
from the CampusAI knowledge base.

STRICT RULES:

1. Use ONLY the retrieved records.

2. Never use outside knowledge for institutional facts.

3. Never invent:
   deadlines,
   schedules,
   lecturers,
   rooms,
   policies,
   fees,
   contacts,
   announcements.

4. If the records do not contain enough information,
   clearly say that verified information could not be found.

5. Answer in the same language as the student whenever possible.

6. Support English, Tamil and Sinhala.

7. Keep answers concise and natural.

8. When a source exists, finish with:

   **Source:** <exact source>

9. Never invent a source.
"""


# ============================================================
# SIMPLE LOCAL RESPONSES
# ============================================================

def local_response(question):

    normalized = question.lower().strip()


    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon"
    ]


    if normalized in greetings:

        return (
            "Hello! I'm CampusAI. "
            "I can help you with campus information, "
            "classes, assignments, library hours and "
            "student services."
        )


    return None


# ============================================================
# ASK CAMPUS AI
# ============================================================

def ask_campus_ai(question):


    # --------------------------------------------------------
    # Handle simple conversation locally
    # --------------------------------------------------------

    local = local_response(
        question
    )


    if local:

        return local


    # --------------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------------

    records = retrieve(
        question,
        top_k=4
    )


    print("\n")
    print("=" * 60)
    print("CAMPUSAI RETRIEVAL")
    print("=" * 60)

    print(
        f"Question: {question}"
    )

    print(
        f"Records found: {len(records)}"
    )


    for record in records:

        print(
            f"- {record.get('id')} "
            f"| score={record.get('retrieval_score')} "
            f"| {record.get('title')}"
        )


    print("=" * 60)


    # --------------------------------------------------------
    # NO RELEVANT DATA
    # --------------------------------------------------------

    if not records:

        return (
            "I couldn't find verified information about that "
            "in the CampusAI knowledge base. Please contact "
            "the relevant campus office for confirmation."
        )


    # --------------------------------------------------------
    # SEND ONLY RELEVANT DATA TO GEMINI
    # --------------------------------------------------------

    context = json.dumps(
        records,
        ensure_ascii=False,
        indent=2
    )


    prompt = f"""
RETRIEVED CAMPUS INFORMATION

{context}


STUDENT QUESTION

{question}


Answer the question using ONLY the retrieved campus information.

Do not use outside institutional knowledge.

If the retrieved records do not provide enough information,
say that verified information could not be found.

Answer in the student's language whenever possible.

Include the exact source from the retrieved information.
"""


    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt,

            config=types.GenerateContentConfig(

                system_instruction=SYSTEM_INSTRUCTION,

                temperature=0.15
            )
        )


        if response.text:

            return response.text


        return (
            "I couldn't generate an answer. "
            "Please try again."
        )


    except Exception as error:

        print("\n")
        print("=" * 60)
        print("GEMINI ERROR")
        print("=" * 60)

        print(
            type(error).__name__
        )

        print(error)

        print("=" * 60)
        print("\n")


        return (
            "CampusAI is temporarily unable to access "
            "the AI service. Please try again shortly."
        )


# ============================================================
# HEADER
# ============================================================

st.html("""
<div class="app-header">

    <div class="app-title">
        CampusAI
    </div>

    <div class="app-status">
        Verified campus knowledge
    </div>

</div>
""")


# ============================================================
# HOME
# ============================================================

if not st.session_state.messages:

    st.html("""
    <div class="home">

        <div class="home-logo">
            CA
        </div>

        <div class="home-title">
            What can I help you with?
        </div>

        <div class="home-text">

            Ask questions about classes, assignments,
            library hours, student services and campus
            information.

            You can ask in English, Tamil or Sinhala.

        </div>

    </div>
    """)


    st.html("""
    <div class="try-label">
        Try asking
    </div>
    """)


    c1, c2 = st.columns(
        2,
        gap="small"
    )


    with c1:

        if st.button(
            "📚 What are the library opening hours?",
            key="question_library",
            use_container_width=True
        ):

            st.session_state.pending_question = (
                "What are the library opening hours?"
            )


    with c2:

        if st.button(
            "📝 When is my Network Security assignment due?",
            key="question_assignment",
            use_container_width=True
        ):

            st.session_state.pending_question = (
                "When is my Network Security assignment due?"
            )


    c3, c4 = st.columns(
        2,
        gap="small"
    )


    with c3:

        if st.button(
            "🗓️ When is the Network Security class?",
            key="question_class",
            use_container_width=True
        ):

            st.session_state.pending_question = (
                "When is the Network Security class?"
            )


    with c4:

        if st.button(
            "💻 Where can I get IT support?",
            key="question_it",
            use_container_width=True
        ):

            st.session_state.pending_question = (
                "Where can I get IT support?"
            )


else:


    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    for message in st.session_state.messages:

        avatar = (
            "👤"
            if message["role"] == "user"
            else "🎓"
        )


        with st.chat_message(
            message["role"],
            avatar=avatar
        ):

            st.markdown(
                message["content"]
            )


# ============================================================
# INPUT
# ============================================================

typed_question = st.chat_input(
    "Message CampusAI"
)


pending_question = (
    st.session_state.pending_question
)


if pending_question:

    question = pending_question

    st.session_state.pending_question = None

else:

    question = typed_question


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:


    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.markdown(
            question
        )


    with st.chat_message(
        "assistant",
        avatar="🎓"
    ):

        with st.spinner(
            "Searching campus knowledge..."
        ):

            answer = ask_campus_ai(
                question
            )


        st.markdown(
            answer
        )


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


# ============================================================
# DISCLAIMER
# ============================================================

if st.session_state.messages:

    st.html("""
    <div class="disclaimer">

        CampusAI retrieves relevant institutional information
        before generating an answer.

        Important academic information should still be
        confirmed with your institution when necessary.

    </div>
    """)