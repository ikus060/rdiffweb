#!/bin/bash

# Generate version string
export VERSION=$(date "+%Y%m%d.%H%M")

echo Updating changelog
git-dch --debian-tag="%(version)s" --new-version=$VERSION --debian-branch master --release

echo Committing changelog
git add debian/changelog
git commit -m "Annotate changelog"

echo Tagging current version
git tag $VERSION
git push
git push --tags

echo Building package
git-buildpackage --git-pbuilder --git-dist=trusty --git-arch=amd64 --git-ignore-branch


# Push package
echo To dput, run:
echo dput --unchecked -c /etc/dput.cf trusty packages.changes
