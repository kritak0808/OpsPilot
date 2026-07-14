# OpsPilot AI: Phase 3 Enterprise Product Design System & UX Architecture

This document defines the user experience framework, interactive patterns, navigation hierarchies, and design system guidelines for **OpsPilot AI**—an Autonomous AI DevOps & Cloud Operations Platform.

---

## 1. Global Visual Language & Design System

### 1.1 Typography
* **Primary Font Stack**: `Inter`, system-ui, -apple-system, sans-serif (used for UI elements, controls, tables, and paragraphs).
* **Mono Font Stack**: `JetBrains Mono`, SFMono-Regular, Consolas, monospace (used for logs, YAML configurations, terminal output, and resource identifiers).
* **Type Scale**:
  * **H1**: 30px (Line Height: 36px, Weight: 600 Semibold) - Page Header
  * **H2**: 24px (Line Height: 30px, Weight: 600 Semibold) - Section Header
  * **H3**: 20px (Line Height: 26px, Weight: 500 Medium) - Card Header
  * **Body Large**: 16px (Line Height: 24px, Weight: 400 Regular) - Chat output, long text
  * **Body Standard**: 14px (Line Height: 20px, Weight: 400 Regular) - Main data tables, sidebar items
  * **Caption / Small**: 12px (Line Height: 16px, Weight: 500 Medium) - Labels, tags, timestamps

### 1.2 Spacing & Grid System
* **Spatial Scale**: Based on a 4px increment system:
  * `4px` (xxs) - Micro-spacing (labels, badge margins)
  * `8px` (xs) - Element gap (buttons, tags inside a row)
  * `12px` (sm) - Control spacing (inputs, items inside lists)
  * `16px` (md) - Page layout subelements (card padding, sidebar margins)
  * `24px` (lg) - Core sections (grid gaps, page header spacing)
  * `32px` (xl) - Outer borders (desktop page container padding)
* **Responsive Layout Grids**:
  * **Desktop (1440px+)**: 12-column grid, 24px columns gap, 32px page margins.
  * **Laptop (1024px-1440px)**: 12-column grid, 16px columns gap, 24px page margins.
  * **Tablet (768px-1024px)**: 8-column grid, 16px columns gap, 16px page margins.
  * **Mobile (<768px)**: 4-column grid, 12px columns gap, 12px page margins.

### 1.3 Border Radius & Elevation
* **Border Radius Scale**:
  * `none` - Code editors, terminal output shells
  * `2px` - Checkboxes, micro-tags
  * `4px` - Buttons, input fields, control groups
  * `6px` - Core cards, system badges
  * `8px` - Nested popovers, navigation tabs
  * `12px` - Modals, central command palette containers
* **Elevation & Shadows**:
  * **Flat Layer (z-0)**: Active canvas, application backgrounds.
  * **Base Border (z-1)**: Page cards.
  * **Floating UI (z-10)**: Dropdowns, menu items.
  * **Overlay Modal (z-50)**: Command palettes, pop-up configurations.

### 1.4 Color Palette & Modes

#### Dark Mode (Primary Mode for NOC/Platform Operations)
* **Canvas Background**: Slate `rgb(9, 11, 15)` (Deep rich dark slate)
* **Surface Background**: Slate `rgb(17, 21, 28)` (Card and popover background)
* **Border Color**: Slate `rgb(29, 35, 47)` (Thin separator line)
* **Primary Brand Text**: Slate `rgb(241, 245, 249)` (Bright slate)
* **Secondary Text**: Slate `rgb(148, 163, 184)` (Muted gray-slate)
* **Primary Brand Accent**: Violet `rgb(124, 58, 237)` (Indigo-violet brand tone)

