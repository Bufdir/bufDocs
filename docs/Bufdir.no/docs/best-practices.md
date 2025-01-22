# Best Practices

## Backend

## Frontend
When we want to use classes from Buflib to get specific styles, for
example [HTML Components](https://buflib.bufdir.no/?path=/docs/html-components-general-information--docs)
or [CSS Util classes](https://buflib.bufdir.no/?path=/docs/css-util-classes-general-information--docs), it is
best to use the class directly in the html like this:

```html
<div class="bl-p-r-2"></div>
```

The alternative would be to use the @extend directive from Sass, like so:

```scss
.my-class {
  @extend .bl-p-r-2;
}
```
Using @extend should be avoided when possible, because the results can be
unpredictable. In the bundle, @extend moves the class to the one it extends,
which can lead to confusion and in the worst case errors in how classes are
weighted. These things can look like errors in buflib, but are not.

### Auth

If we need to expose something to a specific group of internal people, that
should not be accessible to the public, we use episervers AD groups, and expose
the content to logged in users in episerver UI. Feedback results are an example
of how this can be done.

This makes sure that exposing the content to the public unintentionally is
harder, and also makes it easier to know who has access to the content, and
retract the access at a later time if necessary.
