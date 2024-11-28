# Frontend Testing

## How we test our frontend code

We use Vitest and React Testing Library to write unit tests for Typescript
functions and component tests for React components.

We prioritize writing components tests over unit tests in the frontend.

We use msw to mock api in tests (see test example with msw in use under 'Useful
Links' below).

We do not find snapshot tests useful.

## Notes

### Google ReCaptcha

Mock google recaptcha api like this:

```javascript
window.grecaptcha = {
  ready: (callback) => callback(),
  execute: vi.fn(() => Promise.resolve({ data: {} })),
};
```

### Testing async RSC

React testing library does not have support for async RSC, but we can still
manage to do it by awaiting and rendering the component as a function instead of
rendering as jsx, like so:

```typescript
const Result = await Xhtmlstring(props);
render(Result);
```

and then testing what is rendered by using the ´screen´ class supplied by RTL,
like so:

```typescript
const text = screen.getByText('This is a test');
expect(text).toBeInTheDocument();
```

### Mobile & Remote Testing

By using Ngrok, you can test on mobile and share the development server with
team members remotely, making it easy to share & co-work.

**Configuration Ngrok**

Download and install Ngrok from this link [Ngrok](https://ngrok.com/)

Ensure `USE_NGROK=true` is set in `.env.local` as your local env file.

Run `ngrok http https://localhost:3000` in the terminal.

Then, use & share the link that auto generated from Ngrok app. (ex.
https://0f03-80-232-32-53.ngrok-free.app)

## Useful Links

- React Testing Library
  [test example](https://testing-library.com/docs/react-testing-library/example-intro).
- [Vite docs](https://vitest.dev/guide/)
- About unit tests, component test and snapshot tests
  [here](https://www.smashingmagazine.com/2020/06/practical-guide-testing-react-applications-jest/).
