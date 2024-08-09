# Git Protocol Validation 1.0
===========================

This library is a method to validate the setup of a github project. It will compare the configuration of the project to the requirements for using Github as a source control system. The library will check the following:

GitHub is considered a ”Tool” in GAMP5 terminology:	

    ”Tools and systems supporting life cycles, IT processes, and infrastructure (rather than directly supporting product life cycle processes) are not themselves GxP regulated systems and should not be subject to specific validation but managed by routine company assessment and assurance practices and good IT practices”

Hence, we do not qualify GitHub itself. 


# Strategy for Verification of GitHub Configuration

Although we do not quality GitHub itself, we still need to consider if we use specific functionality of GitHub in a manner that supports our qualification effort. If so, we should verify this configuration. 

Any solution that is based on GitHub should be verified in the following way:

| Github Functionality                          | Approach to Github verification                  |
| --------------------------------------------- | ------------------------------------------------ |
| The repository feature (git) of Github must ensure immutable versioning of all objects (code, documentation, artifacts, etc.) stored in the repository. | Git will always ensure immutable versioning of all files stored. This is not a configurable behaviour, but fixed functionality, and hence no configuration verification is needed. |
| Enforce pull requests with at least one reviewer on all changes to the branch where compliance documentation is stored (e.g. master branch). | This is a configurable feature of GitHub. We should verify that this feature is enabled. |
| Pull requests must be retained indefinitely  | Pull request must never be deleted automatically, since they form the formal approvals of our compliance documentation in Git. Pull request are always kept by GitHub for as long as the project exists.  This is not a configurable behaviour, but fixed functionality, and hence no configuration verification is needed. |

# Manual Verification of GitHub Configuration

The following steps should be taken to verify the configuration of GitHub:

1. Log in to GitHub
2. Open the repository
3. Go to the settings of the repository
4. Go to the branch settings
5. Verify that the branch protection rules are set up to enforce pull requests with at least one reviewer on the branch where compliance documentation is stored (e.g. master branch).
6. Verify that the branch protection rules can't be bypassed, ensured by the setting: "Do not allow bypassing the above settings" is __NOT__ ticked
7. Verify that the "Allow force push" setting is __NOT__ ticked

Document these configurations in your verification plan documentation.

# Automated Verification of GitHub Configuration

Though the above manual verification steps are simple, they are prone to human error. It is recommended to automate the verification of the GitHub configuration. This can be done by using the GitHub API to retrieve the configuration of the repository. Our implementation introduces a protocol, which dictates the configuration requirements, named approvers, environments and approval gates needed to support the qualification effort. The protocol is implemented as a yaml file, which is stored in the repository. The protocol is then verified by the library.

## protocol.yml file

The protocol file is a yaml file that describes the configuration requirements of the repository. The file should be stored in the root of the repository. The file should have the following structure:

```yaml
protocol:
  approvers:
    - name: "Reviewer 1"
      email: "some@email.com"
    - name: "Reviewer 2"
      email: "some@email.com"

approval_gates:
  - branch: "master"
    required_approvers: 2
