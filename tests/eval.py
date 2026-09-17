"""
Accuracy evaluation harness for the Gym FAQ Chatbot.

Each case is (user question, set of acceptable FAQ ids) or None when there is
no relevant FAQ and the bot should decline to answer.

Run from the project root:
    python tests/eval.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.chatbot import FAQChatbot  # noqa: E402
from config.settings import FAQ_FILE, SIMILARITY_THRESHOLD  # noqa: E402

# (query, acceptable FAQ ids; None = should return no match)
CASES = [
    ("do you have yoga", {28}),
    ("spinning", {28}),
    ("pilates", {28}),
    ("crossfit", {28}),
    ("hiit", {28}),
    ("treadmill", {23, 54}),
    ("cardio", {23}),
    ("cable machine", {23}),
    ("squat rack", {23}),
    ("locker", {24}),
    ("parking", {27}),
    ("towel", {25, 55}),
    ("guest pass", {41, 49}),
    ("refund", {56, 19}),
    ("cancel membership", {19}),
    ("quit", {53}),
    ("installments", {34}),
    ("invoice", {35}),
    ("corporate", {36}),
    ("clean", {37}),
    ("covid", {38}),
    ("corona", {38}),
    ("insurance", {40}),
    ("safety", {38, 40}),
    ("first aid", {40}),
    ("behavior", {43}),
    ("noise", {43}),
    ("music", {43}),
    ("merchandise", {45}),
    ("supplements", {45}),
    ("fitness assessment", {46}),
    ("diet", {44}),
    ("how to lose weight", {44, None}),
    ("protein", {45}),
    ("student discount", None),
    ("personal trainer cost", {30, 47}),
    ("kids allowed", None),
    ("age limit", None),
    ("timings", {20}),
    ("what time do you close", {20, 13, 14}),
    ("weekend", {21}),
    ("holiday", {21}),
    ("24/7 access", {22}),
    ("night access", {22}),
    ("trainer", {12}),
    ("member", {11}),
    ("discount", {36, 45}),
    ("join", {51}),
    ("register", {51}),
    ("wifi", None),
    ("cafeteria", None),
    ("what classes do you have", {28}),
    ("classes", {28}),
    ("facilities", {23}),
    ("cost", {47}),
    ("price", {47}),
    ("membership options", {15}),
    ("plans and prices", {15, 47}),
    ("cheap plan", {15, 47}),
    # regressions that must keep working
    ("hey mate", {6}),
    ("tell me about gym", {7, 8, 9, 10}),
    ("what are your gym timings", {20}),
    ("asdfgh jklmn", None),
]


def main():
    chatbot = FAQChatbot(FAQ_FILE)
    passed = 0
    failures = []

    for query, expected in CASES:
        response = chatbot.get_response(query, top_k=1, threshold=SIMILARITY_THRESHOLD)
        if response["status"] == "success":
            match_id = response["faq_id"]
        else:
            match_id = None

        if expected is None:
            ok = match_id is None
        else:
            ok = match_id in expected

        if ok:
            passed += 1
        else:
            failures.append((query, match_id, expected))

    total = len(CASES)
    accuracy = passed / total * 100

    print("\n" + "=" * 62)
    print(f"EVAL RESULT: {passed}/{total} correct ({accuracy:.1f}%)")
    print("=" * 62)
    if failures:
        print("\nFailures:")
        for query, got, expected in failures:
            print(f"  {query!r:30s} got={got}  expected={expected}")
    else:
        print("\nAll cases passed!")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
