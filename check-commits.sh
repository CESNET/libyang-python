#!/bin/sh

set -e

revision_range="${1?revision range}"

valid=0
revisions=$(git rev-list --reverse "$revision_range")
total=$(echo $revisions | wc -w)
if [ "$total" -eq 0 ]; then
	exit 0
fi
tmp=$(mktemp)
trap "rm -f $tmp" EXIT

allowed_trailers="
Closes
Fixes
Link
Suggested-by
Requested-by
Reported-by
Co-authored-by
Signed-off-by
Tested-by
Reviewed-by
Acked-by
"

n=0
title=
shortrev=
fail=false
repo=CESNET/libyang-python
repo_url=https://github.com/$repo
api_url=https://api.github.com/repos/$repo

err() {

	echo "error: commit $shortrev (\"$title\") $*" >&2
	fail=true
}

check_issue() {
	curl -f -X GET -L --no-progress-meter \
		-H "Accept: application/vnd.github+json" \
		-H "X-GitHub-Api-Version: 2022-11-28" \
		"$api_url/issues/${1##*/}" | jq -r .state | grep -Fx open
}

for rev in $revisions; do
	n=$((n + 1))
	title=$(git log --format='%s' -1 "$rev")
	fail=false
	shortrev=$(printf '%-12.12s' $rev)

	if [ "$(echo "$title" | wc -m)" -gt 72 ]; then
		err "title is longer than 72 characters, please make it shorter"
	fi
	if ! echo "$title" | grep -qE '^[a-z0-9,{}/_-]+: '; then
		err "title lacks a lowercase topic prefix (e.g. 'data: ')"
	fi
	if echo "$title" | grep -qE '^[a-z0-9,{}/_-]+: [A-Z][a-z]'; then
		err "title starts with an capital letter, please use lower case"
	fi
	if ! echo "$title" | grep -qE '[A-Za-z0-9]$'; then
		err "title ends with punctuation, please remove it"
	fi

	author=$(git log --format='%an <%ae>' -1 "$rev")
	if ! git log --format="%(trailers:key=Signed-off-by,only,valueonly,unfold)" -1 "$rev" |
			grep -qFx "$author"; then
		err "'Signed-off-by: $author' trailer is missing"
	fi

	for trailer in $(git log --format="%(trailers:only,keyonly)" -1 "$rev"); do
		if ! echo "$allowed_trailers" | grep -qFx "$trailer"; then
			err "trailer '$trailer' is misspelled or not in the sanctioned list"
		fi
	done

	git log --format="%(trailers:key=Closes,only,valueonly,unfold)" -1 "$rev" > $tmp
	while read -r value; do
		if [ -z "$value" ]; then
			continue
		fi
		case "$value" in
		$repo_url/*/[0-9]*)
			if ! check_issue "$value"; then
				err "'$value' does not reference a valid open issue"
			fi
			;;
		\#[0-9]*)
			err "please use the full issue URL: 'Closes: $repo_url/issues/$value'"
			;;
		*)
			err "invalid trailer value '$value'. The 'Closes:' trailer must only be used to reference issue URLs"
			;;
		esac
	done < "$tmp"

	git log --format="%(trailers:key=Fixes,only,valueonly,unfold)" -1 "$rev" > $tmp
	while read -r value; do
		if [ -z "$value" ]; then
			continue
		fi
		fixes_rev=$(echo "$value" | sed -En 's/([A-Fa-f0-9]{7,}[[:space:]]\(".*"\))/\1/p')
		if ! git cat-file commit "$fixes_rev" >/dev/null; then
			err "trailer '$value' does not refer to a known commit"
		fi
	done < "$tmp"

	body=$(git log --format='%b' -1 "$rev")
	body=${body%$(git log --format='%(trailers)' -1 "$rev")}
	if [ "$(echo "$body" | wc -w)" -lt 3 ]; then
		err "body has less than three words, please describe your changes"
	fi

	if [ "$fail" = true ]; then
		continue
	fi
	echo "ok    commit $shortrev (\"$title\")"
	valid=$((valid + 1))
done

echo "$valid/$total valid commit messages"
if [ "$valid" -ne "$total" ]; then
	exit 1
fi
