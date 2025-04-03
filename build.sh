#!/bin/bash

# =============================================================================
# === Default Values.
# =============================================================================

PART=patch
CUT_RELEASE=NO
IS_DEV_BRANCH=NO


# =============================================================================
# === Get the current Git Branch.
# =============================================================================

echo "========================================================================"
echo "=== Going to get the current Git Branch."
echo "========================================================================"

BRANCH=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')

echo ">>> INFO    : The current Branch is '${BRANCH}'"
echo


# =============================================================================
# === Validate the current Git Branch.
# =============================================================================

echo "========================================================================"
echo "=== Going to validate the current Git Branch."
echo "========================================================================"

if [[ $BRANCH == *"dev"* ]]; then
    echo ">>> INFO    : This is 'develop' Branch."

    PART=minor
    IS_DEV_BRANCH=YES

elif [[ $BRANCH == *"release-"* ]]; then
    echo ">>> INFO    : This is 'release' Branch."

    PART=patch
    IS_DEV_BRANCH=NO

else
    echo ">>> INFO    : This is 'feature' Branch: Exiting."

    exit 1
fi

echo


# =============================================================================
# === Parse Command Line Arguments.
# =============================================================================

echo "========================================================================"
echo "=== Going to parse the Command Line Arguments."
echo "========================================================================"

while [ "$1" != "" ]; do
    case $1 in
        -v|--version)
            if [ -n "$2" ]; then
                PART=$2

                shift   # Past Argument
                shift   # Past Value

                continue
            else
                echo ">>> ERROR   : '-v|--version' requires a non-empty Option Argument."
                echo

                exit 1
            fi
        ;;
        --cut-release)
            CUT_RELEASE=YES

            shift   # past argument
        ;;
        --) # End of all options.
            shift

            break
        ;;
        -?*)
            echo ">>> WARNING : Unknown Option (ignored): $1"
        ;;
        *)  # Default case: If no more options then break out of the loop.
            break
    esac

    shift
done

echo


# =============================================================================
# === Bump the Version.
# =============================================================================

echo "========================================================================"
echo "=== Going to bump the Version."
echo "========================================================================"

# -----------------------------------------------------------------------------
# --- Current Version.
OLD_VERSION=$(cat VERSION)

echo ">>> INFO    : Current Version: ${OLD_VERSION}"

# -----------------------------------------------------------------------------
# --- Bump the Version.
echo ">>> INFO    : Going to bump '${PART}' Version."

if [[ $CUT_RELEASE == "YES" ]]; then
    # --- Create a new Tag.
    bumpversion --tag $PART --allow-dirty
else
    bumpversion $PART --allow-dirty

    # --- Push the Commit.
    git push origin -u HEAD

    echo ">>> INFO    : All set: Exiting."

    exit 1
fi

echo


# =============================================================================
# === Cut the new Release.
# =============================================================================

echo "========================================================================"
echo "Going to cut the new Release."
echo "========================================================================"

# -----------------------------------------------------------------------------
# --- New Version.
NEW_VERSION=$(cat VERSION)

echo ">>> INFO    : New Version: ${NEW_VERSION}"

# -----------------------------------------------------------------------------
# --- 'major.minor' Version.
MM_VERSION="$(cut -d. -f1-2 <<<${NEW_VERSION})"

echo ">>> INFO    : MM  Version: ${MM_VERSION}"

# -----------------------------------------------------------------------------
# --- Update the Tag.
echo ">>> INFO    : Updating the Tag."

git tag -a -f v$NEW_VERSION -m "Create a new Release ${NEW_VERSION}"

# -----------------------------------------------------------------------------
# --- Cut the new Release.
if [[ $IS_DEV_BRANCH == "YES" ]]; then
    # --- New Release Branch Name.
    NEW_RELEASE_BRANCH="release-${MM_VERSION}"

    # --- Switch to a new Release Branch.
    echo ">>> INFO    : Switching to a new Branch '${NEW_RELEASE_BRANCH}'"

    git checkout -b $NEW_RELEASE_BRANCH
fi

# --- Push the Commit.
echo ">>> INFO    : Pushing the Release Branch to Git Repo."

git push -f origin -u HEAD

# --- Push the Tag.
echo ">>> INFO    : Pushing the Tag to Git Repo."

git push origin --tags

# --- Back-merge the Release Branch into Dev Branch.
echo ">>> INFO    : Back-merging the Release Branch into Dev Branch."

git checkout dev
git remote update
git pull origin dev
git merge $BRANCH
git push origin dev


# =============================================================================
# === Build the Package.
# =============================================================================

# echo "========================================================================"
# echo "Going to build and upload the Package."
# echo "========================================================================"

# python ./setup.py sdist bdist_wheel upload -r http://ec2-34-222-8-94.us-west-2.compute.amazonaws.com:8080
python ./setup.py sdist bdist_wheel


# =============================================================================
# === Install the Package.
# =============================================================================

# echo "========================================================================"
# echo "Installing the Package"
# echo "========================================================================"

# pip install --trusted-host --extra-index-url git+http://ec2-34-222-8-94.us-west-2.compute.amazonaws.com:8080/ddaemon-core-python/
