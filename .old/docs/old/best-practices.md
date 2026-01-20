# Best Practices

## Backend

### Auth

If we need to expose something to a specific group of internal people, that
should not be accessible to the public, we use episervers AD groups, and expose
the content to logged in users in episerver UI. Feedback results are an example
of how this can be done.

This makes sure that exposing the content to the public unintentionally is
harder, and also makes it easier to know who has access to the content, and
retract the access at a later time if necessary.
