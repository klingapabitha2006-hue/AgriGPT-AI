import os
import re


# =========================================================
# PATH
# =========================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def _find_knowledge_file():
    """Find data/agriculture_knowledge.txt for root or backend layouts."""
    candidates = [
        os.path.join(CURRENT_DIR, "data", "agriculture_knowledge.txt"),
        os.path.join(os.path.dirname(CURRENT_DIR), "data", "agriculture_knowledge.txt"),
        os.path.join(os.path.dirname(os.path.dirname(CURRENT_DIR)), "data", "agriculture_knowledge.txt"),
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    # Default to the project-root/data layout when the file is created later.
    return candidates[1] if os.path.basename(CURRENT_DIR).lower() in {"backend", "server", "api"} else candidates[0]

KNOWLEDGE_FILE = _find_knowledge_file()


# =========================================================
# LOAD KNOWLEDGE
# =========================================================

def load_knowledge():
    try:
        with open(
            KNOWLEDGE_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return file.read()

    except FileNotFoundError:
        return ""

    except Exception as e:
        print("Knowledge loading error:", e)
        return ""


# =========================================================
# NORMALIZE
# =========================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
        flags=re.UNICODE
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# LANGUAGE DETECTION
# =========================================================

TANGLISH_WORDS = {
    "enna", "epdi", "eppadi", "epothu", "eppo", "venum",
    "vendum", "pannanum", "podanum", "irukku", "iruku",
    "irukkum", "varum", "varuthu", "nalla", "thevai",
    "sollu", "sollunga", "kudunga", "kudu", "payir",
    "nel", "mann", "neer", "uram", "poochi", "noi",
    "vivasayam", "thakkali", "vazhai", "milagai", "vithai",
    "saagupadi", "thanni", "mazhai", "ilai", "kaai",
    "aaguma", "aagum", "illa", "illai", "yen", "yenna",
    "epadi", "marundhu", "pannunga", "pannu", "iruka",
    "ithu", "athu", "naan", "neenga", "ungal", "romba",
    "konjam", "eppadi", "seiyanum", "seyyanum"
}


def is_tamil(text):
    """True when the text contains Tamil script."""
    return bool(text and re.search(r"[\u0B80-\u0BFF]", text))


def is_tanglish(text):
    """Detect common Romanized Tamil words, unless Tamil script is present."""
    if not text or is_tamil(text):
        return False

    words = set(normalize_text(text).split())
    return bool(words.intersection(TANGLISH_WORDS))


def detect_response_language(question, requested_language="auto"):
    """
    The selected dropdown language takes priority over the question language.
    Supported values: ta/tamil, tanglish/ta-latn, en/english, auto.
    """
    requested = (requested_language or "auto").strip().lower()

    if requested in {"ta", "ta-in", "tamil"}:
        return "tamil"
    if requested in {"tanglish", "ta-latn", "romanized-tamil"}:
        return "tanglish"
    if requested in {"en", "en-in", "english"}:
        return "english"

    if is_tamil(question):
        return "tamil"
    if is_tanglish(question):
        return "tanglish"
    return "english"


def tamil_to_tanglish(text):
    """
    Approximate Tamil-script transliteration to Roman letters.
    This is transliteration, not a full translation engine.
    """
    if not text:
        return ""

    consonants = {
        "க": "k", "ங": "ng", "ச": "s", "ஞ": "nj",
        "ட": "t", "ண": "n", "த": "th", "ந": "n",
        "ப": "p", "ம": "m", "ய": "y", "ர": "r",
        "ல": "l", "வ": "v", "ழ": "zh", "ள": "l",
        "ற": "r", "ன": "n", "ஜ": "j", "ஷ": "sh",
        "ஸ": "s", "ஹ": "h"
    }
    vowel_signs = {
        "ா": "aa", "ி": "i", "ீ": "ee", "ு": "u",
        "ூ": "oo", "ெ": "e", "ே": "ae", "ை": "ai",
        "ொ": "o", "ோ": "oo", "ௌ": "au"
    }
    independent_vowels = {
        "அ": "a", "ஆ": "aa", "இ": "i", "ஈ": "ee",
        "உ": "u", "ஊ": "oo", "எ": "e", "ஏ": "ae",
        "ஐ": "ai", "ஒ": "o", "ஓ": "oo", "ஔ": "au"
    }

    result = []
    i = 0

    while i < len(text):
        char = text[i]

        if char in independent_vowels:
            result.append(independent_vowels[char])
            i += 1
            continue

        if char in consonants:
            base = consonants[char]
            nxt = text[i + 1] if i + 1 < len(text) else ""

            if nxt == "்":
                result.append(base)
                i += 2
            elif nxt in vowel_signs:
                result.append(base + vowel_signs[nxt])
                i += 2
            else:
                result.append(base + "a")
                i += 1
            continue

        result.append(char)
        i += 1

    return "".join(result)


# =========================================================
# CROP DETECTION
# =========================================================

def detect_crop(question):

    q = normalize_text(question)

    crops = {

        "rice": [
            "rice",
            "paddy",
            "நெல்",
            "அரிசி"
        ],

        "tomato": [
            "tomato",
            "தக்காளி"
        ],

        "potato": [
            "potato",
            "potatoes",
            "உருளைக்கிழங்கு"
        ],

        "maize": [
            "maize",
            "corn",
            "மக்காச்சோளம்"
        ],

        "wheat": [
            "wheat",
            "கோதுமை"
        ],

        "sugarcane": [
            "sugarcane",
            "கரும்பு"
        ],

        "cotton": [
            "cotton",
            "பருத்தி"
        ],

        "groundnut": [
            "groundnut",
            "peanut",
            "வேர்க்கடலை"
        ],

        "onion": [
            "onion",
            "வெங்காயம்"
        ],

        "chilli": [
            "chilli",
            "chili",
            "மிளகாய்"
        ],

        "brinjal": [
            "brinjal",
            "eggplant",
            "கத்தரிக்காய்"
        ],

        "banana": [
            "banana",
            "வாழை"
        ]
    }

    for crop, words in crops.items():

        for word in words:

            if word in q:
                return crop

    return "general"


# =========================================================
# QUESTION TYPE
# =========================================================

def detect_question_type(question):

    q = normalize_text(question)

    question_types = {

        "disease": [
            "disease",
            "diseases",
            "infection",
            "symptom",
            "symptoms",
            "identify",
            "diagnose",
            "diagnosis",
            "நோய்",
            "நோய்கள்",
            "அறிகுறி",
            "அறிகுறிகள்",
            "நோய் தாக்குதல்"
        ],

        "pest": [
            "pest",
            "pests",
            "insect",
            "insects",
            "borer",
            "aphid",
            "whitefly",
            "பூச்சி",
            "பூச்சிகள்"
        ],

        "water": [
            "water",
            "irrigation",
            "irrigate",
            "watering",
            "நீர்",
            "நீர்ப்பாசனம்",
            "பாசனம்"
        ],

        "soil": [
            "soil",
            "land",
            "மண்",
            "நிலம்"
        ],

        "fertilizer": [
            "fertilizer",
            "fertiliser",
            "nitrogen",
            "phosphorus",
            "potassium",
            "urea",
            "உரம்",
            "நைட்ரஜன்",
            "பாஸ்பரஸ்",
            "பொட்டாசியம்"
        ],

        "seed": [
            "seed",
            "seeds",
            "seedling",
            "seedlings",
            "விதை",
            "நாற்று",
            "நாற்றுகள்"
        ],

        "harvesting": [
            "harvest",
            "harvesting",
            "அறுவடை"
        ],

        "storage": [
            "storage",
            "store",
            "storing",
            "சேமிப்பு",
            "சேமிக்க"
        ],

        "climate": [
            "climate",
            "temperature",
            "weather",
            "rainfall",
            "humidity",
            "sunlight",
            "season",
            "வெப்பநிலை",
            "மழை",
            "காலநிலை",
            "ஈரப்பதம்",
            "பருவம்",
            "வானிலை"
        ],

        "weed": [
            "weed",
            "weeds",
            "weeding",
            "களை"
        ],

        "nursery": [
            "nursery",
            "நாற்றங்கால்"
        ],

        "planting": [
            "plant",
            "planting",
            "transplant",
            "transplanting",
            "cultivate",
            "cultivation",
            "grow",
            "growing",
            "சாகுபடி",
            "நடவு",
            "விதைப்பு"
        ]
    }

    for question_type, words in question_types.items():

        for word in words:

            if word in q:
                return question_type

    return "general"


# =========================================================
# SECTION PARSER
# =========================================================

def parse_sections(knowledge):

    sections = {}

    current_section = None
    current_content = []

    for raw_line in knowledge.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        clean = normalize_text(line)

        is_heading = False

        # -------------------------------
        # Normal headings
        # -------------------------------

        heading_words = [
            "crop:",
            "soil:",
            "climate:",
            "seed:",
            "irrigation:",
            "fertilizer:",
            "harvesting:",
            "storage:",
            "water management",
            "weed management",
            "land preparation",
            "planting:",
            "crop health",
            "general farming advice",
            "crop stages",
            "crop monitoring",
            "weather and farming",
            "temperature",
            "humidity",
            "sunlight",
            "pest management",
            "integrated pest management",
            "crop disease management",
            "rice blast",
            "bacterial leaf blight",
            "brown spot",
            "rice tungro"
        ]

        if any(
            clean.startswith(word)
            for word in heading_words
        ):
            is_heading = True

        # -------------------------------
        # Crop block headings
        # -------------------------------

        crop_heading_words = [
            "rice",
            "tomato",
            "potato",
            "maize",
            "wheat",
            "sugarcane",
            "cotton",
            "groundnut",
            "onion",
            "chilli",
            "brinjal",
            "banana"
        ]

        if any(
            clean.startswith(word)
            for word in crop_heading_words
        ):
            if len(clean) <= 80:
                is_heading = True

        # -------------------------------
        # Uppercase headings
        # -------------------------------

        if (
            line == line.upper()
            and len(line) <= 80
            and any(char.isalpha() for char in line)
        ):
            is_heading = True

        # -------------------------------
        # Save section
        # -------------------------------

        if is_heading:

            if current_section is not None:

                sections[current_section] = (
                    " ".join(current_content).strip()
                )

            current_section = clean
            current_content = []

        else:

            if current_section is not None:
                current_content.append(line)

    if current_section is not None:

        sections[current_section] = (
            " ".join(current_content).strip()
        )

    return sections


# =========================================================
# FIND BEST SECTION
# =========================================================

def find_best_section(
    sections,
    crop,
    question_type,
    question
):

    q = normalize_text(question)

    type_keywords = {

        "disease": [
            "disease",
            "diseases",
            "blast",
            "blight",
            "wilt",
            "curl",
            "scab",
            "நோய்"
        ],

        "pest": [
            "pest",
            "insect",
            "borer",
            "aphid",
            "whitefly",
            "பூச்சி"
        ],

        "water": [
            "water",
            "irrigation",
            "நீர்",
            "பாசனம்"
        ],

        "soil": [
            "soil",
            "land",
            "மண்",
            "நிலம்"
        ],

        "fertilizer": [
            "fertilizer",
            "fertiliser",
            "nitrogen",
            "phosphorus",
            "potassium",
            "urea",
            "உரம்"
        ],

        "seed": [
            "seed",
            "seedling",
            "விதை",
            "நாற்று"
        ],

        "harvesting": [
            "harvest",
            "harvesting",
            "அறுவடை"
        ],

        "storage": [
            "storage",
            "store",
            "சேமிப்பு"
        ],

        "climate": [
            "climate",
            "temperature",
            "weather",
            "rainfall",
            "humidity",
            "sunlight",
            "வெப்பநிலை",
            "மழை",
            "காலநிலை",
            "ஈரப்பதம்"
        ],

        "weed": [
            "weed",
            "weeding",
            "களை"
        ],

        "nursery": [
            "nursery",
            "நாற்றங்கால்"
        ],

        "planting": [
            "plant",
            "planting",
            "transplant",
            "cultivate",
            "cultivation",
            "நடவு",
            "சாகுபடி"
        ]
    }

    crop_words = {

        "rice": [
            "rice",
            "paddy",
            "நெல்",
            "அரிசி"
        ],

        "tomato": [
            "tomato",
            "தக்காளி"
        ],

        "potato": [
            "potato",
            "உருளைக்கிழங்கு"
        ],

        "maize": [
            "maize",
            "corn",
            "மக்காச்சோளம்"
        ],

        "wheat": [
            "wheat",
            "கோதுமை"
        ],

        "sugarcane": [
            "sugarcane",
            "கரும்பு"
        ],

        "cotton": [
            "cotton",
            "பருத்தி"
        ],

        "groundnut": [
            "groundnut",
            "peanut",
            "வேர்க்கடலை"
        ],

        "onion": [
            "onion",
            "வெங்காயம்"
        ],

        "chilli": [
            "chilli",
            "chili",
            "மிளகாய்"
        ],

        "brinjal": [
            "brinjal",
            "eggplant",
            "கத்தரிக்காய்"
        ],

        "banana": [
            "banana",
            "வாழை"
        ]
    }

    candidates = []

    for section_name, content in sections.items():

        score = 0

        section_lower = section_name.lower()
        content_lower = normalize_text(content)

        # --------------------------------
        # Question type
        # --------------------------------

        keywords = type_keywords.get(
            question_type,
            []
        )

        for keyword in keywords:

            if keyword in section_lower:
                score += 15

            if keyword in content_lower:
                score += 2

            if keyword in q:
                score += 1

        # --------------------------------
        # Crop
        # --------------------------------

        if crop != "general":

            for word in crop_words.get(
                crop,
                []
            ):

                if word in section_lower:
                    score += 25

                if word in content_lower:
                    score += 4

        # --------------------------------
        # Exact question words
        # --------------------------------

        question_words = set(
            q.split()
        )

        section_words = set(
            section_lower.split()
        )

        common_words = (
            question_words &
            section_words
        )

        score += len(common_words) * 3

        if score > 0:

            candidates.append(
                (
                    score,
                    section_name,
                    content
                )
            )

    if not candidates:
        return ""

    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    best_score, best_section, best_content = (
        candidates[0]
    )

    print(
        "[Shebixion Retrieval] "
        f"Crop={crop} | "
        f"Type={question_type} | "
        f"Section={best_section} | "
        f"Score={best_score}"
    )

    return best_content


# =========================================================
# TAMIL ANSWER DATABASE
# =========================================================

TAMIL_ANSWERS = {

    # -----------------------------------------------------
    # RICE
    # -----------------------------------------------------

    ("rice", "climate"):
        "நெல் பயிர் வெப்பமான மற்றும் ஈரப்பதமான காலநிலையில் நன்றாக வளரும். "
        "சரியான வெப்பநிலை, போதுமான மழை மற்றும் தேவையான நீர் கிடைப்பது "
        "நெல் வளர்ச்சிக்கு முக்கியமானது.",

    ("rice", "soil"):
        "நெல் பயிருக்கு களிமண் மற்றும் களிமண் கலந்த மண் பொதுவாக ஏற்றது. "
        "இத்தகைய மண் நீரை தக்கவைத்துக்கொள்ளும் திறன் கொண்டது.",

    ("rice", "water"):
        "நெல் பயிருக்கு வளர்ச்சி நிலைக்கு ஏற்ப சரியான நீர்ப்பாசனம் தேவை. "
        "தேவையில்லாமல் தொடர்ந்து அதிக நீர் தேங்குவதை தவிர்க்க வேண்டும்.",

    ("rice", "fertilizer"):
        "நெல் பயிருக்கு நைட்ரஜன், பாஸ்பரஸ் மற்றும் பொட்டாசியம் போன்ற "
        "சத்துக்கள் தேவை. உரமிடுதல் மண் நிலை மற்றும் பயிரின் தேவையை "
        "அடிப்படையாகக் கொண்டு செய்ய வேண்டும்.",

    ("rice", "seed"):
        "நல்ல தரமான மற்றும் ஆரோக்கியமான நெல் விதைகளை பயன்படுத்த வேண்டும். "
        "உள்ளூர் சூழ்நிலைக்கு ஏற்ற தரமான விதைகளை தேர்வு செய்வது நல்லது.",

    ("rice", "disease"):
        "நெல் பயிரில் Blast, Bacterial Leaf Blight, Brown Spot மற்றும் "
        "Rice Tungro போன்ற நோய்கள் ஏற்படலாம். இலைகளில் நிறமாற்றம், "
        "பழுப்பு புள்ளிகள், உலர்தல் அல்லது அசாதாரண வளர்ச்சி போன்ற "
        "அறிகுறிகளை தொடர்ந்து கண்காணிக்க வேண்டும்.",

    ("rice", "pest"):
        "நெல் வயலில் பூச்சி தாக்குதலை கண்டறிய இலைகள் மற்றும் தண்டுகளை "
        "தொடர்ந்து கண்காணிக்க வேண்டும். பூச்சியை சரியாக அடையாளம் கண்ட "
        "பிறகே பரிந்துரைக்கப்பட்ட மேலாண்மை முறைகளை பின்பற்ற வேண்டும்.",

    ("rice", "harvesting"):
        "நெல் மணிகள் சரியான முதிர்ச்சி நிலையை அடைந்தபோது அறுவடை செய்ய வேண்டும். "
        "அறுவடைக்குப் பிறகு நன்றாக உலர்த்துவது சேமிப்பு பிரச்சனைகளை குறைக்க உதவும்.",


    # -----------------------------------------------------
    # TOMATO
    # -----------------------------------------------------

    ("tomato", "climate"):
        "தக்காளி பயிருக்கு மிதமான வெப்பநிலை மற்றும் நல்ல சூரிய ஒளி ஏற்றது. "
        "அதிக வெப்பம், அதிக மழை மற்றும் அதிக ஈரப்பதம் சில நோய் மற்றும் "
        "பூச்சி பிரச்சனைகளை அதிகரிக்கலாம்.",

    ("tomato", "soil"):
        "தக்காளிக்கு வளமான, நல்ல வடிகால் வசதியுள்ள மற்றும் கரிமப் பொருட்கள் "
        "நிறைந்த மண் ஏற்றது.",

    ("tomato", "water"):
        "தக்காளிக்கு முறையான மற்றும் தேவையான அளவு நீர்ப்பாசனம் வழங்க வேண்டும். "
        "நீர் பற்றாக்குறையையும் அதிக நீர் தேக்கத்தையும் தவிர்க்க வேண்டும்.",

    ("tomato", "fertilizer"):
        "தக்காளிக்கு நைட்ரஜன், பாஸ்பரஸ், பொட்டாசியம் போன்ற சத்துக்கள் தேவை. "
        "மண் வளம் மற்றும் பயிரின் வளர்ச்சி நிலையை அடிப்படையாகக் கொண்டு உர மேலாண்மை செய்ய வேண்டும்.",

    ("tomato", "disease"):
        "தக்காளியில் Tomato Leaf Curl, Early Blight, Late Blight மற்றும் "
        "Bacterial Wilt போன்ற நோய்கள் ஏற்படலாம். இலைகள் சுருட்டப்படுதல், "
        "கரும்புள்ளிகள் மற்றும் திடீர் வாடுதல் போன்ற அறிகுறிகளை கண்காணிக்க வேண்டும்.",

    ("tomato", "pest"):
        "தக்காளியில் Fruit Borer மற்றும் Whitefly போன்ற பூச்சிகள் பாதிப்பை ஏற்படுத்தலாம். "
        "பயிரை தொடர்ந்து கண்காணித்து ஒருங்கிணைந்த பூச்சி மேலாண்மை முறைகளை பின்பற்ற வேண்டும்.",


    # -----------------------------------------------------
    # POTATO
    # -----------------------------------------------------

    ("potato", "climate"):
        "உருளைக்கிழங்கு பயிருக்கு குளிர்ச்சியான வளர்ச்சி சூழல் பொதுவாக ஏற்றது. "
        "அதிக வெப்பநிலை கிழங்கு வளர்ச்சியை பாதிக்கலாம்.",

    ("potato", "soil"):
        "உருளைக்கிழங்கிற்கு தளர்வான, வளமான மற்றும் நல்ல வடிகால் வசதியுள்ள மண் ஏற்றது. "
        "நீர் தேங்குவதை தவிர்க்க வேண்டும்.",

    ("potato", "water"):
        "உருளைக்கிழங்கு வளர்ச்சிக்கு போதுமான ஈரப்பதம் தேவை. "
        "ஆனால் அதிகப்படியான நீர் தேக்கம் ஏற்படாமல் பார்த்துக்கொள்ள வேண்டும்.",

    ("potato", "disease"):
        "உருளைக்கிழங்கில் Early Blight, Late Blight, Bacterial Wilt மற்றும் "
        "Common Scab போன்ற நோய்கள் ஏற்படலாம். பயிரை தொடர்ந்து கண்காணிப்பது முக்கியம்.",

    ("potato", "pest"):
        "உருளைக்கிழங்கில் Aphids மற்றும் Potato Tuber Moth போன்ற பூச்சிகள் "
        "பாதிப்பை ஏற்படுத்தலாம். தொடர்ந்து கண்காணித்து பொருத்தமான பூச்சி மேலாண்மை முறைகளை பயன்படுத்த வேண்டும்.",


    # -----------------------------------------------------
    # MAIZE
    # -----------------------------------------------------

    ("maize", "climate"):
        "மக்காச்சோளத்திற்கு போதுமான வெப்பமும் தேவையான ஈரப்பதமும் உள்ள சூழல் ஏற்றது. "
        "முக்கியமான வளர்ச்சி நிலைகளில் போதுமான நீர் கிடைக்க வேண்டும்.",

    ("maize", "soil"):
        "மக்காச்சோளம் வளமான மற்றும் நல்ல வடிகால் வசதியுள்ள மண்ணில் நன்றாக வளரும்.",

    ("maize", "water"):
        "மக்காச்சோளத்தின் முக்கிய வளர்ச்சி நிலைகளில் போதுமான ஈரப்பதம் வழங்க வேண்டும். "
        "நீண்ட நேரம் நீர் தேங்குவதை தவிர்க்க வேண்டும்.",

    ("maize", "pest"):
        "மக்காச்சோளத்தில் Stem Borer மற்றும் Fall Armyworm போன்ற பூச்சிகள் "
        "பாதிப்பை ஏற்படுத்தலாம். தொடர்ந்து கண்காணிப்பது முக்கியம்.",

    ("maize", "disease"):
        "மக்காச்சோளத்தில் பூஞ்சை, பாக்டீரியா அல்லது வைரஸ் நோய்கள் ஏற்படலாம். "
        "இலைகளில் புள்ளிகள் மற்றும் அசாதாரண வளர்ச்சி போன்ற அறிகுறிகளை கவனிக்க வேண்டும்.",


    # -----------------------------------------------------
    # WHEAT
    # -----------------------------------------------------

    ("wheat", "climate"):
        "கோதுமை பொதுவாக குளிர்ச்சியான பருவநிலைக்கு ஏற்ற பயிராகும்.",

    ("wheat", "soil"):
        "கோதுமைக்கு வளமான மற்றும் நல்ல வடிகால் வசதியுள்ள மண் ஏற்றது.",

    ("wheat", "water"):
        "கோதுமைக்கு பயிரின் வளர்ச்சி நிலை, மண் ஈரப்பதம் மற்றும் உள்ளூர் சூழ்நிலைக்கு ஏற்ப நீர்ப்பாசனம் வழங்க வேண்டும்.",

    ("wheat", "disease"):
        "கோதுமையில் Rust போன்ற பூஞ்சை நோய்கள் ஏற்படலாம். பயிரை தொடர்ந்து கண்காணிக்க வேண்டும்.",


    # -----------------------------------------------------
    # SUGARCANE
    # -----------------------------------------------------

    ("sugarcane", "climate"):
        "கரும்பு பயிருக்கு வெப்பமான சூழல் மற்றும் போதுமான ஈரப்பதம் பொதுவாக ஏற்றது.",

    ("sugarcane", "soil"):
        "கரும்புக்கு வளமான, நல்ல வடிகால் வசதியுள்ள மற்றும் தேவையான அளவு நீரை தக்கவைக்கும் மண் ஏற்றது.",

    ("sugarcane", "water"):
        "கரும்புக்கு வளர்ச்சி காலத்தில் போதுமான நீர் தேவை. முடிந்தவரை நீர் தேக்கம் ஏற்படாமல் பார்த்துக்கொள்ள வேண்டும்.",

    ("sugarcane", "disease"):
        "கரும்பில் இலைகளில் அசாதாரண அறிகுறிகள், வாடுதல் மற்றும் வளர்ச்சி மாற்றங்களை தொடர்ந்து கண்காணிக்க வேண்டும்.",


    # -----------------------------------------------------
    # COTTON
    # -----------------------------------------------------

    ("cotton", "climate"):
        "பருத்தி பயிருக்கு ஏற்ற வெப்பமான காலநிலை மற்றும் போதுமான சூரிய ஒளி தேவை.",

    ("cotton", "soil"):
        "பருத்தி பொதுவாக வளமான மற்றும் நல்ல வடிகால் வசதியுள்ள மண்ணில் நன்றாக வளரும்.",

    ("cotton", "pest"):
        "பருத்தியில் Bollworms மற்றும் சில sucking pests போன்ற பூச்சிகள் பாதிப்பை ஏற்படுத்தலாம். தொடர்ந்து கண்காணிக்க வேண்டும்.",

    ("cotton", "disease"):
        "பருத்தியில் இலைப் புள்ளிகள், வாடுதல் மற்றும் பிற அசாதாரண அறிகுறிகளை கண்காணிக்க வேண்டும்.",


    # -----------------------------------------------------
    # GROUNDNUT
    # -----------------------------------------------------

    ("groundnut", "climate"):
        "வேர்க்கடலைக்கு வெப்பமான சூழல் பொதுவாக ஏற்றது.",

    ("groundnut", "soil"):
        "வேர்க்கடலைக்கு தளர்வான மற்றும் நல்ல வடிகால் வசதியுள்ள மண் ஏற்றது. "
        "இது காய்கள் சரியாக வளர உதவும்.",

    ("groundnut", "water"):
        "வேர்க்கடலையின் முக்கிய வளர்ச்சி நிலைகளில் போதுமான ஈரப்பதம் வழங்க வேண்டும். "
        "நீர் தேக்கத்தை தவிர்க்க வேண்டும்.",

    ("groundnut", "disease"):
        "வேர்க்கடலையில் Leaf Spot, Rust போன்ற நோய்கள் ஏற்படலாம். "
        "பயிரை தொடர்ந்து கண்காணிக்க வேண்டும்.",


    # -----------------------------------------------------
    # ONION
    # -----------------------------------------------------

    ("onion", "climate"):
        "வெங்காயத்திற்கு மிதமான காலநிலை பொதுவாக ஏற்றது. இது கிழங்கு வளர்ச்சிக்கு உதவும்.",

    ("onion", "soil"):
        "வெங்காயத்திற்கு வளமான மற்றும் நல்ல வடிகால் வசதியுள்ள மண் ஏற்றது.",

    ("onion", "water"):
        "வெங்காயத்திற்கு முறையான ஈரப்பதம் தேவை. அதிகப்படியான நீர் தேக்கத்தை தவிர்க்க வேண்டும்.",

    ("onion", "pest"):
        "வெங்காயத்தில் Thrips போன்ற பூச்சிகள் இலைகளை பாதிக்கலாம். தொடர்ந்து கண்காணிக்க வேண்டும்.",


    # -----------------------------------------------------
    # CHILLI
    # -----------------------------------------------------

    ("chilli", "climate"):
        "மிளகாய்க்கு வெப்பமான சூழல் மற்றும் நல்ல சூரிய ஒளி பொதுவாக ஏற்றது.",

    ("chilli", "soil"):
        "மிளகாய் வளமான மற்றும் நல்ல வடிகால் வசதியுள்ள மண்ணில் நன்றாக வளரும்.",

    ("chilli", "water"):
        "மிளகாய்க்கு தேவையான அளவு நீர்ப்பாசனம் வழங்க வேண்டும். நீண்ட நேரம் நீர் தேங்குவதை தவிர்க்க வேண்டும்.",

    ("chilli", "pest"):
        "மிளகாயில் Aphids, Thrips மற்றும் Mites போன்ற பூச்சிகள் ஏற்படலாம். பயிரை தொடர்ந்து கண்காணிக்க வேண்டும்.",

    ("chilli", "disease"):
        "மிளகாயில் வைரஸ், பூஞ்சை மற்றும் பாக்டீரியா நோய்கள் ஏற்படலாம். பயிரை தொடர்ந்து கண்காணிக்க வேண்டும்.",


    # -----------------------------------------------------
    # BRINJAL
    # -----------------------------------------------------

    ("brinjal", "climate"):
        "கத்தரிக்காய்க்கு வெப்பமான காலநிலை பொதுவாக ஏற்றது.",

    ("brinjal", "soil"):
        "கத்தரிக்காய் வளமான மற்றும் நல்ல வடிகால் வசதியுள்ள மண்ணில் நன்றாக வளரும்.",

    ("brinjal", "water"):
        "கத்தரிக்காய்க்கு போதுமான மண் ஈரப்பதம் வழங்க வேண்டும். அதிகப்படியான நீர் தேக்கத்தை தவிர்க்க வேண்டும்.",

    ("brinjal", "pest"):
        "கத்தரிக்காயில் Shoot and Fruit Borer போன்ற பூச்சிகள் தாவரத்தையும் பழங்களையும் பாதிக்கலாம்.",

    ("brinjal", "disease"):
        "கத்தரிக்காயில் Bacterial Wilt போன்ற நோய்கள் ஏற்படலாம். பயிரை தொடர்ந்து கண்காணிக்க வேண்டும்.",


    # -----------------------------------------------------
    # BANANA
    # -----------------------------------------------------

    ("banana", "climate"):
        "வாழைக்கு வெப்பமான சூழல் மற்றும் போதுமான ஈரப்பதம் பொதுவாக ஏற்றது.",

    ("banana", "soil"):
        "வாழைக்கு வளமான, நல்ல வடிகால் வசதியுள்ள மற்றும் கரிமப் பொருட்கள் நிறைந்த மண் ஏற்றது.",

    ("banana", "water"):
        "வாழைக்கு மண் மற்றும் வானிலை நிலைக்கு ஏற்ப போதுமான ஈரப்பதம் வழங்க வேண்டும்.",

    ("banana", "disease"):
        "வாழையில் இலைகள், தண்டு மற்றும் பழங்களில் அசாதாரண அறிகுறிகளை தொடர்ந்து கண்காணிக்க வேண்டும்.",

    ("banana", "pest"):
        "வாழையில் பல்வேறு பூச்சிகள் பாதிப்பை ஏற்படுத்தலாம். பயிரை தொடர்ந்து கண்காணிப்பது முக்கியம்."
}


# =========================================================
# GENERAL TAMIL ANSWERS
# =========================================================

GENERAL_TAMIL = {

    "soil":
        "மண் வளத்தை அறிய மண் பரிசோதனை செய்வது நல்லது. "
        "கரிமப் பொருட்கள், பயிர் சுழற்சி மற்றும் சரியான உர மேலாண்மை "
        "மண் ஆரோக்கியத்தை மேம்படுத்த உதவும்.",

    "water":
        "நீர்ப்பாசனம் பயிரின் வகை, மண், வானிலை மற்றும் வளர்ச்சி நிலையை "
        "அடிப்படையாகக் கொண்டு செய்ய வேண்டும். தேவையில்லாத நீர் வீணாவதை தவிர்க்க வேண்டும்.",

    "fertilizer":
        "உரத்தை மண் பரிசோதனை முடிவு மற்றும் பயிரின் தேவையை அடிப்படையாகக் கொண்டு பயன்படுத்த வேண்டும். "
        "அதிகப்படியான உரப் பயன்பாட்டை தவிர்க்க வேண்டும்.",

    "disease":
        "இலைகளில் புள்ளிகள், மஞ்சள் நிறம், வாடுதல் அல்லது அசாதாரண வளர்ச்சி "
        "போன்ற அறிகுறிகளை தொடர்ந்து கண்காணிக்க வேண்டும். "
        "சரியான நோயை கண்டறிந்த பிறகே மேலாண்மை முறையை தேர்வு செய்ய வேண்டும்.",

    "pest":
        "பயிரை தொடர்ந்து கண்காணித்து பூச்சியை சரியாக அடையாளம் காண வேண்டும். "
        "பின்னர் பொருத்தமான ஒருங்கிணைந்த பூச்சி மேலாண்மை முறைகளை பின்பற்ற வேண்டும்.",

    "climate":
        "ஒவ்வொரு பயிருக்கும் வெப்பநிலை, மழை, ஈரப்பதம் மற்றும் சூரிய ஒளி "
        "தேவைகள் வேறுபடும். பயிரை தேர்வு செய்யும்போது உள்ளூர் காலநிலை மற்றும் பருவநிலையை கருத்தில் கொள்ள வேண்டும்.",

    "seed":
        "உள்ளூர் மண் மற்றும் காலநிலைக்கு ஏற்ற நல்ல தரமான ஆரோக்கியமான விதைகளை பயன்படுத்துவது நல்லது.",

    "harvesting":
        "பயிரின் சரியான முதிர்ச்சி நிலையை அடைந்த பிறகு அறுவடை செய்ய வேண்டும். "
        "சரியான நேரத்தில் அறுவடை செய்வது தரத்தையும் இழப்பைக் குறைப்பதையும் உதவும்.",

    "storage":
        "விவசாயப் பொருட்களை சுத்தமான, உலர்ந்த மற்றும் பாதுகாப்பான இடத்தில் சேமிக்க வேண்டும். "
        "அதிக ஈரப்பதம் மற்றும் பூச்சி தாக்குதலை தவிர்க்க வேண்டும்.",

    "planting":
        "நல்ல தரமான நடவு பொருட்களை பயன்படுத்தி, பயிருக்கு ஏற்ற இடைவெளி மற்றும் "
        "மண் தயாரிப்புடன் நடவு செய்ய வேண்டும்.",

    "nursery":
        "ஆரோக்கியமான நாற்றுகளை உருவாக்க சுத்தமான நாற்றங்கால், சரியான ஈரப்பதம், "
        "நல்ல வடிகால் மற்றும் பூச்சி நோய் பாதுகாப்பு தேவை.",

    "weed":
        "களைகள் நீர், சத்து மற்றும் சூரிய ஒளிக்காக பயிருடன் போட்டியிடும். "
        "ஆரம்ப நிலையிலேயே பொருத்தமான களை மேலாண்மை செய்வது நல்லது.",

    "general":
        "விவசாயத்தில் பயிர் தேர்வு, மண், நீர், காலநிலை, சத்து, பூச்சி மற்றும் "
        "நோய் மேலாண்மை ஆகியவற்றை ஒருங்கிணைத்து கவனிப்பது முக்கியம்."
}


# =========================================================
# GET TAMIL ANSWER
# =========================================================

def get_tamil_answer(
    crop,
    question_type,
    retrieved_answer=""
):

    # ---------------------------------------
    # Exact crop + question type
    # ---------------------------------------

    key = (
        crop,
        question_type
    )

    if key in TAMIL_ANSWERS:

        return TAMIL_ANSWERS[key]

    # ---------------------------------------
    # General Tamil answer
    # ---------------------------------------

    if question_type in GENERAL_TAMIL:

        return GENERAL_TAMIL[
            question_type
        ]

    # ---------------------------------------
    # Crop general
    # ---------------------------------------

    crop_names = {

        "rice": "நெல்",
        "tomato": "தக்காளி",
        "potato": "உருளைக்கிழங்கு",
        "maize": "மக்காச்சோளம்",
        "wheat": "கோதுமை",
        "sugarcane": "கரும்பு",
        "cotton": "பருத்தி",
        "groundnut": "வேர்க்கடலை",
        "onion": "வெங்காயம்",
        "chilli": "மிளகாய்",
        "brinjal": "கத்தரிக்காய்",
        "banana": "வாழை"
    }

    if crop in crop_names:

        return (
            f"{crop_names[crop]} பயிர் பற்றிய தகவலுக்கு "
            "மண், காலநிலை, நீர்ப்பாசனம், உரம் மற்றும் "
            "நோய் மேலாண்மை போன்ற அம்சங்களை கவனிக்க வேண்டும்."
        )

    return GENERAL_TAMIL["general"]


# =========================================================
# GENERAL AGRICULTURE SEARCH
# =========================================================

def general_agriculture_search(
    sections,
    question
):

    q = normalize_text(question)

    scores = []

    for section_name, content in sections.items():

        score = 0

        section_text = normalize_text(
            section_name
        )

        content_text = normalize_text(
            content
        )

        for word in q.split():

            if len(word) < 2:
                continue

            if word in section_text:
                score += 5

            if word in content_text:
                score += 1

        if score > 0:

            scores.append(
                (
                    score,
                    section_name,
                    content
                )
            )

    scores.sort(
        key=lambda x: x[0],
        reverse=True
    )

    if scores:
        return scores[0][2]

    return ""




def _word_match(text, phrase):
    """Match English keywords as whole words; Tamil phrases as substrings."""
    text_n = normalize_text(text)
    phrase_n = normalize_text(phrase)
    if not phrase_n:
        return False
    if re.search(r"[\u0B80-\u0BFF]", phrase_n):
        return phrase_n in text_n
    return bool(re.search(r"(?<!\w)" + re.escape(phrase_n) + r"(?!\w)", text_n))


def find_best_qa(knowledge, question):
    """Find Qn/A Q&A records in agriculture_knowledge.txt when present."""
    q_norm = normalize_text(question)
    if not q_norm:
        return ""
    # Supports single-line records such as: Q1: Question? A: Answer
    # and multi-line Qn/A blocks until the next Qn marker.
    matches = list(re.finditer(r"(?im)^\s*Q\s*\d+\s*[:.)-]\s*", knowledge))
    records = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(knowledge)
        block = knowledge[start:end].strip()
        qa = re.search(r"(?is)^\s*Q\s*\d+\s*[:.)-]\s*(.*?)\s+A\s*:\s*(.*)$", block)
        if qa:
            records.append((qa.group(1).strip(), qa.group(2).strip()))
    if not records:
        return ""
    q_tokens = [w for w in q_norm.split() if len(w) > 2 and w not in {"what", "when", "where", "which", "does", "have", "with", "for", "the", "and", "how", "can", "are", "is", "why"}]
    best_score, best_answer = 0, ""
    for stored_q, stored_a in records:
        stored_norm = normalize_text(stored_q)
        score = 0
        if q_norm and q_norm in stored_norm:
            score += 12
        for token in q_tokens:
            if _word_match(stored_norm, token):
                score += 3
        if score > best_score:
            best_score, best_answer = score, stored_a
    # Avoid returning a weakly related Q&A answer.
    return best_answer if best_score >= 3 else ""


# =========================================================
# MAIN SEARCH - LANGUAGE AWARE
# =========================================================

def search_knowledge(question, response_language="auto", original_question=None):
    """Search the local agriculture knowledge file and answer in the chosen language.

    `question` may be a frontend-enriched retrieval query. `original_question`
    preserves the farmer's actual wording for language detection and topic intent.
    """
    question = (question or "").strip()
    original_question = (original_question or question).strip()

    if not question and not original_question:
        return "Please enter an agriculture-related question."

    retrieval_query = question or original_question
    combined_query = original_question
    if normalize_text(retrieval_query) != normalize_text(original_question):
        combined_query = original_question + " " + retrieval_query

    language = detect_response_language(original_question, response_language)
    knowledge = load_knowledge()
    if not knowledge:
        return "Agriculture knowledge is currently unavailable."

    sections = parse_sections(knowledge)
    crop = detect_crop(combined_query)
    question_type = detect_question_type(combined_query)

    print(
        f"[AgriGpt] Question={original_question} | "
        f"Language={language} | Crop={crop} | Type={question_type}"
    )

    answer = find_best_section(sections, crop, question_type, combined_query)

    # Direct Q&A records are more precise than broad topic paragraphs.
    qa_answer = find_best_qa(knowledge, combined_query) if language == "english" else ""
    if qa_answer:
        return qa_answer

    if language == "tamil":
        return get_tamil_answer(crop, question_type, answer)

    if language == "tanglish":
        tamil_answer = get_tamil_answer(crop, question_type, answer)
        return tamil_to_tanglish(tamil_answer)

    if answer:
        return answer

    answer = general_agriculture_search(sections, combined_query)
    if answer:
        return answer

    return (
        "Sorry, I could not find specific information for this agriculture question. "
        "Please ask about crops, soil, fertilizer, irrigation, pests, diseases, "
        "seeds, harvesting, storage, or farming practices."
    )