#### Light Mode
* **Canvas Background**: Gray `rgb(248, 250, 252)` (Light slate gray)
* **Surface Background**: Slate `rgb(255, 255, 255)` (Pure white)
* **Border Color**: Slate `rgb(226, 232, 240)` (Light gray separator)
* **Primary Brand Text**: Slate `rgb(15, 23, 42)` (Deep dark slate text)
* **Secondary Text**: Slate `rgb(100, 116, 139)` (Medium slate)
* **Primary Brand Accent**: Violet `rgb(109, 40, 217)` (Deep violet)

#### Semantic / Status Colors (Unified across modes)
* **Success**: Emerald `rgb(16, 185, 129)` (Green tag)
* **Warning**: Amber `rgb(245, 158, 11)` (Yellow caution tag)
* **Error**: Rose `rgb(244, 63, 94)` (Red danger tag)
* **Info**: Blue `rgb(59, 130, 246)` (Blue information badge)

### 1.5 System States
* **Loading States**: Shimmer skeleton loader layouts representing actual components (e.g., text lines, chart blocks) rather than generic circular spinners.
* **Empty States**: Centered illustration layouts with descriptive headlines, direct instructions, and a single call-to-action button (e.g., "Connect Repository").
* **Error States**: Display error codes with direct instructions for resolution and a retry button.
* **Success States**: Subtle toast notifications with a progress bar.

---

## 2. Application Shell & Navigation Layout

The application shell provides the framing layout for the dashboard workspace.

```text
+----------------------------------------------------------------------------------+
| Org Sw. | Workspace Sw. |  [🔍 Global Search...]  | Alerts | Profile | Help  |
+----------------------------------------------------------------------------------+
|  Dashboard         |  Workspace Canvas                                           |
|  Projects          |                                                             |
|  Applications      |  [Breadcrumbs: Org > Project > Application > Deployments]   |
|  Deployments       |                                                             |
|  Pipelines         |  +-------------------------------------------------------+  |
|  Kubernetes        |  | Metric Chart                                          |  |
|  Monitoring        |  |                                                       |  |
|  AI Assistant      |  +-------------------------------------------------------+  |
|  Settings          |                                                             |
+----------------------------------------------------------------------------------+
```

### 2.1 Shell Components
* **Top Navigation Bar**:
  * Left: **Organization Switcher** (dropdown list of organizations) + **Workspace Switcher** (dropdown list of projects).
  * Center: **Global Search Bar** (launches the **Command Palette** on click).
  * Right: Quick-access buttons (incident count, help menu, user profile options).
* **Sidebar Navigation**: Left-aligned, collapsible panel. Houses system links organized by functional domains.
* **Command Palette**: Accessed via `Cmd+/` or `Ctrl+/`. Integrates search, navigation links, and administrative actions in a search overlay.
* **Notification Center**: Displays system alerts, build outcomes, and agent diagnostic updates.

### 2.2 Navigation Hierarchy (Sidebar Structure)
1. **Home**:
   - `Executive Overview` -> High-level operational overview.
   - `Operations Dashboard` -> Platform health status.
2. **Delivery & Source Control**:
   - `Projects` -> Project listing.
   - `Applications` -> Managed microservices.
   - `Deployments` -> Active release pipelines.
   - `Pipelines` -> Automation run histories.
   - `Repositories` -> Source code integrations.
3. **Infrastructure & Containers**:
   - `Kubernetes` -> Cluster management panels.
   - `Infrastructure` -> Terraform state views.
4. **Telemetry & Troubleshooting**:
   - `Monitoring` -> Prometheus dashboard widgets.
   - `Logs` -> Loki query terminal.
   - `Metrics` -> Resource saturation charts.
   - `Tracing` -> OpenTelemetry trace visualizations.
   - `Incidents` -> Active outages and alerts.
   - `Alerts` -> Notification rules.
5. **AI Assistant Area**:
   - `AI Chat` -> Conversation interface with DevOps agents.
   - `AI Agents` -> Specialized agent configuration panels.
6. **Administration**:
   - `Secrets` -> Encryption key configurations.
   - `Notifications` -> Integration profiles (Slack/PagerDuty).
   - `Audit Logs` -> Access and compliance records.
   - `Settings` -> Organization-wide settings.

