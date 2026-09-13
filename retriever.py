import json
import re
from pathlib import Path


DATA_FOLDER = Path("data")


# ============================================================
# STOP WORDS
# ============================================================

STOP_WORDS = {
    # English
    "a", "an", "the", "is", "are", "was", "were",
    "what", "when", "where", "who", "why", "how",
    "i", "my", "me", "you", "your",
    "to", "for", "of", "in", "on", "at", "by",
    "and", "or", "with", "from", "do", "does",
    "can", "could", "should", "would",
    "this", "that", "these", "those",
    "it", "its", "be", "been", "being",

    # common mixed-language filler
    "எப்போது",
    "எங்கே",
    "என்ன",
    "எப்படி",
    "කොහෙද",
    "කවදා",
    "මොකක්ද"
}


# ============================================================
# CATEGORY ALIASES
# ============================================================

CATEGORY_ALIASES = {

    "library": [
        "library",
        "library hours",
        "opening hours",
        "books",
        "நூலகம்",
        "நூலக நேரம்",
        "පුස්තකාලය"
    ],

    "assignment": [
        "assignment",
        "deadline",
        "submission",
        "submit",
        "coursework",
        "ஒப்படைப்பு",
        "சமர்ப்பிக்க",
        "පැවරුම",
        "භාර දෙන්න"
    ],

    "course": [
        "course",
        "class",
        "lecture",
        "lecturer",
        "room",
        "schedule",
        "timetable",
        "வகுப்பு",
        "பாடம்",
        "விரிவுரையாளர்",
        "පන්තිය",
        "දේශනය"
    ],

    "service": [
        "support",
        "student services",
        "it support",
        "help desk",
        "office",
        "உதவி",
        "ஆதரவு",
        "සේවාව",
        "සහාය"
    ],

    "contact": [
        "contact",
        "email",
        "phone",
        "telephone",
        "call",
        "தொடர்பு",
        "மின்னஞ்சல்",
        "සම්බන්ධ",
        "දුරකථන"
    ],

    "policy": [
        "policy",
        "rule",
        "attendance",
        "procedure",
        "regulation",
        "விதி",
        "கொள்கை",
        "வருகை",
        "නීතිය",
        "ප්‍රතිපත්තිය"
    ],

    "general": [
        "campus",
        "institution",
        "college",
        "university",
        "campusai",
        "வளாகம்",
        "பல்கலைக்கழகம்",
        "විශ්වවිද්‍යාල"
    ]
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(text):

    if text is None:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"[^\w\s\u0B80-\u0BFF\u0D80-\u0DFF@.-]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize(text):

    tokens = normalize_text(text).split()

    return {
        token
        for token in tokens
        if (
            token not in STOP_WORDS
            and len(token) >= 3
        )
    }


# ============================================================
# LOAD DATA
# ============================================================

def load_knowledge_base():

    records = []

    if not DATA_FOLDER.exists():
        return records

    for file_path in DATA_FOLDER.glob("*.json"):

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if not isinstance(data, list):
                continue

            for record in data:

                record["_file"] = file_path.name

                records.append(record)

        except Exception as error:

            print(
                f"Could not load {file_path}: {error}"
            )

    return records


# ============================================================
# CATEGORY DETECTION
# ============================================================

def detect_categories(question):

    question_text = normalize_text(question)

    detected = set()

    for category, aliases in CATEGORY_ALIASES.items():

        for alias in aliases:

            alias_text = normalize_text(alias)

            if alias_text in question_text:

                detected.add(category)
                break

    return detected


# ============================================================
# SCORE RECORD
# ============================================================

def score_record(question, record):

    question_text = normalize_text(question)
    question_tokens = tokenize(question)

    title = normalize_text(
        record.get("title", "")
    )

    content = normalize_text(
        record.get("content", "")
    )

    category = normalize_text(
        record.get("category", "")
    )

    keywords = record.get(
        "keywords",
        []
    )

    title_tokens = tokenize(title)
    content_tokens = tokenize(content)

    keyword_tokens = set()

    for keyword in keywords:
        keyword_tokens.update(
            tokenize(keyword)
        )

    detected_categories = detect_categories(
        question
    )

    score = 0


    # --------------------------------------------------------
    # CATEGORY MATCH
    # --------------------------------------------------------

    if category in detected_categories:
        score += 20


    # --------------------------------------------------------
    # EXACT TOKEN OVERLAP
    # --------------------------------------------------------

    title_overlap = (
        question_tokens
        & title_tokens
    )

    keyword_overlap = (
        question_tokens
        & keyword_tokens
    )

    content_overlap = (
        question_tokens
        & content_tokens
    )

    score += (
        len(title_overlap)
        * 6
    )

    score += (
        len(keyword_overlap)
        * 5
    )

    score += (
        len(content_overlap)
        * 2
    )


    # --------------------------------------------------------
    # EXACT MULTI-WORD KEYWORD PHRASES
    # --------------------------------------------------------

    for keyword in keywords:

        keyword_text = normalize_text(
            keyword
        )

        if (
            " " in keyword_text
            and len(keyword_text) >= 5
            and keyword_text in question_text
        ):

            score += 12


    # --------------------------------------------------------
    # TITLE PHRASE BONUS
    # --------------------------------------------------------

    if (
        title
        and title in question_text
    ):

        score += 15


    # --------------------------------------------------------
    # REQUIRE MEANINGFUL OVERLAP
    # --------------------------------------------------------

    meaningful_overlap = (
        title_overlap
        | keyword_overlap
        | content_overlap
    )

    if (
        category not in detected_categories
        and len(meaningful_overlap) == 0
    ):

        return 0


    return score


# ============================================================
# RETRIEVE
# ============================================================

def retrieve(
    question,
    top_k=4,
    minimum_score=12
):

    records = load_knowledge_base()

    scored_records = []


    for record in records:

        score = score_record(
            question,
            record
        )

        if score >= minimum_score:

            scored_records.append(
                (
                    score,
                    record
                )
            )


    scored_records.sort(
        key=lambda item: item[0],
        reverse=True
    )


    relevant = []


    for score, record in scored_records[:top_k]:

        clean_record = {
            key: value
            for key, value in record.items()
            if not key.startswith("_")
        }

        clean_record[
            "retrieval_score"
        ] = score

        relevant.append(
            clean_record
        )


    return relevant