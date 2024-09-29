# Releasing and deploy this project

## Make release branch

Start by pulling the latest changes from the develop and main branch and then
run from develop: `git flow release start` followed by the new version number
for the project (for example 1.2.3).

The version should follow [semver](https://semver.org/).

## Update version number

Update version number in ./src/NextJs/package.json to the same as you
chose for the project when creating the release branch (for example 1.2.3).

package.json example:

```json
{
  "name": "projectname",
  "version": "1.2.3",
```

and then run `npm i` and `npm run build` in /src/NextJs.

## Update the changelog

Open ./changelog.md and document the latest release following the pattern of
previous releases.

Remember to change the headline to reflect the actual release number and date,
remove unused headlines (i.e. if there are no lines under the headline "Removed"
for this release).

Copy/paste the template for the changelog from the bottom of the changelog and
put it on top of the changelog to prepare for adding unreleased changes after
this release.

## Deploy to QA

The lead tester will prompt for QA releases. If we need to release without being
prompted by the lead tester, then make sure to notice him/her.

Commit the changes and make the commit message be the same as the version of the
project (for example 1.2.3).

Run `git flow release publish` from the release branch to trigger a deploy to
QA.

## Deploy to PROD

The lead tester will prompt for a PROD release when they are finished approving
the release on the QA environment.

Pull latest changes on the current release branch (in case someone else has made
"patches" on the active release branch), the `main` branch, and the `develop`
branch (to avoid merge conflicts) and then run `git flow release finish`.

**If you are prompted by the terminal to write in a file, write the same as the
commit message (version of the project, for example 1.2.3), save and close.**

`git flow release finish` will:

- merge the release branch back into 'master'
- tag the release with its name
- back-merge the release into 'develop'
- remove the release branch

Now push the changes from the develop branch with `git push` (this will trigger
a deploy to DevTest).

Then checkout the `main` branch and push the changes and the tags with
`git push && git push --tags` to trigger a deploy to PROD.

The release will first go to a "staging slot", which will have to be "swapped"
for the "prod slot" in the azure prod webapp settings, after the staging slots
url has been tested by a tester and approved for swapping.
