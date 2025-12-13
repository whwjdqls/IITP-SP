from google import genai
import sys

# ⚠️ 실제로는 환경변수 사용 권장
client = genai.Client(api_key="AIzaSyBz420tptEuhbGHUyTuQ5Q9_WtzL9cYid0")

# stdin으로 C++에서 프롬프트를 받음
prompt = sys.stdin.read()

response = client.models.generate_content(
    model="gemma-3-27b-it",
    contents=prompt,
)

print(response.text)
