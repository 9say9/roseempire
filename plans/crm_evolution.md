# Rose Empire CRM Evolution Plan: Hyper-Specific Command Center

## 1. Visual Identity: "Nebula Command"
The goal is to transition from a basic utility dashboard to a high-end B2B Command Center.

### Color Palette (Dark Mode)
- **Core Background:** `#0a0c10` (Deep Obsidian)
- **Surface/Cards:** `#161b22` (Gunmetal Grey)
- **Primary Accent:** `#6366f1` (Indigo Neon)
- **Secondary Accent:** `#06b6d4` (Cyan Electric)
- **Success/Positive:** `#10b981` (Emerald Green)
- **Warning/Urgent:** `#f59e0b` (Amber Gold)
- **Text High:** `#f9fafb` (Off-White)
- **Text Muted:** `#9ca3af` (Cool Grey)

### UI Enhancements
- **Glassmorphism:** Use `backdrop-filter: blur()` and subtle semi-transparent borders for cards.
- **Typography:** 'Inter' for UI, 'JetBrains Mono' for bot logs and blueprints.
- **Animations:** Smooth transitions for lead selection and hover effects on action buttons.
- **Layout:** 
    - Top: High-density KPI ribbons.
    - Mid-Left: Hyper-specific Pitch Control Center.
    - Mid-Right: Bot Command Suite (Sarah/James/Adeel).
    - Bottom: Full-width Lead Pipeline with status badges.

---

## 2. Hyper-Specific B2B Features
To make the CRM "realistic," we need to move beyond just "Scraped" and "Sent."

### Pipeline Stages (Status Evolution)
Replace the simple `pending/sent` with a professional sales funnel:
- `Lead Identified` $\rightarrow$ `Researching` $\rightarrow$ `Pitch Drafted` $\rightarrow$ `Contacted` $\rightarrow$ `In Negotiation` $\rightarrow$ `Closed/Contracted`.

### Data Enrichment Fields
Add the following tracking parameters to the pipeline view:
- **Lead Tier:** (S / A / B / C) based on facility size/repute.
- **Pain Point:** (e.g., "High turnover of linens", "Hygiene compliance", "Luxury upgrade").
- **Product Focus:** Specific mapping (e.g., "Waterproof Protectors for Care Homes").
- **Last Contact Date:** Timestamp of the last AI dispatch.

### Bot Workflow Integration
- **Sarah (Scraper):** Add "Search Intelligence" flags (e.g., `Source: Google Maps`, `Certainty: High`).
- **James (Copywriter):** Display "Pitch Angle" (e.g., "Compliance Focus" vs "Luxury Focus").
- **Adeel (Analyst):** Add a "Quality Score" visualizer (progress bar).

---

## 3. Technical Implementation Strategy

### Frontend (`templates/index.html`)
- Replace embedded CSS with a modern utility-first approach (Tailwind-inspired custom CSS).
- Implement a `Tabbed Interface` to separate "Lead Generation," "Outreach," and "System Logs."
- Use SVG icons (Lucide-style) for all action buttons.

### Backend (`app.py` & `dashboard_api.py`)
- Expand the `load_pipeline_leads` logic to include new status and tier fields.
- Update the `/api/pitch` endpoint to return "Why this fit" and "Value Props" as structured data for a better UI display.
- Implement a status update endpoint `/api/leads/update-status` to move leads through the funnel manually.

## 4. Execution Workflow
1. **Visual Overhaul:** Apply the "Nebula Command" styles.
2. **Funnel Implementation:** Update the table to reflect the 6-stage sales pipeline.
3. **Lead Enrichment:** Modify the CSV handling to support Tiers and Pain Points.
4. **Bot Sync:** Ensure Sarah's output maps directly to these new "realistic" fields.
