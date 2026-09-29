[![MIT License](https://img.shields.io/github/license/bcgov/quickstart-openshift.svg)](/LICENSE)
[![Lifecycle](https://img.shields.io/badge/Lifecycle-Experimental-339999)](https://github.com/bcgov/repomountie/blob/master/doc/lifecycle-badges.md)
[![Merge](https://github.com/bcgov/quickstart-openshift/actions/workflows/merge.yml/badge.svg)](https://github.com/bcgov/quickstart-openshift/actions/workflows/merge.yml)
[![Analysis](https://github.com/bcgov/quickstart-openshift/actions/workflows/analysis.yml/badge.svg)](https://github.com/bcgov/quickstart-openshift/actions/workflows/analysis.yml)
[![Scheduled](https://github.com/bcgov/quickstart-openshift/actions/workflows/scheduled.yml/badge.svg)](https://github.com/bcgov/quickstart-openshift/actions/workflows/scheduled.yml)

# CHEFS to JIRA

## Update JIRA issues with information from CHEFS form Submissions

This repository facilitates populating on prem JIRA tickets using CHEFS submissions.

## How it works

When CHEFS submits it sends an email. The JIRA Project has Email Requests configured so that when it receives an email a new ticket is created.

The github action "sync.yml" uses github environment variables to run on a schedule. It calls main.py, which contains the bulk of the projects logic. The script:

1. Checks configured on-prem JIRA for new submissions

   For each found submission that still requires work:

2. Gets submission attachments from CHEFS.

3. Uses the CHEFS CDOGS Template to generate a CDOGS document using the submission answers.

4. For each CHEFS form question it checks for configuration mapping the answer to a JIRA field.

5. Updates JIRA ticket with CDOGS PDF/Word attachment, CHEFS answers (as configured), and adds any CHEFS user-submitted attachments.

6. Comments on the ticket that the ticket was pre-populated by Chefs-To-Jira

## Requirements

The following things are needed to deploy this to a new environment:

- A service account account with JIRA Credentials with API read/write permission.

- JIRA Project "Email Requests" functionality configured to generate new tickets when an email is received from the CHEFS submission. (This can use the email protocol Microsoft Graph API)

- A CHEFS form with API integration enabled, and its API Key

## Setup

This project can be fairly quickly rolled out to new business areas given they meet the requirements. The process for doing so is:

1. Create a new github Environment in this project (i.e. prod-JIRAPROJECT).

- The script setup_new_env_and_sync/setup_new_github_environment.ps1 can be used to quickly create the github secrets/variables.
- The example config file setup_new_env_and_sync/environmentTemplate.example.json specifies all environment secrets/variables.

The environment secrets/variables specify:

- Which CDOGS, CHEFS, and JIRA on-prem to connect to and their credentials

- Which JIRA Project, and optionally component to look for submissions for.

- Log level

2. Update the CHEFS form to leverage and jira field mappings. These are fields in the CHEFS form where its answers should be put into specific jira fields.

- This has only been tested with Text and Select form "component", but may work with others.

- To map a chefs component to a jira form, add a "Custom Properties" key value pair on the Text or Select components API tab. The key is always "JiraMapping". Value is the JIRA field.

- Note that in JIRA there are both true names for fields, and display names - the script tries to match the JiraMapping first to the actual field name and then to the display name. Field names are case sensitive, though this script will try and find a case insensitive one if an exact match is not found.

3. Duplicate and rename to create a new sync.yml with a project specific name (i.e. .github/workflows/sync-JIRAPROJECT.yml). Change the following three attribute values in the new sync.yml:

- Modify "name" to match your project (i.e. Sync prd-ministry-project)

- Modify the "environment" to match the environment you created in step 1.

- Optionally, modify the frequency the sync runs by changing the "cron:" value. This uses "cron" formatting; google is helpful, "_/10 _ \* \* \*" is every 10 minutes.

## Code Layout

- .github/workflows contains configuration required to host this application in github.

- src folder contains all production code

- src/main.py is the script that handles most business logic. References /src's \_helpers heavily.

- src/utilities folder contains logging and file functions used mostly in automated testing.

- src/\*\_helpers folders are named after the system's API they provide functionality for.

- setup_new_env_and_sync folder assists in quickly rolling out for a new project.

- tests folder contains automated testing support, heavily referencing src, and has a seperate readme.

## Credits

- Peter Platten and Heather Hay were primary developers, additionally

- The Optimize Team's Service Designers (Chris Stewart, Kiera Wilkinson, Harsha Kalra) gathered user requirements from the WLRS Privacy Team.

- Product Owner Bonny Hastings provided leadership and connections

- Derek Roberts shared Git knowledge, and advice on modern practices and AI use in development

- Paul Goodman was key with onboarding to the JIRA API

- Gary Wong and Jason Sherman assisted with onboarding to CHEFS/CDOGS, and discovery around ESS.

- The Kilo code plugin for VS Code generated quite a lot of code - always reviewed and tested by a developer.

- This repository contains components from bcgov/quickstart-openshift, bcgov/quickstart-openshift-backends, and bcgov/copilot-instructions

## Library/Module/API Documentation

- CHEFS API - https://submit.digital.gov.bc.ca/app/api/v1/docs

- CDOGS API - https://cdogs.api.gov.bc.ca/api/v2/docs

- JIRA API - https://jira.readthedocs.io/api.html

- Github Actions - https://docs.github.com/en/actions
