import os
import yaml
import requests
import json
from datetime import datetime


def load_protocol(file_path):
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Protocol file not found: {file_path}")
    except yaml.YAMLError:
        raise ValueError(f"Error parsing the protocol file: {file_path}")


def get_branch_protection_rules(owner, repo, branch, headers):
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}/protection"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Error fetching branch protection rules: {e}")


def verify_branch_protection(protocol, branch_protection):
    results = {}
    for rule in protocol["protocol"]["branch_protection_rules"]:
        branch = rule["branch"]
        required_reviewers = rule["required_reviewers"]
        allow_force_push = rule["allow_force_push"]
        allow_bypass = rule["allow_bypass"]

        branch_protection = get_branch_protection_rules(
            protocol["protocol"]["Github"]["organization"],
            protocol["protocol"]["Github"]["project"],
            branch,
            headers,
        )

        results[branch] = {
            "required_reviewers": branch_protection["required_pull_request_reviews"][
                "required_approving_review_count"
            ]
            >= required_reviewers,
            "allow_force_push": branch_protection["allow_force_pushes"]["enabled"]
            == allow_force_push,
            "allow_bypass": branch_protection["enforce_admins"]["enabled"] == allow_bypass,
        }
    return results


def report_results(results, format="text"):
    report = {
        "verification_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "repository": f"{REPO_OWNER}/{REPO_NAME}",
        "results": results,
    }

    if format == "json":
        with open("verification_report.json", "w") as file:
            json.dump(report, file, indent=4)
    elif format == "html":
        with open("verification_report.html", "w") as file:
            file.write("<html><body><h1>Verification Report</h1>")
            file.write(f"<p>Date: {report['verification_date']}</p>")
            file.write(f"<p>Repository: {report['repository']}</p>")
            file.write("<ul>")
            for branch, branch_results in results.items():
                file.write(f"<li>Branch: {branch}<ul>")
                for key, value in branch_results.items():
                    status = "PASS" if value else "FAIL"
                    file.write(f"<li>{key}: {status}</li>")
                file.write("</ul></li>")
            file.write("</ul></body></html>")
    elif format == "markdown":
        with open("verification_report.md", "w") as file:
            file.write("# Verification Report\n")
            file.write(f"**Date:** {report['verification_date']}\n")
            file.write(f"**Repository:** {report['repository']}\n")
            for branch, branch_results in results.items():
                file.write(f"## Branch: {branch}\n")
                for key, value in branch_results.items():
                    status = "PASS" if value else "FAIL"
                    file.write(f"- **{key}:** {status}\n")
    else:
        for branch, branch_results in results.items():
            print(f"Branch: {branch}")
            for key, value in branch_results.items():
                status = "PASS" if value else "FAIL"
                print(f"{key}: {status}")


if __name__ == "__main__":
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        raise EnvironmentError("GITHUB_TOKEN environment variable is not set")

    REPO_OWNER = "your-repo-owner"
    REPO_NAME = "your-repo-name"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        protocol = load_protocol("protocol.yml")
        verification_results = verify_branch_protection(protocol, headers)
        report_results(verification_results, format="json")
    except Exception as e:
        print(f"Error: {e}")
