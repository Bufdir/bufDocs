# Releasing and deploy this project

## Make release branch

Start by pulling the latest changes from the main and develop branches and then
(from develop) run:

```bash
$ git flow release start [version]
```

The version is the new version number for the project (for example 1.2.3) and
should follow [semver](https://semver.org/).

## Update version number

Update the version number in ./src/NextJs/package.json to the same as you
chose for the project when creating the release branch (for example 1.2.3).

package.json example:

```json
{
  "name": "projectname",
  "version": "1.2.3"
}
```

Then go to /src/NextJs and run
```bash
$ npm i
$ npm run build
```

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

Commit the changes and make the commit message the same as the new version of the
project (for example 1.2.3).

While on the release branch, run the following to trigger a deploy to QA:
```bash
$ git flow release publish
```

You can check the progress of the builds (one for frontend and one for backend)
in Azure devops pipelines.

## Deploy to PROD

The lead tester will prompt for a PROD release when they are finished approving
the release on the QA environment.

Pull latest changes on the current release branch (in case someone else has made
"patches" on the active release branch), the `main` branch, and the `develop`
branch (to avoid merge conflicts) and then run:
```bash
$ git flow release finish
```

**You will most likely be prompted several times by the terminal to write in a
file.** Check the following list to see the steps `git flow release finish` goes
through. For the merge commits add the version number (for example 1.2.3) to the
message and for the tag, just write the version number before you save and close.

`git flow release finish` will:

- merge the release branch back into 'master'
- tag the release with its name
- back-merge the release into 'develop'
- remove the release branch

Now make sure you are on the develop branch, where you will trigger a deploy to
DevTest by pushing the changes with:

```bash
$ git push
```

Then check out the `main` branch and trigger a deploy to PROD by push the changes
and the tags with:
```bash
git push && git push --tags
```

You can check the progress of the builds (one for frontend and one for backend)
in Azure devops pipelines.

The release will be deployed as a container to a docker registry, the pipeline will
then trigger a revision update to a container app in Azure. This update takes some
time and will usually finish a few minutes after the pipeline has finished.