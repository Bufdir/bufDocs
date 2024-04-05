This is a [Next.js](https://nextjs.org/) project bootstrapped with
[`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Getting Started

First, start up the dotnet backend server:

```bash
dotnet run
```

Copy the .env.example to .env.local and ask a teammember for the AZURE_AD_CLIENT_SECRET

Then, run the Next.js development server:

```bash
npm run dev
```

Open [https://localhost:3000](https://localhost:3000) with your browser to see
the result.

## Structure

- `src/app`: We put pages and layout components here.
- `src/app/layout.tsx`: defines the layout of the app with the header, feedback
  component and footer.
- `src/app/[[routeParams]]/page.tsx`: takes all params that is not defined in
  other named pages and passes to different page templates based on content type
  defined in the Content Delivery API.
- `src/page-templates`: defines page templates for different content types.
- `public`: Static assets like images are served from here.

## Converting razor pages to Next.js page templates

Go to the [razor-to-next](../../docs/razor-to-next.md) document to read about
the conversion process.

## Learn More About Next.js

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js
  features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out
[the Next.js GitHub repository](https://github.com/vercel/next.js/) - your
feedback and contributions are welcome!
