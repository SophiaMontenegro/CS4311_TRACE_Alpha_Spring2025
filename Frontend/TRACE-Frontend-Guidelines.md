
# TRACE Frontend Implementation Guidelines

A checklist for all teams contributing to the unified frontend. Follow these rules to ensure accessibility, performance, and consistency across all tools.

---

## 1. Component Usage
- [ ] Use existing shared components from `lib/components/ui/`.
- [ ] Do not recreate existing components.
- [ ] Add new props *properly* if needed.

---

## 2. Accessibility (a11y)
- [ ] Use semantic HTML (`<button>`, `<label>`, `<section>`, etc.).
- [ ] Interactive elements must have `aria-label` or `aria-describedby`.
- [ ] All modals/tooltips must be keyboard navigable and closeable via `Esc`.

---

## 3. Responsive Design
- [ ] Pages must work on:
  - MacBook screen (~1280–1440px width)
  - Desktop monitor (~1920px width)

---

## 4. Color Usage
- [ ] Follow colorblind-friendly practices — use high contrast.
- [ ] Use system tokens for colors, no hardcoded hex.
- [ ] Severity indicators must include:
  - Text labels (“High”, “Medium”, “Low”)

---

## 5. Testing & Behavior
- [ ] Validate all forms and show helpful error messages.
- [ ] Gracefully handle failures (use toasts or alerts).
- [ ] Include tooltips and hover behavior as per SRS.

---