---
applyTo: "src/components/**/*.js"
---

# Frontend Component Instructions

These instructions apply to all reusable UI components under `src/components/**/*.js`.

## Component Structure

- Each component must be a **functional component** using React hooks.
- Export the component as the **default export** of its file.
- One component per file. The file name must match the component name (PascalCase), e.g. `SkillCard.js` → `export default function SkillCard`.
- Colocate a component's helper sub-components in the same file only when they are not reused elsewhere; otherwise extract them into their own files.

## Props

- Define and validate props using **PropTypes** or document them with JSDoc `@param` comments.
- Destructure props in the function signature rather than accessing them via `props.<name>`.
- Provide sensible `defaultProps` (or default parameter values) for optional props.
- Avoid passing too many props ("prop drilling") — lift shared state to context or a custom hook when more than two levels of nesting are needed.

## State & Side Effects

- Use `useState` only for UI-local state (e.g. toggle visibility, controlled input).
- Use **TanStack Query** (`useQuery`, `useMutation`) for any state that comes from or goes to the server; do not manage server data with `useState`/`useEffect`.
- Keep `useEffect` usage minimal. Every `useEffect` must have an explicit dependency array and a cleanup function where applicable.
- Extract complex or reusable stateful logic into custom hooks in `src/hooks/`.

## Styling

- Use **Tailwind CSS** utility classes exclusively. Do not write inline `style` props or separate `.css` / `.module.css` files for components.
- Use the `clsx` helper for conditional or composed class names.
- Follow a consistent class ordering: layout → spacing → sizing → typography → color → interaction (e.g. `flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg`).
- Build for mobile-first; apply responsive prefixes (`sm:`, `md:`, `lg:`) as needed.

## Forms

- Use **react-hook-form** (`useForm`, `Controller`) for all form components.
- Validate with **Yup** schemas passed to `@hookform/resolvers/yup`.
- Display field-level error messages inline, adjacent to the relevant input.
- Disable the submit button while the form is submitting (`formState.isSubmitting`).

## Feedback & Loading States

- Show a loading indicator (spinner or skeleton) while async data is being fetched.
- Show meaningful error messages when a request fails — use **react-toastify** for transient notifications.
- Never leave the user with a blank screen or silent failure.

## Accessibility

- Use semantic HTML elements (`<button>`, `<nav>`, `<main>`, `<section>`, etc.) instead of generic `<div>` + `onClick` where possible.
- Every interactive element must be keyboard-focusable and have a visible focus ring.
- Images must have descriptive `alt` text; decorative images use `alt=""`.
- Provide `aria-label` or `aria-labelledby` for icon-only buttons and unlabelled form controls.

## Performance

- Memoize expensive computations with `useMemo` and stable callbacks with `useCallback` only when a measurable performance issue exists — do not over-memoize.
- Lazy-load heavy child components with `React.lazy` + `Suspense` when they are not needed on the initial render.
- Avoid creating new objects/arrays in JSX props that will cause unnecessary re-renders.

## Code Style

- Keep JSX readable: if an element has more than three props, put each prop on its own line.
- Avoid ternary chains in JSX longer than two levels; extract them into variables or helper functions.
- Do not leave `console.log` statements in committed code.
- Use optional chaining (`?.`) and nullish coalescing (`??`) instead of verbose null checks.
