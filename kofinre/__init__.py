"""KoFinRe-QA Framework — Korean Public Financial RFP Quality Analysis."""
__version__ = "2.0.0"

SMELL_CODES = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10"]
SMELL_NAMES = {
    "S1": "Non-atomic",
    "S2": "Incomplete",
    "S3": "Ambiguous",
    "S4": "WeakObligation",
    "S5": "MissingActor",
    "S6": "MissingQuant",
    "S7": "UndefinedAcronym",
    "S8": "CoordAmbiguity",
    "S9": "Passive",
    "S10": "Unverifiable",
}
SMELL_NAMES_KO = {
    "S1": "복합의무",
    "S2": "불완전",
    "S3": "모호어",
    "S4": "약한의무",
    "S5": "주체누락",
    "S6": "정량부재",
    "S7": "미정의약어",
    "S8": "범위모호",
    "S9": "수동표현",
    "S10": "검증불가",
}
