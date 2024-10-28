import os
import yaml
import requests


def load_protocol(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def get_branch_protection_rules(owner, repo, branch, headers):
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}/protection"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def verify_branch_protection(protocol, branch_protection):
    required_reviewers = protocol["protocol"]["required_reviewers"]
    allow_force_push = protocol["protocol"]["allow_force_push"]
    allow_bypass = protocol["protocol"]["allow_bypass"]

    results = {
        "required_reviewers": branch_protection["required_pull_request_reviews"][
            "required_approving_review_count"
        ]
        >= required_reviewers,
        "allow_force_push": branch_protection["allow_force_pushes"]["enabled"]
        == allow_force_push,
        "allow_bypass": branch_protection["enforce_admins"]["enabled"] == allow_bypass,
    }
    return results


def report_results(results):
    for key, value in results.items():
        status = "PASS" if value else "FAIL"
        print(f"{key}: {status}")


if __name__ == "__main__":
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_OWNER = "your-repo-owner"
    REPO_NAME = "your-repo-name"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    protocol = load_protocol("protocol.yml")
    branch_protection = get_branch_protection_rules(
        REPO_OWNER, REPO_NAME, "master", headers
    )
    verification_results = verify_branch_protection(protocol, branch_protection)
    report_results(verification_results)
