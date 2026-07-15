---
name: Cognitive Engineering
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#cbc3d7'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#958ea0'
  outline-variant: '#494454'
  surface-tint: '#d0bcff'
  primary: '#d0bcff'
  on-primary: '#3c0091'
  primary-container: '#a078ff'
  on-primary-container: '#340080'
  inverse-primary: '#6d3bd7'
  secondary: '#c8c6c5'
  on-secondary: '#303030'
  secondary-container: '#474746'
  on-secondary-container: '#b7b5b4'
  tertiary: '#ffb869'
  on-tertiary: '#482900'
  tertiary-container: '#ca801e'
  on-tertiary-container: '#3f2300'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e9ddff'
  primary-fixed-dim: '#d0bcff'
  on-primary-fixed: '#23005c'
  on-primary-fixed-variant: '#5516be'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1b1b1c'
  on-secondary-fixed-variant: '#474746'
  tertiary-fixed: '#ffdcbb'
  tertiary-fixed-dim: '#ffb869'
  on-tertiary-fixed: '#2c1700'
  on-tertiary-fixed-variant: '#673d00'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
  signal-emerald: '#10B981'
  signal-amber: '#F59E0B'
  signal-rose: '#F43F5E'
  signal-cyan: '#06B6D4'
  border-subtle: '#262626'
  text-muted: '#A3A3A3'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  code-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '400'
    lineHeight: 14px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 12px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  sidebar-width: 260px
  inspector-width: 320px
  gutter: 12px
  row-height-dense: 28px
  row-height-standard: 36px
---

## Brand & Style

The design system is engineered for technical depth and cognitive efficiency, catering to software architects and senior engineers. It functions as a high-performance control plane, prioritizing information density over decorative white space.

The aesthetic follows a **Modern Corporate/IDE** movement—specifically a "dark-mode first" philosophy reminiscent of high-end developer tools. The visual language is defined by surgical precision, utilitarian layouts, and a "low-latency" feel. Every element must serve a functional purpose, facilitating deep focus and rapid data parsing without visual fatigue.

**Key Principles:**
- **Density as a Feature:** Maximize visible data points using compact vertical rhythms.
- **Cognitive Layering:** Use color strictly for semantic signaling and focus.
- **Technical Honesty:** No unnecessary embellishments; borders and tonal shifts define structure.

## Colors

The palette is anchored in a deep charcoal base to minimize ocular strain during long-form technical analysis.

- **Surface Architecture:** The primary background uses `#0D0D0D`. Secondary surfaces for sidebars and panels use a slightly lighter gray to create depth without relying on shadows.
- **Semantic Signaling:** Chromatic colors are reserved for status. **Emerald** represents healthy nodes, **Amber** denotes warnings, and **Rose** indicates critical architectural risks (e.g., high Bus Factor). **Cyan** is utilized for neutral metadata and information tooltips.
- **Brand Accent:** **DNA Purple** (`#8B5CF6`) is used sparingly for primary actions, active states, and brand-specific highlights.
- **Interactive States:** Use subtle luminosity increases on hover rather than dramatic color shifts.

## Typography

This design system utilizes a dual-font strategy to separate intent:

1.  **Inter (UI):** Used for all navigational elements, labels, and descriptive text. It is chosen for its exceptional legibility at small sizes.
2.  **JetBrains Mono (Data):** Used for file paths, symbol names, commit hashes, and code snippets. This ensures that technical data is instantly recognizable and monospaced for alignment in high-density tables.

**Type Implementation:**
- Use **label-caps** for section headers in the Inspector Panel.
- Use **code-sm** for inline metadata and terminal-style outputs.
- Maintain a strict 12px or 14px base for body text to ensure high information density.

## Layout & Spacing

The layout follows a **Fixed-Fluid-Fixed** three-pane architecture. 

- **Sidebar (Left):** Fixed width, containing navigation and the file/module tree.
- **Main Stage (Center):** Fluid canvas for WebGL graphs or primary data visualizations.
- **Inspector (Right):** Fixed width for contextual metadata and deep-dive analytics.

**Grid & Rhythm:**
- A **4px base unit** governs all spacing.
- **High-Density Mode:** Tables and lists should use the `row-height-dense` (28px) unit to maximize vertical data visibility.
- **Breakpoints:** On displays narrower than 1280px, the Inspector panel should collapse into a drawer or overlay to preserve the Main Stage.

## Elevation & Depth

Depth is primarily achieved through **Tonal Layering** and **Low-Contrast Outlines** rather than traditional shadows. This maintains a flat, "pro-tool" aesthetic.

- **Level 0 (Canvas):** The deepest layer (`#0D0D0D`).
- **Level 1 (Panels):** Sidebars and Inspector use `#161616` with a 1px border of `border-subtle` (`#262626`).
- **Level 2 (Modals/Command Palette):** Centrally floating elements use a slightly lighter surface (`#1F1F1F`) with a subtle 8px ambient shadow to separate them from the work surface.
- **Backdrop Blurs:** Use a 12px blur on overlays (like the Command Palette) to maintain context while focusing user attention.

## Shapes

The shape language is **Soft (0.25rem)**, providing a subtle hint of modern refinement without appearing "consumer-grade" or overly playful.

- **UI Controls:** Buttons, inputs, and chips use a 4px radius.
- **Nodes/Status Badges:** Use circular/pill shapes only for semantic status indicators (e.g., health dots) to make them stand out against the rectangular grid of the UI.
- **Graph Nodes:** Use 4px rounded rectangles for module nodes to maximize label space within the node.

## Components

- **Buttons:** Primary buttons use `DNA Purple` with white text. Secondary buttons are ghost-style with `border-subtle` and white text. No gradients.
- **Input Fields:** Darker than the panel surface (`#050505`). Borders turn `DNA Purple` only on focus. Use JetBrains Mono for text in search or filter inputs.
- **Chips/Badges:** Small, condensed labels with a background tint corresponding to their semantic signal (e.g., a faint red background for "Critical").
- **Tree/Lists:** Hover states should use a subtle gray highlight (`#1F1F1F`) extending to the full width of the panel. Use "guide lines" (1px vertical lines) for nested tree structures.
- **Command Palette:** A centered modal triggered by `Cmd+K`. It features high-density results with keyboard shortcut hints aligned to the right in `code-sm` typography.
- **Skeletons:** High-fidelity skeletons should match the exact geometry of the components, using a subtle pulse animation between `#161616` and `#1F1F1F`.