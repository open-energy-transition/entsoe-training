# Git refresher for energy modellers: instructor script

- **Instructor:** Will Usher
- **Length:** 150 minutes, including a 10-minute break
- **Audience:** junior data analysts and energy modellers
- **Running example:** learners build the lesson's own `recipes` repo (`guacamole.md`, `groceries.md`, `hummus.md`), then explore the real history of the `git-novice` lesson

> **Attribution**
>
> This script is derived from [Version Control with Git](https://swcarpentry.github.io/git-novice/),
> Copyright (c) [The Carpentries](https://carpentries.org/), licensed under
> [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> It is not an official Carpentries lesson, and The Carpentries do not endorse it.
>
> **What changed**
>
> - The running example is the original recipe example. Each edit is one to three lines, so learners spend their time on git, not on typing.
> - Episodes 1 to 9 are condensed into a 150-minute refresher. Episodes 10 to 14 are dropped.
> - SSH key setup moves to a pre-course checklist.
> - Two blocks are new: "Branches and pull requests" and "Explore a real project", which digs into the history of the `git-novice` lesson itself.
> - Instructor tips are adapted from the lesson's [instructor notes](https://swcarpentry.github.io/git-novice/instructor/instructor-notes.html).

## Contents

- [Block 8. Branches and pull requests](#block-8-branches-and-pull-requests-20-min)
- [Block 10. Wrap-up](#block-10-wrap-up-5-min)


## Block 8. Branches and pull requests (20 min)

No original episode. This block is new.

### Say

- A branch is a movable label on a commit. `main` stays usable while you try things.
- A pull request (PR) asks to merge a branch, with a review in between.
- After the merge, delete the branch. Its commits live on in `main`.

Swap roles: the **Collaborator** writes the branch and opens the PR. The **Owner** reviews and merges.

### 8.1 Collaborator: create a branch (2 min)

```bash
git switch main
git pull origin main
git switch -c add-more-steps
git branch
```

```text
Switched to a new branch 'add-more-steps'
```

```text
* add-more-steps
  main
```

### 8.2 Collaborator: add two steps (5 min)

Add two lines at the end of `guacamole.md`:

```diff
@@ -5,3 +5,5 @@
 * salt
 ## Instructions
 * peel the avocados and put them into a bowl.
+* squeeze the lime into the bowl.
+* add salt and mash with a fork.
```

```bash
git diff
git add guacamole.md
git commit -m "Add lime and salt steps"
git push -u origin add-more-steps
```

```text
[add-more-steps ea716e5] Add lime and salt steps
 1 file changed, 2 insertions(+)
```

```text
remote: Create a pull request for 'add-more-steps' on GitHub by visiting:
remote:      https://github.com/owner-username/recipes/pull/new/add-more-steps
To github.com:owner-username/recipes.git
 * [new branch]      add-more-steps -> add-more-steps
branch 'add-more-steps' set up to track 'origin/add-more-steps'.
```

<details>
<summary>Full guacamole.md on the branch</summary>

```markdown
# Guacamole
## Ingredients
* avocado
* lime
* salt
## Instructions
* peel the avocados and put them into a bowl.
* squeeze the lime into the bowl.
* add salt and mash with a fork.
```

</details>

### 8.3 Collaborator: open the PR (3 min)

1. Open the link from the push output, or click **Compare & pull request** on GitHub.
2. Base: `main`. Compare: `add-more-steps`.
3. Title: "Add more steps". Description: what changed and how you checked it.
4. Under **Reviewers**, pick the Owner. Click **Create pull request**.

### 8.4 Owner: review and merge (5 min)

1. Open the PR. Click **Files changed**. Click a line to leave a comment.
2. Optional: check the branch locally.

   ```bash
   git fetch origin
   git switch add-more-steps
   cat guacamole.md
   git switch main
   ```

   Say: reading the whole file shows whether the steps make sense in order. The diff alone shows only the new lines.
3. Click **Review changes** > **Approve** > **Submit review**.
4. Click **Merge pull request** > **Confirm merge** > **Delete branch**.

### 8.5 Both: update and tidy up (3 min)

```bash
git switch main
git pull origin main
git branch -d add-more-steps
git fetch --prune
git log --oneline --graph --all -4
```

```text
Updating 0d76591..6781557
Fast-forward
 guacamole.md | 2 ++
 1 file changed, 2 insertions(+)
```

```text
Deleted branch add-more-steps (was ea716e5).
```

```text
*   6781557 Merge pull request #1 from owner-username/add-more-steps
|\
| * ea716e5 Add lime and salt steps
|/
*   0d76591 Merge changes from GitHub
...
```

The Owner has a local `add-more-steps` only after checking it in 8.4. If `git branch -d` says `branch 'add-more-steps' not found`, skip it.

### 8.6 The real thing (2 min)

The `git-novice` lesson takes changes the same way. In your clone:

```bash
git log --oneline --graph -7
```

```text
*   d361fe95 Merge pull request #1134 from KevinSpek/fix-dead-links
|\
| * d6cf2562 Replace the Code School Try Git suggestion in instructor notes
|/
*   78b9c02a Merge pull request #1131 from swcarpentry/update/workflows
|\
| * 173a9fc0 [actions] update sandpaper workflow to version v1.0.3
|/
* dc212edb [actions] update workbench docker version to v0.2.9 (#1130)
```

Say: PR #1134 brought the `fix-dead-links` branch into `main`. GitHub deleted the branch after the merge, but the graph keeps its shape. `dc212edb` was squash-merged, so it has no side branch, only `(#1130)` in its message.

### Challenge: delete an unmerged branch

Make a branch, add garlic again, commit, and switch back to `main`. Is the garlic in `main`? Now delete the branch.

<details>
<summary>Solution</summary>

```bash
git switch -c try-garlic
nano guacamole.md
git add guacamole.md
git commit -m "Try garlic again"
git switch main
grep garlic guacamole.md
git branch -d try-garlic
```

`grep` prints nothing: `main` has no garlic. The delete fails, because the commit exists only on that branch:

```text
error: the branch 'try-garlic' is not fully merged
hint: If you are sure you want to delete it, run 'git branch -D try-garlic'
```

`git branch -D try-garlic` deletes it anyway. Git protects work you have not merged.

</details>

### Tips

- `git switch <hash>` refuses to run. `git checkout <hash>` gives a detached HEAD. Go back with `git switch main`.
- The PR link appears only when pushing to GitHub. It is GitHub's message, not Git's.
- Keep branches short-lived and small. Long branches are where conflicts come from. Block 9 shows one that lived for 14 months.

---

## Block 9. Explore a real project: git-novice (15 min)

No original episode. This block is new. It explores the history of the lesson this course is built on.
All hashes and outputs below are real, taken at `main` = `d361fe95`.

### Say

- History is a research tool. It tells you what changed, when, and why.
- `git log -S`, `git log --follow` and `git blame` answer "where did this come from?".
- Small commits with clear messages make that research easy.

### 9.1 Clone (2 min)

```bash
cd ~/Desktop
git clone https://github.com/swcarpentry/git-novice.git
cd git-novice
git log --oneline | wc -l
git log --oneline -5
```

```text
1770
```

```text
d361fe95 Merge pull request #1134 from KevinSpek/fix-dead-links
d6cf2562 Replace the Code School Try Git suggestion in instructor notes
78b9c02a Merge pull request #1131 from swcarpentry/update/workflows
173a9fc0 [actions] update sandpaper workflow to version v1.0.3
dc212edb [actions] update workbench docker version to v0.2.9 (#1130)
```

Say: 1770 commits since 2013, from hundreds of people. Hashes here have 8 characters, because the repo is large.

### 9.2 The smallest diff (1 min)

```bash
git show f1d66b3b
```

````diff
commit f1d66b3b17d025cd75062b27457b3211b2a79e05
Author: Ankur Chaurasia <...>
Date:   Thu Aug 13 11:05:10 2026 +0100

    Fix .gitignore example for pictures folder

    Correcting the folder from pictures/data/ to pictures/pie/

diff --git a/episodes/06-ignore.md b/episodes/06-ignore.md
index c73f3101..cc615fca 100644
--- a/episodes/06-ignore.md
+++ b/episodes/06-ignore.md
@@ -253,7 +253,7 @@ the contents of pictures folder, but create an exception for the contents of the

 ```output
 pictures/*              # ignore everything in pictures folder
-!pictures/pie/          # do not ignore pictures/data/ contents
+!pictures/pie/          # do not ignore pictures/pie/ contents
 ```
````

Say: one line, one fix, and a message that says why. It fixes the same `pictures/*` and `!` pattern we used in block 4.

### 9.3 Follow a renamed file (2 min)

`episodes/04-changes.md` is the episode behind block 2. It has been renamed twice. Without `--follow`, its history stops at the last move.

```bash
git log --oneline episodes/04-changes.md | wc -l
git log --oneline --follow episodes/04-changes.md | wc -l
git log --oneline --follow --diff-filter=R --name-status episodes/04-changes.md
```

```text
134
```

```text
143
```

```text
5177001a Cleaning up existing files before merging new styles
R100	04-changes.md	episodes/04-changes.md
394dc878 Rename files to follow new numbering scheme
R100	03-changes.md	04-changes.md
```

Say: `R100` means a rename with 100% identical content. The file started in 2015 as `03-changes.md`.

### 9.4 A readable two-file diff (2 min)

```bash
git show --stat 15d56848
git show --word-diff 15d56848 -- episodes/14-supplemental-rstudio.md
```

```text
    fixing the names for the changes in more recent commits

 episodes/07-github.md               | 4 ++--
 episodes/14-supplemental-rstudio.md | 2 +-
 2 files changed, 3 insertions(+), 3 deletions(-)
```

```text
@@ -82,7 +82,7 @@ to accept the Xcode license if you are using macOS.
...
![](fig/RStudio_screenshot_navigateexisting.png){alt='RStudio window showing the "Create Project From Existing Directory" dialog. In the dialog, the project working directory has been set to [-"~/Desktop/planets"'}-]{+"~/Desktop/recipes"'}+}
```

Say: one commit, two files, one idea. Both files still said `planets` in image alt text. The line is long, so a plain diff hides the change. `--word-diff` shows the one word that moved.

### 9.5 Side note: an ignore rule with an exception (1 min)

```bash
git check-ignore -v --no-index site/README.md site/index.html
git ls-files site
```

```text
.gitignore:4:!site/README.md	site/README.md
.gitignore:3:site/*	site/index.html
```

```text
site/README.md
```

Say: `git check-ignore -v` names the rule that matches each path. Line 3 ignores the folder contents. Line 4 brings one file back, so `site/README.md` is the only tracked file in `site/`. This is the block 4 challenge in a real repo.

### 9.6 Where did the recipes come from? (6 min)

Learners run these in their clone:

```bash
git log -S'guacamole' --oneline -- episodes/04-changes.md
git show 231fb970^:episodes/04-changes.md | grep -n -m1 mars.txt
git blame -L 405,407 -L 417,419 episodes/04-changes.md
```

```text
1cb39c17 Change challenge commit messages to present tense
231fb970 🥑-ise the lesson: from planets to recipes
```

```text
30:Let's create a file called `mars.txt` that contains some notes
```

```text
58775cbeb 03-changes.md          (Ivan Gonzalez      2015-02-22 14:32:21 -0500 405) and into long-term storage.
58775cbeb 03-changes.md          (Ivan Gonzalez      2015-02-22 14:32:21 -0500 406) First,
231fb970c episodes/04-changes.md (David Perez-Suarez 2023-07-13 20:17:44 +0100 407) we'll improve our recipe by changing 'lemon' to 'lime':
21c9dac88 episodes/04-changes.md (David Perez-Suarez 2024-08-14 16:00:30 +0100 417) * avocado
21c9dac88 episodes/04-changes.md (David Perez-Suarez 2024-08-14 16:00:30 +0100 418) * lime
21c9dac88 episodes/04-changes.md (David Perez-Suarez 2024-08-14 16:00:30 +0100 419) * salt
```

Say:

- `git log -S` lists commits that add or remove a string. The oldest one, `231fb970`, brought the recipes in.
- `231fb970^` is its parent. `git show <commit>:<file>` prints the file as it was then. Before the recipes, learners tracked notes about Mars in `mars.txt`.
- `git blame` follows renames. Lines from 2015 still show the old name `03-changes.md`.
- `git blame` shows the *last* commit that touched a line. `21c9dac8` only switched list markers from `-` to `*`. To look further back, blame its parent: `git blame -L 362,362 21c9dac8^ -- episodes/04-changes.md` points at `231fb970` again.

### Challenge: when did learners first see the recipes?

`231fb970` is dated July 2023. The lesson's website is built from `main`. When did the recipes reach `main`, and through which pull request?

<details>
<summary>Solution</summary>

Search only the commits on `main` itself, and look inside merge commits:

```bash
git log --first-parent -m -S'guacamole' --format='%h %ad %s' --date=short -- episodes/04-changes.md
```

```text
560e602e 2025-05-19 Merge pull request #1086 from ndporter/patch-1
ecbc85e0 2024-09-29 Merge pull request #1003 from swcarpentry/recipes-draft
```

`--first-parent` follows only `main`'s own line of commits. `-m` lets `-S` look at the changes each merge brought in.
The oldest hit is the answer: PR #1003, merged on 29 September 2024. The recipes sat on the `recipes-draft` branch for about 14 months.
`git log --oneline --merges --grep=recipes` shows the extra work that took: `f0466725 Merge branch 'main' into recipes-draft` pulled `main` back into the branch to catch up.

</details>

### Optional finale: is anything left of the planets?

```bash
git grep -n -i planets
git log -S'planets' --oneline -1
```

```text
15d56848 fixing the names for the changes in more recent commits
```

Say: `git grep` searches today's files and finds nothing. `git log -S` searches history. The newest commit that removed `planets` is `15d56848`, the two-file commit from 9.4. Together, the two commands tell you when something disappeared.

### Tips

- The lesson keeps changing. If outputs differ from this script, run `git switch --detach d361fe95` to match it. Go back with `git switch main`.
- `git blame` prints 9-character hashes such as `231fb970c`, one more than `git log`. Both name the same commit.
- `git log -p -S'guacamole'` shows the matching diffs too.
- Some terminals show the 🥑 in the commit message as a box. That is a font issue, not a git one.

---

## Block 10. Wrap-up (5 min)

### A typical work session

Ask learners to put the steps in order before you show the table.

| Order | Action | Command |
|---|---|---|
| 1 | Update local | `git pull origin main` |
| 2 | Branch, if the change is bigger than a typo | `git switch -c my-change` |
| 3 | Make changes | `nano guacamole.md` |
| 4 | Stage | `git add guacamole.md` |
| 5 | Commit | `git commit -m "Describe the change"` |
| 6 | Update remote | `git push origin my-change`, then open a PR |
| 7 | Celebrate | |

### Cheat sheet

| Task | Command |
|---|---|
| What changed? | `git status`, `git diff`, `git diff --staged` |
| Save a snapshot | `git add <file>`, `git commit -m "..."` |
| History | `git log --oneline --graph --all`, `git show <hash>` |
| Find a string in history | `git log -S'text' --oneline` |
| Follow a renamed file | `git log --follow <file>` |
| Who wrote this line? | `git blame <file>` |
| Throw away edits | `git restore <file>` |
| Old version of a file | `git restore -s <hash> <file>` |
| Undo a shared commit | `git revert <hash>` |
| Sync | `git pull origin main`, `git push origin main` |
| Branches | `git switch -c <name>`, `git switch main`, `git branch -d <name>` |
| Escape a merge | `git merge --abort` |

### Close

1. Ask each learner for one thing that worked and one thing to improve.
2. Point to the full lesson for self-study: https://swcarpentry.github.io/git-novice/
3. Homework: in your `git-novice` clone, find when episode 5 switched from `git checkout` to `git restore`, and who made the change.

<details>
<summary>Homework solution</summary>

```bash
git log -S'git restore' --format='%h %ad %an %s' --date=short -- episodes/05-history.md
```

The oldest line is the answer:

```text
c4cb6383 2023-06-05 Koen Leuveld change the use of git checkout to git restore
```

</details>