---

## 3. Page Architecture Design

### 3.1 Kubernetes Cluster Dashboard

```text
+----------------------------------------------------------------------------------+
| Cluster: prod-us-east-1  [Namespace: payment v]           [Add Pod] [Sync State] |
+----------------------------------------------------------------------------------+
| [ Pods: 14/15 ] [ Restarts: 4 ] [ CPU: 72% ] [ Memory: 64% ]                     |
+----------------------------------------------------------------------------------+
| Filters: [Search Pods...] [Status: All v]                                        |
| +------------------------------------------------------------------------------+ |
| | Pod Name          | Namespace | Status   | Restarts | CPU (Cores) | Memory   | |
| +-------------------+-----------+----------+----------+-------------+----------+ |
| | payment-v1-abc    | payment   | Running  | 0        | 0.12        | 256MB    | |
| | payment-db-0      | payment   | Degraded | 12       | 0.85        | 1.2GB    | |
| +-------------------+-----------+----------+----------+-------------+----------+ |
+----------------------------------------------------------------------------------+
```

* **Purpose**: Inspect Kubernetes cluster states, view node resources, and diagnose container issues.
* **Primary KPIs**: Cluster CPU allocation %, Cluster Memory allocation %, active nodes, and restart rates.
* **Widgets**: Node layout grid and resource allocation meters.
* **Tables**: Pod list table (fields: Pod Name, Namespace, Status, Restarts, CPU (Cores), Memory, IP).
* **Charts**: Resource allocation trends over time (CPU/Memory utilization).
* **Filters**: Namespace selectors, node dropdown filters, and status filters.
* **Actions**: Restart Pod, View Logs, Edit YAML, Open Diagnostic Terminal.
* **AI Features**: "Diagnose Pod" action next to crashing pods. This launches a slide-out drawer containing a log analysis, event summary, and a recommended fix.
* **States**:
  * *Empty*: "No clusters connected." (Call-to-action button: "Import Cluster").
  * *Loading*: Grid skeleton placeholders showing resource blocks.
  * *Error*: Notification banner: "Unable to query Kubernetes API." (Includes retry option).

### 3.2 Incident Management Page
* **Purpose**: Triage system outages, coordinate incident response, and document post-mortems.
* **Primary KPIs**: Mean Time to Resolve (MTTR), active P0 incidents, and incident durations.
* **Widgets**: Priority distribution chart and on-call engineer shifts.
* **Tables**: Incident log table (fields: ID, Status, Severity, Summary, Impacted Service, Time Triggered, Assignee).
* **Charts**: Frequency of incidents grouped by service name.
* **Filters**: Severity selectors, service selectors, and assignee dropdowns.
* **Actions**: Acknowledge, Resolve, Escalate, Assign, Create War Room.
* **AI Features**: Inline Root Cause Analysis (RCA) card showing correlation summaries, git changes, and a drafted incident post-mortem.
* **States**:
  * *Empty*: "All systems operational. No active incidents."
  * *Loading*: Row skeletons showing incident cards.
  * *Error*: Error alert: "Failed to sync alerts with Alertmanager."

---

## 4. Multi-Domain Dashboard Frameworks

### 4.1 Executive Overview Dashboard

```text
+----------------------------------------------------------------------------------+
| EXECUTIVE OVERVIEW                                        [Last 30 Days v] [Exp] |
+----------------------------------------------------------------------------------+
| [ Service SLA: 99.98% ] [ Cost: $12.4K (-4%) ] [ MTTR: 14m ] [ Deploys: 1,240 ]   |
+----------------------------------------------------------------------------------+
| +-----------------------------------------+ +----------------------------------+ |
| | Monthly Spend Trend                    | | SLA Violations by Service        | |
| | [Bar Chart: Infrastructure Costs]       | | [Donut Chart: Outage Minutes]    | |
| +-----------------------------------------+ +----------------------------------+ |
+----------------------------------------------------------------------------------+
```

