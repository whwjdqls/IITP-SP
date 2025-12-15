import json
import sys

from google import genai

# ⚠️ 실제로는 환경변수 사용 권장
client = genai.Client(api_key="AIzaSyBz420tptEuhbGHUyTuQ5Q9_WtzL9cYid0")

# stdin으로 C++에서 프롬프트를 받음
# prompt = sys.stdin.read()

# print("------------------------------------------------before response------------------------------------------------")
# response = client.models.generate_content(
#     model="gemini-1.3-mini",
#     contents=prompt,
# )
# print("------------------------------------------------after response------------------------------------------------")
# print(response.text[0])

# C++에서 전달한 args 사용
prompt = sys.argv[1]

response = client.models.generate_content(
    model="gemma-3-27b-it",
    contents=prompt,
)

# JSON 출력
# print(json.dumps({"text": response.text[0]}), flush=True)
print(response.text, flush=True)


# print("hello")
# import json

# print(json.dumps({"text": "hello from gemma"}))
# print("a")