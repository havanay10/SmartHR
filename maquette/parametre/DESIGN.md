---
name: Executive Slate & Deep Teal
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#3e4946'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#6e7a75'
  outline-variant: '#bdc9c4'
  surface-tint: '#006b5b'
  primary: '#005f50'
  on-primary: '#ffffff'
  primary-container: '#0d7a68'
  on-primary-container: '#aaffe9'
  inverse-primary: '#7cd7c1'
  secondary: '#565d79'
  on-secondary: '#ffffff'
  secondary-container: '#d8deff'
  on-secondary-container: '#5a627e'
  tertiary: '#9e2622'
  on-tertiary: '#ffffff'
  tertiary-container: '#c03f37'
  on-tertiary-container: '#ffeae8'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#99f3dd'
  primary-fixed-dim: '#7cd7c1'
  on-primary-fixed: '#00201a'
  on-primary-fixed-variant: '#005144'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#bec5e5'
  on-secondary-fixed: '#131a33'
  on-secondary-fixed-variant: '#3e4660'
  tertiary-fixed: '#ffdad6'
  tertiary-fixed-dim: '#ffb4ab'
  on-tertiary-fixed: '#410002'
  on-tertiary-fixed-variant: '#8b1817'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-hero:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '600'
    lineHeight: 22px
  kpi-value:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.02em
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 19px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 17px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 15px
    letterSpacing: 0.06em
  label-badge:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
  mono-data:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-lg: 1.5rem
  margin: 1.5rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.25rem
  space-xl: 1.75rem
  space-2xl: 2.5rem
---

## Brand & Style

The design system targets HR leaders, Chief People Officers, and enterprise operations directors who require immediate cognitive clarity when navigating complex human capital analytics, predictive AI turnover modeling, and team composition diagnostics. The design style balances Corporate Modern with precision data dashboard aesthetics: robust architectural structure, clean content framing, and calm confidence.

