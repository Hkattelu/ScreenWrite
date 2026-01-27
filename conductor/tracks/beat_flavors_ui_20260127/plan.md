# Implementation Plan: Beat Flavors UI Refinement

This plan refactors the `BeatList` component to support specialized UI treatments for different beat flavors (Annotation, Citation, Image) instead of a one-size-fits-all video player.

## Phase 1: Component Refactoring & Type Safety [checkpoint: 202a259]
Goal: Extract the asset preview logic into a standalone component and ensure full type coverage.

- [x] Task: Create `BeatAsset` component skeleton [skip]
    - Extract the preview logic from `BeatList.tsx` into `webapp/frontend/src/components/BeatAsset.tsx`.
    - Support `visual_type` and `visual_content` props.
- [x] Task: Update `BeatList.tsx` to use `BeatAsset` [skip]
    - Replace inline asset rendering with the new component.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Component Refactoring & Type Safety' (Protocol in workflow.md) [skip]

## Phase 2: Implement Minimalist Badges (Annotation & Citation) [checkpoint: ab1b955]
Goal: Replace video placeholders with stylized labels and icons for text-based beats.

- [x] Task: Implement `Annotation` flavor UI [skip]
    - Render a purple-themed badge with "ANNOTATION" text and `Type` icon.
    - Ensure no video player or loading spinners are rendered for this type.
- [x] Task: Implement `Citation` flavor UI [skip]
    - Render an amber-themed badge with "CITATION" text and `Quote` icon.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Implement Minimalist Badges (Annotation & Citation)' (Protocol in workflow.md) [skip]

## Phase 3: Implement Image Flavor & Upload [checkpoint: 98357ae]
Goal: Provide a visible upload trigger for image beats.

- [x] Task: Implement `Image` flavor UI [skip]
    - Render an indigo-themed placeholder with an "Upload Image" button.
- [x] Task: Implement File Upload Trigger [skip]
    - Use a hidden `<input type="file" />` triggered by the visible button.
    - Wire up the change event to a (mocked or simple) handler.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Implement Image Flavor & Upload' (Protocol in workflow.md) [skip]

## Phase 4: Final Polish & Accessibility
Goal: Ensure the audit feedback regarding legibility and a11y is fully satisfied.

- [ ] Task: Verify font sizes and contrast
    - Ensure all new labels use `text-xs` and pass contrast checks.
- [ ] Task: Add Aria Labels
    - Ensure all interactive badges and upload buttons have descriptive `aria-label` attributes.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Polish & Accessibility' (Protocol in workflow.md)
