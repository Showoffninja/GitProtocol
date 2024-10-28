import os
import pytest
import requests
import yaml
from unittest.mock import patch, mock_open
from gitverify import load_protocol, get_branch_protection_rules, verify_branch_protection, report_results


def test_load_protocol_valid_file():
    protocol_content = """
    protocol:
      required_reviewers: 2
      allow_force_push: False
      allow_bypass: False
    """
    with patch("builtins.open", mock_open(read_data=protocol_content)):
        protocol = load_protocol("protocol.yml")
        assert protocol["protocol"]["required_reviewers"] == 2
        assert protocol["protocol"]["allow_force_push"] is False
        assert protocol["protocol"]["allow_bypass"] is False


def test_load_protocol_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_protocol("non_existent_protocol.yml")


def test_load_protocol_invalid_format():
    invalid_protocol_content = "invalid_yaml_content"
    with patch("builtins.open", mock_open(read_data=invalid_protocol_content)):
        with pytest.raises(ValueError):
            load_protocol("protocol.yml")


def test_get_branch_protection_rules_success():
    owner = "test_owner"
    repo = "test_repo"
    branch = "master"
    headers = {"Authorization": "token test_token"}
    mock_response = {
        "required_pull_request_reviews": {"required_approving_review_count": 2},
        "allow_force_pushes": {"enabled": False},
        "enforce_admins": {"enabled": True},
    }
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = lambda: None
        branch_protection = get_branch_protection_rules(owner, repo, branch, headers)
        assert branch_protection["required_pull_request_reviews"]["required_approving_review_count"] == 2
        assert branch_protection["allow_force_pushes"]["enabled"] is False
        assert branch_protection["enforce_admins"]["enabled"] is True


def test_get_branch_protection_rules_network_error():
    owner = "test_owner"
    repo = "test_repo"
    branch = "master"
    headers = {"Authorization": "token test_token"}
    with patch("requests.get", side_effect=requests.exceptions.RequestException):
        with pytest.raises(ConnectionError):
            get_branch_protection_rules(owner, repo, branch, headers)


def test_verify_branch_protection():
    protocol = {
        "protocol": {
            "branch_protection_rules": [
                {
                    "branch": "main",
                    "required_reviewers": 2,
                    "allow_force_push": False,
                    "allow_bypass": False,
                },
                {
                    "branch": "release",
                    "required_reviewers": 1,
                    "allow_force_push": False,
                    "allow_bypass": False,
                },
            ],
            "required_status_checks": [
                {
                    "branch": "main",
                    "checks": ["build", "test"],
                },
                {
                    "branch": "release",
                    "checks": ["build"],
                },
            ],
            "code_owners": [
                {
                    "path": "/",
                    "owners": ["@myOrg/reviewers"],
                },
                {
                    "path": "/src",
                    "owners": ["@myOrg/developers"],
                },
            ],
        }
    }
    branch_protection = {
        "required_pull_request_reviews": {"required_approving_review_count": 2},
        "allow_force_pushes": {"enabled": False},
        "enforce_admins": {"enabled": False},
    }
    results = verify_branch_protection(protocol, branch_protection)
    assert results["main"]["required_reviewers"] is True
    assert results["main"]["allow_force_push"] is True
    assert results["main"]["allow_bypass"] is True
    assert results["release"]["required_reviewers"] is True
    assert results["release"]["allow_force_push"] is True
    assert results["release"]["allow_bypass"] is True


def test_report_results_text(capsys):
    results = {
        "main": {
            "required_reviewers": True,
            "allow_force_push": False,
            "allow_bypass": True,
        },
        "release": {
            "required_reviewers": True,
            "allow_force_push": False,
            "allow_bypass": True,
        },
    }
    report_results(results, format="text")
    captured = capsys.readouterr()
    assert "Branch: main" in captured.out
    assert "required_reviewers: PASS" in captured.out
    assert "allow_force_push: FAIL" in captured.out
    assert "allow_bypass: PASS" in captured.out
    assert "Branch: release" in captured.out
    assert "required_reviewers: PASS" in captured.out
    assert "allow_force_push: FAIL" in captured.out
    assert "allow_bypass: PASS" in captured.out


def test_report_results_json():
    results = {
        "main": {
            "required_reviewers": True,
            "allow_force_push": False,
            "allow_bypass": True,
        },
        "release": {
            "required_reviewers": True,
            "allow_force_push": False,
            "allow_bypass": True,
        },
    }
    report_results(results, format="json")
    with open("verification_report.json", "r") as file:
        report = json.load(file)
        assert report["repository"] == "your-repo-owner/your-repo-name"
        assert report["results"]["main"]["required_reviewers"] is True
        assert report["results"]["main"]["allow_force_push"] is False
        assert report["results"]["main"]["allow_bypass"] is True
        assert report["results"]["release"]["required_reviewers"] is True
        assert report["results"]["release"]["allow_force_push"] is False
        assert report["results"]["release"]["allow_bypass"] is True


def test_report_results_html():
    results = {
        "main": {
            "required_reviewers": True,
            "allow_force_push": False,
            "allow_bypass": True,
        },
        "release": {
            "required_reviewers": True,
            "allow_force_push": False,
            "allow_bypass": True,
        },
    }
    report_results(results, format="html")
    with open("verification_report.html", "r") as file:
        content = file.read()
        assert "<h1>Verification Report</h1>" in content
        assert "<li>Branch: main<ul>" in content
        assert "<li>required_reviewers: PASS</li>" in content
        assert "<li>allow_force_push: FAIL</li>" in content
        assert "<li>allow_bypass: PASS</li>" in content
        assert "<li>Branch: release<ul>" in content
        assert "<li>required_reviewers: PASS</li>" in content
        assert "<li>allow_force_push: FAIL</li>" in content
        assert "<li>allow_bypass: PASS</li>" in content


def test_report_results_markdown():
    results = {
        "main": {
            "required_reviewers": True,
            "allow_force_push": False,
            "allow_bypass": True,
        },
        "release": {
            "required_reviewers": True,
            "allow_force_push": False,
            "allow_bypass": True,
        },
    }
    report_results(results, format="markdown")
    with open("verification_report.md", "r") as file:
        content = file.read()
        assert "# Verification Report" in content
        assert "## Branch: main" in content
        assert "- **required_reviewers:** PASS" in content
        assert "- **allow_force_push:** FAIL" in content
        assert "- **allow_bypass:** PASS" in content
        assert "## Branch: release" in content
        assert "- **required_reviewers:** PASS" in content
        assert "- **allow_force_push:** FAIL" in content
        assert "- **allow_bypass:** PASS" in content