The tone evokes authority, rigorous compliance, forward-looking AI enablement, and empathetic talent management. The UI avoids gimmicks in favor of crisp separation of concerns: a dark, focused control spine (midnight slate) contrasting with an open, high-readability canvas (#F8FAFC) where cards float with subtle perimeter definition.

## Colors

The system employs a dual-atmosphere paradigm:
- **Sidebar & Core Navigation Chrome**: Deep midnight navy (`#0B132B` to `#0F172A`) providing maximum contrast, anchored command, and clear separation from analytical workflows. Active menu highlights use soft deep-teal glass tints (`rgba(13, 122, 104, 0.25)`) with an emerald/teal accent border.
- **Primary Operational Teal (`#0D7A68`)**: Used for primary calls-to-action ("+ Nouvel employé", "Assigner en Binôme", "Traiter l'anomalie"), verified states, and active module markers.
- **Semantic State Architecture**:
  - *Critical / Danger*: Coral red (`#E0564C`) for urgent turnover alerts, threshold breaches, and mandatory intervention tags.
  - *Preventive / Caution*: Rich warm amber (`#D97706` / `#F59E0B`) for soft signals, repeated anomalies, and pending authorizations.
  - *Success / Nominal*: Deep emerald-teal (`#059669`) for active employees, high match scores, and resolved audit records.
  - *Neutral & Canvas*: Base canvas `#F8FAFC`, card surfaces `#FFFFFF`, borders `#E2E8F0`, muted metadata `#64748B`, and high-contrast text `#0F172A`.

## Typography

Typography relies entirely on **Inter**, tuned for high density and rapid scanability across data-dense tables, metric cards, and behavioral DISC profiles. 

All KPI metrics and summary figures apply negative tracking (`-0.02em`) with heavy weight (`700`) to guarantee distinct numerical legibility from a distance. Metadata tags and category headers utilize `label-caps` with uppercase transformation and loose tracking (`0.06em`) to anchor analytical groupings without competing with data values.

## Layout & Spacing

The viewport implements a fixed two-tier application shell:
1. **Persistent Left Rail**: Fixed 260px desktop width, vertically divided into application identity, core workflow navigation, AI connection health, and current user credential footer.
2. **Top Utility Bar**: Fixed 64px height with integrated date context, quick-alert bell counter, and user profile avatar.
3. **Workspace Canvas**: Fluid container with 24px/32px exterior margins and an internal 12-column grid system (16px gutters) hosting modular metric rows, split split-pane employee drawers, and side-by-side diagnostic cards.

Component internal padding obeys strict metric steps: standard metric summary cards leverage 16px to 20px padding; tight list items and mini table rows use 8px to 12px vertical gaps.

## Elevation & Depth

This system avoids heavy drop shadows, opting for sharp structural definition with low-opacity ambient layers and subtle border strokes:

- **Base Cards (Elevation 1)**: `box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05), 0 1px 2px rgba(15, 23, 42, 0.03)` with a hairline boundary `border: 1px solid #E2E8F0`.
- **Active / Accent Cards**: Top-edge semantic accent stripe (3px solid highlight in teal, coral, or amber) applied directly to card top borders to denote operational urgency.
- **Drawer & Flyout Modals (Elevation 2)**: Used for the collaborative employee side-drawer (`box-shadow: -4px 0 24px rgba(11, 19, 43, 0.08)`), creating clear spatial elevation over list backgrounds.
- **Popovers & Menus (Elevation 3)**: Crisp floating menus with `box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.1), 0 8px 10px -6px rgba(15, 23, 42, 0.06)` framed by a `#CBD5E1` boundary.

## Shapes

The design system standardizes on **Rounded Level 2**:
- Main analytics cards, alert panels, and dashboard containers use `0.75rem` (12px) border-radius.
- Filter chips, secondary buttons, input wrappers, and segmented control tabs utilize `0.5rem` (8px).
- Status badges, category pills, and AI connectivity indicators utilize a full pill format (`9999px`) to immediately distinguish contextual status from actionable square elements.
- Avatars and DISC/co-working crossover chips employ circular geometry (`50%` / round).

## Components

### Buttons
- **Primary**: Solid teal `#0D7A68` background, white bold text, 8px radius, 10px 18px padding. Hover: `#0B6355`. Active: `#084C41`.
- **Secondary / Outline**: 1px `#CBD5E1` border on white canvas, `#0F172A` text. Hover: `#F1F5F9` background.
- **Urgent Action**: Solid coral `#E0564C` or outline coral with coral text for immediate escalation.

### Metric KPI Tiles
- Multi-row data structure: Category label (`label-caps` in `#64748B`), key numerical value (`kpi-value` in `#0F172A`), subtitle / Delta indicator (`body-sm`), accompanied by a soft tinted icon medallion (teal, rose, cyan, or amber tint).
- Highlight state: Optional 3px solid top-accent bar in semantic category color.

### Navigation Items (Sidebar)
- 40px item height, rounded 8px radius, horizontal flex alignment with 12px icon gap.
- Default: `#94A3B8` text, transparent background.
- Hover: `#1E293B` background, `#F8FAFC` text.
- Active: Background `rgba(13, 122, 104, 0.22)`, border-left `3px solid #10B981`, white text (`#FFFFFF`) with medium weight.

### Status Badges & Chips
- **Critical / Urgent**: Background `#FEE2E2`, text `#991B1B`, border `#FECACA`.
- **Preventive / Alert**: Background `#FEF3C7`, text `#92400E`, border `#FDE68A`.
- **Nominal / Active**: Background `#D1FAE5`, text `#065F46`, border `#A7F3D0`.
- **Informational / Category**: Background `#F1F5F9`, text `#475569`, border `#E2E8F0`.

### Employee List & Drawer Panels
- Split-pane layout: Collaborative talent rows feature lettered/photo avatar chips (42px circle), bold primary label, compact role description, and a discrete "Voir dossier" affordance.
- Inspection Drawer: White surface, tab bar for "Contrat Poste" vs "Congés & Absences" with an emerald-teal underline indicator (`2px solid #0D7A68`).