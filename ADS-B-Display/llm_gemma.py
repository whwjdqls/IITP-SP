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

# UTF-8로 안전하게 출력 (이모지 등 유니코드 문자 처리)
output_text = str(response.text)
try:
    # UTF-8로 인코딩해서 stdout.buffer에 직접 쓰기
    sys.stdout.buffer.write(output_text.encode('utf-8', errors='replace'))
    sys.stdout.buffer.write(b'\n')
    sys.stdout.buffer.flush()
except (AttributeError, UnicodeEncodeError):
    # sys.stdout.buffer가 없거나 인코딩 실패 시 대체 방법
    # 문제가 있는 문자를 제거하거나 치환
    safe_text = output_text.encode('ascii', errors='replace').decode('ascii')
    print(safe_text, flush=True)

