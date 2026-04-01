import os
import requests
from groq import Groq

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
PR_NUMBER    = os.environ["PR_NUMBER"]
REPO         = os.environ["REPO"]

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def get_pr_diff():
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    return requests.get(url, headers=headers).text

def review_with_groq(diff):
    prompt = f"""You are an expert code reviewer. Review this git diff:

1. **Summary** — what changed
2. **Issues** — bugs, security problems, bad practices
3. **Suggestions** — specific improvements with code examples
4. **Verdict** — Approve / Request Changes / Needs Discussion

Be concise and actionable. Diff:

{diff[:8000]}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def post_comment(review):
    url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    requests.post(url, headers=headers,
        json={"body": f"## AI Code Review\n\n{review}"})

if __name__ == "__main__":
    diff = get_pr_diff()
    review = review_with_groq(diff)
    post_comment(review)
    print("Review posted!")