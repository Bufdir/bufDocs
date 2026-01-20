# Frontend Testing

## How we test our frontend code

We use Vitest and React Testing Library to write unit tests for Typescript
functions and component tests for React components.

We prioritize writing components tests over unit tests in the frontend.

We use msw to mock api in tests (see test example with msw in use under 'Useful
Links' below).

We do not find snapshot tests useful.

## Notes

### Fetch error

Tests run in Node. Node does not support fetch natively atm, so polyfill it by
importing whatwg-fetch:

```javascript
import 'whatwg-fetch';
```

### Google ReCaptcha

Mock google recaptcha api like this:

```javascript
window.grecaptcha = {
  ready: (callback) => callback(),
  execute: vi.fn(() => Promise.resolve({ data: {} })),
};
```

## Useful Links

- React Testing Library
  [test example](https://testing-library.com/docs/react-testing-library/example-intro).
- [Vite docs](https://vitest.dev/guide/)
- About unit tests, component test and snapshot tests
  [here](https://www.smashingmagazine.com/2020/06/practical-guide-testing-react-applications-jest/).
