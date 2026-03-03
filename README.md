# GatedPlans Example - Learning Lab

A Snowflake Native App that demonstrates **feature gating based on Marketplace pricing plans**. The app uses `SYSTEM$GET_PURCHASE_ATTRIBUTES()` to detect a consumer's active plan and control which features they can access.

## What It Does

The app presents three trophy cup icons (Bronze, Silver, Gold) and three corresponding buttons (Standard, Premium, Enterprise). When a user clicks a button:

- **If their plan covers that tier** - the corresponding cup icon flashes with a CSS animation and a success message is shown.
- **If their plan does not cover that tier** - an upgrade prompt is displayed, inviting them to contact their account team or upgrade via the Marketplace listing.

### Plan Entitlements

| Plan | Bronze Cup | Silver Cup | Gold Cup |
|------|-----------|-----------|---------|
| Standard | Yes | No | No |
| Premium | Yes | Yes | No |
| Enterprise | Yes | Yes | Yes |

Plans are cumulative - higher tiers include all features from lower tiers.

### Demo Mode

Since `SYSTEM$GET_PURCHASE_ATTRIBUTES()` only returns data when the app is installed via a Marketplace listing with pricing plans, the app includes a **sidebar demo selector** that lets you simulate different plans. When a live Marketplace plan is detected, it takes priority over the demo selector.

## Project Structure

```
learning_lab_gated_plans/
├── README.md                  # This file
├── manifest.yml               # Native App manifest (version, setup script, default Streamlit)
├── setup_script.sql           # Creates schema, Streamlit object, and grants
├── pricing_plans.yml          # Reference file for Marketplace plan definitions
└── streamlit/
    └── gated_plans_app.py     # Streamlit UI with buttons, icons, gating logic
```

### File Details

- **`manifest.yml`** - Declares the app version (v1), the setup script, and the default Streamlit entry point (`gated_plans_app.gated_plans_dashboard`).
- **`setup_script.sql`** - Runs on install. Creates an application role (`app_public`), a schema (`gated_plans_app`), the Streamlit object, and grants usage to the app role.
- **`pricing_plans.yml`** - Reference only. Documents the three pricing plans (Standard, Premium, Enterprise) that would be configured in Provider Studio when creating a Marketplace listing. These cannot be created via SQL.
- **`streamlit/gated_plans_app.py`** - The main application. Contains the UI layout, CSS animations, plan detection logic, entitlement checks, and upgrade prompts.

## How Feature Gating Works

### Live Mode (Marketplace)

When installed via a Marketplace listing with pricing plans configured:

```python
session.sql("SELECT SYSTEM$GET_PURCHASE_ATTRIBUTES()").collect()
# Returns JSON: {"plan_name": "PREMIUM"}
```

The app parses the `plan_name` attribute and uses it to determine feature access.

### Related System Functions

| Function | Purpose |
|----------|---------|
| `SYSTEM$GET_PURCHASE_ATTRIBUTES()` | Returns the consumer's active plan attributes as JSON |
| `SYSTEM$IS_LISTING_PURCHASED()` | Returns TRUE if the consumer has an active purchase |
| `SYSTEM$IS_LISTING_TRIAL()` | Returns TRUE if the consumer is on a trial |

## Deployment

### Prerequisites

- ACCOUNTADMIN role (or a role with CREATE APPLICATION PACKAGE privilege)
- A Snowflake account (this was deployed to `sfsenorthamerica-demo191`)

### Step 1: Create a Staging Database and Stage

The staging database holds the app files. It must be separate from the application package.

```sql
CREATE DATABASE IF NOT EXISTS GATEDPLANS_STAGING;
CREATE SCHEMA IF NOT EXISTS GATEDPLANS_STAGING.STAGE_CONTENT;
CREATE OR REPLACE STAGE GATEDPLANS_STAGING.STAGE_CONTENT.APP_CODE
  DIRECTORY = (ENABLE = TRUE);
```

### Step 2: Upload Files to Stage

