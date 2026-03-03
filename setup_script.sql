-- =============================================================
-- GatedPlans Example - Setup Script
-- Creates the schema and Streamlit app for the Native App
-- =============================================================

CREATE APPLICATION ROLE IF NOT EXISTS app_public;

CREATE SCHEMA IF NOT EXISTS gated_plans_app;
GRANT USAGE ON SCHEMA gated_plans_app TO APPLICATION ROLE app_public;

CREATE OR REPLACE STREAMLIT gated_plans_app.gated_plans_dashboard
  FROM '/streamlit'
  MAIN_FILE = '/gated_plans_app.py';

GRANT USAGE ON STREAMLIT gated_plans_app.gated_plans_dashboard TO APPLICATION ROLE app_public;
