import os
import requests
import google.generativeai as genai

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
PR_NUMBER    = os.environ["PR_NUMBER"]
REPO         = os.environ["REPO"]

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

def get_pr_diff():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    return requests.get(url, headers=headers, timeout=10).text

def review_with_gemini(diff):
    prompt = f"""You are an expert code reviewer. Review this git diff:

1. **Summary** — what changed
2. **Issues** — bugs, security problems, bad practices
3. **Suggestions** — specific improvements with code examples
4. **Verdict** — Approve / Request Changes / Needs Discussion

Be concise and actionable. Diff:

{diff[:8000]}"""
    return model.generate_content(prompt).text

def post_comment(review):
    url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    requests.post(url, headers=headers, json={"body": f"## AI Code Review\n\n{review}"}, timeout=10)

if __name__ == "__main__":
    diff = get_pr_diff()
    review = review_with_gemini(diff)
    post_comment(review)
    print("Review posted!")