```sql
PUT 'file:///path/to/learning_lab_gated_plans/manifest.yml'
  @GATEDPLANS_STAGING.STAGE_CONTENT.APP_CODE/
  OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

PUT 'file:///path/to/learning_lab_gated_plans/setup_script.sql'
  @GATEDPLANS_STAGING.STAGE_CONTENT.APP_CODE/
  OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

PUT 'file:///path/to/learning_lab_gated_plans/streamlit/gated_plans_app.py'
  @GATEDPLANS_STAGING.STAGE_CONTENT.APP_CODE/streamlit/
  OVERWRITE=TRUE AUTO_COMPRESS=FALSE;
```

### Step 3: Create the Application Package

```sql
CREATE APPLICATION PACKAGE GATEDPLANS_EXAMPLE_PKG
  COMMENT = 'GatedPlans Example - Feature gating demo with pricing plans';
```

### Step 4: Register a Version

If release channels are enabled (default on newer accounts):

```sql
ALTER APPLICATION PACKAGE GATEDPLANS_EXAMPLE_PKG
  REGISTER VERSION v1
  USING '@GATEDPLANS_STAGING.STAGE_CONTENT.APP_CODE';
```

If release channels are not enabled:

```sql
ALTER APPLICATION PACKAGE GATEDPLANS_EXAMPLE_PKG
  ADD VERSION v1
  USING '@GATEDPLANS_STAGING.STAGE_CONTENT.APP_CODE';
```

### Step 5: Create the Application

For same-account development/testing (installs directly from the stage):

```sql
CREATE APPLICATION "GatedPlans Example"
  FROM APPLICATION PACKAGE GATEDPLANS_EXAMPLE_PKG
  USING '@GATEDPLANS_STAGING.STAGE_CONTENT.APP_CODE';
```

### Step 6: Access the App

Open Snowsight and navigate to **Data Products > Apps > GatedPlans Example**. The Streamlit dashboard loads automatically.

## Updating the App

After making code changes:

```sql
-- Re-upload changed files
PUT 'file:///path/to/learning_lab_gated_plans/streamlit/gated_plans_app.py'
  @GATEDPLANS_STAGING.STAGE_CONTENT.APP_CODE/streamlit/
  OVERWRITE=TRUE AUTO_COMPRESS=FALSE;

-- Upgrade the application
ALTER APPLICATION "GatedPlans Example" UPGRADE
  USING '@GATEDPLANS_STAGING.STAGE_CONTENT.APP_CODE';
```

## Configuring Marketplace Pricing Plans

Pricing plans are configured in **Provider Studio** (not via SQL) when creating a Marketplace listing. The `pricing_plans.yml` file in this project documents the plan structure for reference.

### Steps in Provider Studio

1. Navigate to **Data Products > Provider Studio > Listings**
2. Create a new listing for the `GATEDPLANS_EXAMPLE_PKG` application package
3. Under **Pricing**, add three plans:
   - **Standard** (Free) - `plan_name: STANDARD`
   - **Premium** (Free) - `plan_name: PREMIUM`
   - **Enterprise** (Free) - `plan_name: ENTERPRISE`
4. Each plan has a `purchase_attributes` object with a `plan_name` key that the app reads via `SYSTEM$GET_PURCHASE_ATTRIBUTES()`

## Cleanup

To remove the app and all related objects:

```sql
DROP APPLICATION IF EXISTS "GatedPlans Example";
DROP APPLICATION PACKAGE IF EXISTS GATEDPLANS_EXAMPLE_PKG;
DROP DATABASE IF EXISTS GATEDPLANS_STAGING;
```

## Snowflake Objects Created

| Object | Type | Purpose |
|--------|------|---------|
| `GATEDPLANS_STAGING` | Database | Holds staged app files |
| `GATEDPLANS_STAGING.STAGE_CONTENT.APP_CODE` | Stage | Internal stage for app code |
| `GATEDPLANS_EXAMPLE_PKG` | Application Package | Defines the distributable app |
| `GatedPlans Example` | Application | Installed instance of the app |