* **Layout Structure**: 4-column layout block for top metrics, 2-column layout block for main analysis charts.
* **Metric Cards**: Service Level Agreement (SLA) status, Monthly Cloud Cost, MTTR, and Deployment success rates.
* **Main Charts**: Trend chart showing monthly cloud costs and a pie chart of outages by service.
* **AI Insight Panel**: Top widget summarizing cost changes and optimization suggestions: *"AI recommendation: Scale down 4 unused EKS nodes in staging to save $320/mo."*

### 4.2 Kubernetes Dashboard
* **Layout Structure**: 2-column resource panel, followed by a wide grid listing active pods and nodes.
* **Metric Cards**: Healthy pods ratio, system restart rates, and pending resource allocations.
* **Main Charts**: Resource usage timelines showing allocated vs. actual usage.
* **AI Insight Panel**: Action recommendations highlighting pods close to Out-of-Memory (OOM) limits: *"Resource Alert: `payment-service` pod is using 94% of memory limits. AI recommendation: Increase memory limits by 256MB."*

---

## 5. Integrated AI Experience Patterns

OpsPilot AI embeds diagnostics directly into standard developer workflows.

```text
+----------------------------------------------------------------------------------+
| payment-db-0 (State: Degraded)                                                   |
+----------------------------------------------------------------------------------+
| Log Output:                                                                      |
| [2026-07-10 20:59:00] FATAL: connection limit exceeded for non-superusers        |
|                                                                                  |
| +------------------------------------------------------------------------------+ |
| | 💡 OpsPilot AI Analysis: Connection Pool Exhausted                           | |
| |                                                                              | |
| | Analysis: Database is rejecting connections due to limit exhaustion.         | |
| | Proposed Fix: Increase max_connections or scale the application connection   | |
| | pool settings in environment config.                                         | |
| |                                                                              | |
| | [Apply Recommendation] [Open AI Chat for details]                            | |
| +------------------------------------------------------------------------------+ |
+----------------------------------------------------------------------------------+
```

### 5.1 AI Chat Drawer
* **Design Pattern**: Slide-out panel accessible from any page.
* **Behavior**: Retains the page context automatically (e.g., if open on a pipeline failure page, the chat session initializes with the build logs).
* **Interactions**: Suggests quick commands like "Analyze error logs" or "Generate config patch."

### 5.2 Contextual Root Cause (RCA) Banners
* **Design Pattern**: Warning banners next to active incidents.
* **Behavior**: Clicking the banner opens a modal detailing the root cause, matching system events, and a suggested code diff.
* **Interactions**: "Apply Remediation" button to trigger automated hotfixes.

---

## 6. Interactive User Flows & Responsive Design

### 6.1 Incident Investigation Flow
1. **Notification Intake**: Developer receives an alert notification via Slack, containing a link to the incident page.
2. **Incident Summary**: Developer lands on the incident detail page. A prominent AI Insight box displays: *"Diagnostic: Connection pool limit exceeded for database."*
3. **Log Inspection**: Developer clicks "View Logs," opening a side-by-side terminal with the error stack trace highlighted.
4. **Remediation**: Developer reviews the AI-generated Terraform edit, selects "Apply Fix," and is redirected to approval validation.

### 6.2 Responsive Screen Adaptations

| Screen Width | Target Platform | Interface Changes |
| :--- | :--- | :--- |
| **1440px+** | Desktop Monitor | Full 12-column page layout. Persistent sidebar navigation, multi-column metric layouts, and side-by-side log terminals. |
| **1024px-1440px** | Laptop | Standard 12-column layout. Sidebar navigation collapses to icons on scroll, and tables automatically hide secondary columns. |
| **768px-1024px** | Tablet | 8-column layout. Sidebar collapses to a slide-out menu. Multi-column charts stack vertically. |
| **<768px** | Mobile Device | 4-column layout. Interactive charts are replaced with flat summary widgets, and log terminals present text wrap formats. |
