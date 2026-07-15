---
name: Cognitive Engineering Mobile
colors:
  surface: '#15121b'
  surface-dim: '#15121b'
  surface-bright: '#3b3742'
  surface-container-lowest: '#0f0d15'
  surface-container-low: '#1d1a23'
  surface-container: '#211e27'
  surface-container-high: '#2c2832'
  surface-container-highest: '#37333d'
  on-surface: '#e7e0ed'
  on-surface-variant: '#cbc3d7'
  inverse-surface: '#e7e0ed'
  inverse-on-surface: '#322f39'
  outline: '#958ea0'
  outline-variant: '#494454'
  surface-tint: '#d0bcff'
  primary: '#d0bcff'
  on-primary: '#3c0091'
  primary-container: '#a078ff'
  on-primary-container: '#340080'
  inverse-primary: '#6d3bd7'
  secondary: '#4cd7f6'
  on-secondary: '#003640'
  secondary-container: '#03b5d3'
  on-secondary-container: '#00424e'
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
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#ffdcbb'
  tertiary-fixed-dim: '#ffb869'
  on-tertiary-fixed: '#2c1700'
  on-tertiary-fixed-variant: '#673d00'
  background: '#15121b'
  on-background: '#e7e0ed'
  surface-variant: '#37333d'
typography:
  headline-lg:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  body-md:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-sm:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  metric-lg:
    fontFamily: JetBrains Mono
    fontSize: 18px
    fontWeight: '700'
    lineHeight: 24px
    letterSpacing: -0.04em
  metric-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '700'
    lineHeight: 12px
    letterSpacing: 0.06em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  touch-target-min: 44px
  container-margin: 16px
  gutter-inline: 12px
  stack-gap: 8px
  section-padding: 24px
---

## Brand & Style
The design system for mobile is a high-performance extension of the "Cognitive Engineering" DNA. It adopts a **Technical Minimalism** style blended with **Developer-Centric** utility. The brand personality is precise, authoritative, and low-latency, designed for users who require rapid data synthesis on the move.

The aesthetic prioritizes function over form, utilizing sharp geometry and high-density information arrays to evoke the feeling of a portable diagnostic terminal. It targets engineers and technical operators who value signal over noise.

## Colors
The palette is rooted in a deep `#131313` obsidian surface to minimize power consumption and visual fatigue. The **DNA Purple** (#8b5cf6) serves as the primary action signal and branding anchor.

Secondary accents use **Cyan** (#06b6d4) for secondary data streams. Signal colors (Emerald, Amber, Rose) are tuned for high-contrast accessibility against the dark background, ensuring critical status changes are immediately perceptible even at low screen brightness.

## Typography
The typography system uses a dual-font approach. **Geist** provides a clean, neutral sans-serif foundation for UI labels and navigation, ensuring legibility at small scale. 

**JetBrains Mono** is utilized exclusively for technical metrics, data values, and status labels to maintain the "Engineering" DNA. Mobile-specific sizing is condensed to support high-density layouts without sacrificing touch-readability. All interactive labels must maintain a minimum perceived size equivalent to 14px for accessibility.

## Layout & Spacing
This design system employs a **Fluid-Technical Grid**. On mobile, the layout uses a 4-column system with a 16px outer margin. 

Despite the high-density aesthetic, all interactive elements must respect a **44px minimum touch target** height or width. Spacing is governed by an 8pt linear scale, with 4pt increments used for tight data-grid clusters. Content should be stacked vertically in modular "blocks" that allow for rapid vertical scanning.

## Elevation & Depth
Depth is expressed through **Tonal Layering** and **Ghost Outlines** rather than traditional shadows. 

1. **Surface (Level 0):** #131313 (Base)
2. **Container (Level 1):** #1c1c1c (Modular cards and sections)
3. **Overlay (Level 2):** #262626 (Modals and tooltips)

Separation is reinforced with 1px solid borders using high-contrast "wireframe" strokes (Primary or Neutral-700) to maintain the technical, non-skeuomorphic feel. Interactive elements use a subtle inner glow of the primary color when active.

## Shapes
The shape language is **Soft-Geometric**. A base radius of 4px (`roundedness: 1`) is applied to all primary containers and buttons. This provides just enough softness to distinguish the interface from a raw terminal while maintaining a disciplined, structured appearance. Icons should follow a 2px stroke weight with minimal rounding on terminals.

## Components

### Buttons
- **Primary:** Solid Purple (#8b5cf6) with white text. 44px height. Sharp 4px corners.
- **Ghost:** 1px Purple border, transparent fill. Used for secondary technical actions.

### Data Chips
- Small, monospace-driven badges. Backgrounds use 15% opacity of signal colors (Emerald, Rose, etc.) with a 100% opacity text label for status indicators.

### Technical Lists
- High-density rows with 12px vertical padding. Left-aligned Geist labels with right-aligned Monospace values. Separated by 1px dimmed borders.

### Input Fields
- Darker-than-surface fill (#0a0a0a) with a 1px border that illuminates Purple on focus. Monospace input text for precision.

### Status Cards
- Used for primary metrics. Features a 2px top-border accent in a signal color to denote system health at a glance.

### Terminal Feed
- A mobile-optimized log component using `metric-sm` typography, allowing for 8-10 lines of scrollable diagnostic data within a single card.