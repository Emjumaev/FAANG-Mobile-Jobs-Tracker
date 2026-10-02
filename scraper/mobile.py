"""Mobile-engineering role classifier.

classify(title) -> (platform, level) for a mobile software job, or None for
everything else. Two gates, then two labels:

1. The title must name a mobile platform/technology (iOS, Android, Flutter,
   React Native, Kotlin Multiplatform, "Mobile", ...).
2. It must read like an engineering role (engineer / developer / SWE / intern
   / tech lead / engineering manager ...) and NOT like a product, design,
   sales, marketing, hardware, telecom or IT role that merely mentions mobile.

platform: "iOS", "Android", "iOS & Android" (both named), "Cross-platform"
          (Flutter / React Native / KMP / .NET MAUI ...), or "Mobile" (generic)
level:    "Intern", "Entry", "Mid", "Senior", "Staff+", "Manager"
"""
import re


def _rx(pattern):
    return re.compile(pattern, re.IGNORECASE)


# "iPhone"/"iPad" alone are left out on purpose: titles that use the device
# name instead of "iOS" are almost always hardware roles (Apple).
IOS_RE = _rx(r"\bios\b|\bipados\b|\bswift(ui)?\b|objective[- ]?c|"
             r"\bmacos\b|\bwatchos\b|\btvos\b|\bvisionos\b|\bxcode\b|\buikit\b|"
             r"apple platforms?")
ANDROID_RE = _rx(r"\bandroid\b|\bjetpack\b")
CROSS_RE = _rx(r"\bflutter\b|react[- ]native|kotlin multiplatform|\bkmp\b|\bkmm\b|"
               r"\bxamarin\b|\.net maui|\bmaui\b|\bionic\b|\bcapacitor\b|"
               r"\bcordova\b|\bexpo\b|cross[- ]platform mobile|"
               r"mobile cross[- ]platform")
MOBILE_RE = _rx(r"\bmobile\b")

# Kotlin on its own is just as often a backend language; only count it as
# Android when the title also says mobile/app/Android.
KOTLIN_ONLY_RE = _rx(r"\bkotlin\b")
KOTLIN_MOBILE_CONTEXT_RE = _rx(r"\bandroid\b|\bmobile\b|\bapps?\b|multiplatform|\bkmp\b|\bkmm\b")

# What an engineering job title looks like.
ENGINEER_RE = _rx(
    r"engineer|developer|\bdev\b|programmer|\bswe\b|\bsde\b|\bsdet\b|"
    r"architect|software|intern|co-?op|tech(nical)? lead|team lead|"
    r"engineering manager|\bengineering\b|working student|werkstudent|"
    r"\bcoder\b|technologist|member of technical staff|\bmts\b|"
    # non-English titles (Lyft/Doctolib/Zalando post localized variants)
    r"ing[eé]nieur|entwickler|d[eé]veloppeur|desarrollador|desenvolvedor|"
    r"ingeniero|engenheiro|sviluppatore|programista|ontwikkelaar")

# Roles that mention a mobile platform but aren't mobile software engineering.
EXCLUDE_RE = _rx(
    # non-engineering functions
    r"product manager|product management|program manager|project manager|"
    r"product owner|\bdesigner\b|\bdesign\b|\bux\b|researcher|\bresearch\b|"
    r"sales|marketing|growth|recruit|sourcer|talent|account (manager|executive)|"
    r"partner(ship)?s?\b|business develop|customer|support|success|"
    r"solutions? (engineer|architect|consultant)|consultant|\banalyst\b|"
    r"writer|content|editor|evangelist|advocate|community|operations|"
    r"finance|legal|counsel|compliance|\bhr\b|people|"
    # hardware / silicon / telecom / IT
    r"hardware|mechanical|electrical|silicon|\basic\b|\bsoc\b|\brf\b|"
    r"antenna|cellular|\b[45]g\b|\blte\b|baseband|modem|telecom|carrier|"
    r"\bhw\b|analog|power systems|charging|sensing|validation engineer|"
    r"mobile robot|mobile manipulat|robotics|"
    r"mobile network|network engineer|t-mobile|\bit\b|it systems|"
    r"mobile device management|\bmdm\b|endpoint|help ?desk|"
    # SWIFT the banking network, not Swift the language
    r"swift (payments?|network|messag|transfers?|gpi)|"
    # web / backend that only borrows the word
    r"mobile web|\bbackend\b|back-end|server[- ]side|data engineer|"
    r"\bsre\b|site reliability|devops|infrastructure engineer")

# Titles where an exclusion word is clearly part of a mobile-engineering
# role name; these skip EXCLUDE_RE ("Mobile Platform Engineer, Developer
# Infrastructure", "iOS Engineer - Growth", "Android Engineer, Support Tools").
HARD_INCLUDE_RE = _rx(
    r"(ios|android|mobile|flutter|react[- ]native)[\s,/&-]+(software )?"
    r"(engineer|developer|programmer|swe|sde|intern)")

LEVELS = [
    ("Intern", _rx(r"\bintern(ship)?\b|\bco-?op\b|working student|werkstudent")),
    ("Manager", _rx(r"\bmanager\b|\bdirector\b|\bhead of\b|\bvp\b|vice president|"
                    r"\bchief\b")),
    ("Staff+", _rx(r"\bstaff\b|\bprincipal\b|distinguished|\bfellow\b|\barchitect\b|"
                   r"\bsr\.? ?staff\b|\blead\b|\biv\b|\bv\b|\bl[5-8]\b|\be[5-8]\b")),
    ("Senior", _rx(r"\bsenior\b|\bsr\.?\b|\bsr\b|\biii\b|\bl4\b|\be4\b")),
    ("Entry", _rx(r"\bjunior\b|\bjr\.?\b|new grad|graduate|entry|early career|"
                  r"\bassociate\b|university|campus|\bi\b|\b1\b|apprentice|"
                  r"\btrainee\b")),
]


def _platform(title):
    ios = bool(IOS_RE.search(title))
    cross = bool(CROSS_RE.search(title))
    android = bool(ANDROID_RE.search(title))
    if not android and not cross and KOTLIN_ONLY_RE.search(title):
        android = bool(KOTLIN_MOBILE_CONTEXT_RE.search(title))
    if ios and android:
        return "iOS & Android"
    if ios:
        return "iOS"
    if android:
        return "Android"
    if cross:
        return "Cross-platform"
    if MOBILE_RE.search(title):
        return "Mobile"
    return None


def _level(title):
    for name, pattern in LEVELS:
        if pattern.search(title):
            return name
    return "Mid"


def classify(title):
    platform = _platform(title)
    if not platform:
        return None
    if not ENGINEER_RE.search(title):
        return None
    if EXCLUDE_RE.search(title) and not HARD_INCLUDE_RE.search(title):
        return None
    return platform, _level(title)
