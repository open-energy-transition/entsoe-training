# Git refresher for energy modellers: instructor script

- **Instructor:** Will Usher
- **Length:** 150 minutes, including a 10-minute break
- **Audience:** junior data analysts and energy modellers
- **Running example:** learners build the lesson's own `recipes` repo (`guacamole.md`, `groceries.md`, `hummus.md`), then explore the real history of [PyPSA](https://github.com/PyPSA/PyPSA), an open-source energy system modelling tool

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
> - Two blocks are new: "Branches and pull requests" and "Explore a real project", which digs into the history of PyPSA.
> - Instructor tips are adapted from the lesson's [instructor notes](https://swcarpentry.github.io/git-novice/instructor/instructor-notes.html).

## Contents

- [Instructor prep](#instructor-prep)
- [Block 8. Branches and pull requests](#block-8-branches-and-pull-requests-20-min)
- [Block 9. Exploring a real repository](#block-9-explore-a-real-project-pypsa-15-min)
- [Block 10. Wrap-up](#block-10-wrap-up-5-min)

## Schedule

| # | Block | Ep | Min | Starts at |
|---|---|---|---|---|
| 8 | Branches and Pull Requests| 8 | 20 | 0:00 |
| 9 | Exploring a Real Repository | 9 | 15 | 0:20 |
| 10 | Wrap-up | 10 | 5 | 0:35 |

## Instructor prep

1. Test the network and the projector. Make the terminal font big.
2. Use a short prompt: `export PS1='$ '`.
3. Make a second folder for solo demos of blocks 6 and 7: you will clone your own repo as `~/Desktop/recipes-at-work`.
4. Clone two repos in a second terminal: `git clone https://github.com/swcarpentry/git-novice.git` and `git clone https://github.com/PyPSA/PyPSA.git`. You show the lesson's `.gitignore` in block 4 and its graph in 8.6. Everyone clones PyPSA in block 9.
5. Paste each snippet into the chat as you reach it, for anyone who falls behind.

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
- Keep branches short-lived and small. Long branches are where conflicts come from. Block 9 shows one that needed three catch-up merges from `master` before it landed.

---

## Block 9. Explore a real project: PyPSA (15 min)

### Say

- History is a research tool. It tells you what changed, when, and why.
- `git log -S`, `git log --follow` and `git blame` answer "where did this come from?".
- Small commits with clear messages make that research easy.
- PyPSA is an open-source tool for modelling energy systems. Many of you use it already.

### 9.1 Clone (2 min)

```bash
cd ~/Desktop
git clone https://github.com/PyPSA/PyPSA.git
cd PyPSA
git log --oneline | wc -l
git log --oneline -5
```

```text
3497
```

```text
96253dbf docs: make wind/solar split unique in stochastic example (#2156)
1b450e9b fix: distribute slack on single-bus sub-networks for all slack weights (#2152)
0b2a4c84 fix: count storage withdrawal in primary energy and operational limits (#2133)
d5091d3c fix: support linopy 1.0 next to linopy 0.10 (#2129)
fdb52bca fix: raise for `committable` on components without unit commitment (#2127)
```

Say: 3497 commits since October 2015, from about 150 authors. The clone is about 80 MB and takes a few seconds on good Wi-Fi. Hashes here have 8 characters, because the repo is large. The `(#2156)` at the end is the pull request number. PyPSA's main branch is called `master`, not `main`.

### 9.2 The smallest diff (1 min)

```bash
git show 38c9f418
```

```diff
commit 38c9f418cc1a57f64263e00986bbaf080d0d8f8b
Author: Koen van Greevenbroek <...>
Date:   Mon Feb 26 14:49:40 2024 +0000

    Fix calculation of MGA cost bound

diff --git a/pypsa/optimization/abstract.py b/pypsa/optimization/abstract.py
index f2aa7170..30412066 100644
--- a/pypsa/optimization/abstract.py
+++ b/pypsa/optimization/abstract.py
@@ -377,7 +377,7 @@ def optimize_mga(
 
     # build budget constraint
     if not multi_investment_periods:
-        optimal_cost = (n.statistics.capex() + n.statistics.opex()).sum()
+        optimal_cost = n.statistics.capex().sum() + n.statistics.opex().sum()
         fixed_cost = n.statistics.installed_capex().sum()
     else:
         w = n.investment_period_weightings.objective
```

Say: one line, one fix. MGA explores near-optimal solutions within a cost budget. `+` on two pandas Series lines them up by index first. A row that exists in only one of them becomes NaN, and `.sum()` skips NaN. So costs could drop out of the budget. Summing each one first fixes it. A one-line diff is easy to review, and easy to find again.

### 9.3 Follow a renamed file (2 min)

`pypsa/networks.py` holds the `Network` class, the `n` in `n.optimize()`. It has been renamed five times. Without `--follow`, its history stops at the last move.

```bash
git log --oneline pypsa/networks.py | wc -l
git log --oneline --follow pypsa/networks.py | wc -l
git log --oneline --follow --diff-filter=R --name-status pypsa/networks.py
```

```text
78
```

```text
412
```

```text
c36338c1 feat: introduce component class (#1075)
R081	pypsa/components.py	pypsa/networks.py
388a2698 Include a more friendly package format with setup.py etc.
R100	components.py	pypsa/components.py
9e15c167 Rename classes.py and remove vresutils dependency
R100	classes.py	components.py
0112a5c1 Allow generator capacity to be extended in the model
R092	network.py	classes.py
6685547d Renamed classes to network
R098	classes.py	network.py
```

Say: `R100` means a rename with 100% identical content. `R081` means 81% similar: the file moved and changed in the same commit. The file started in 2015 as `classes.py`, and was renamed back and forth on the same day.

### 9.4 A readable two-file diff (2 min)

```bash
git show --stat 355f4efb
git show --word-diff -U0 355f4efb
```

```text
    rename capex_fixed to installed_capex

 pypsa/optimization/abstract.py | 2 +-
 pypsa/statistics.py            | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)
```

```text
...
@@ -326 +326 @@ def optimize_mga(
    fixed_cost = [-n.statistics.capex_fixed().sum()-]{+n.statistics.installed_capex().sum()+}
...
@@ -239 +239 @@ class StatisticsAccessor:
    def [-capex_fixed(self,-]{+installed_capex(self,+} comps=None, aggregate_groups="sum", groupby=None):
```

Say: one commit, two files, one idea. It renames a method and its only caller together, so no commit in between is broken. `--word-diff` shows the words that moved, and `-U0` drops the context lines.

### 9.5 Side note: an ignore rule with an exception (1 min)

```bash
git check-ignore -v --no-index docs/examples/unit-commitment.ipynb examples/scratch.ipynb
git ls-files '*.ipynb' | wc -l
git ls-files 'docs/*.ipynb' | wc -l
```

```text
.gitignore:14:!/docs/**/*.ipynb	docs/examples/unit-commitment.ipynb
.gitignore:13:*.ipynb	examples/scratch.ipynb
```

```text
56
```

```text
56
```

Say: `git check-ignore -v` names the rule that matches each path. The path does not need to exist: `examples/scratch.ipynb` is made up. Line 13 ignores every notebook. Line 14 brings back notebooks anywhere under `docs/`. So all 56 tracked notebooks live in `docs/`. This is the block 4 challenge in a real repo.

### 9.6 Where did `n.optimize()` come from? (6 min)

Learners run these in their clone:

```bash
git log -S'def optimize(' --oneline -- pypsa
git show 9e7f1834^:pypsa/components.py | grep -n -e 'def lopf' -e 'import network_lopf'
git blame -L 30,31 -L 170,170 pypsa/networks.py
```

```text
0e391be4 refactor: remove `v1.0.0` deprecations (#1257)
9e7f1834 Integrate new optimization module based on linopy (#336)
```

```text
49:from pypsa.opf import network_lopf, network_opf
66:    from pypsa.linopf import network_lopf as network_lopf_lowmem
625:    def lopf(
```

```text
^2fbc2bef classes.py          (Tom Brown    2015-10-12 17:06:19 +0200  30) import numpy as np
8ec3287d3 classes.py          (Tom Brown    2015-10-13 18:25:06 +0200  31) import pandas as pd
5f2e4d3f7 pypsa/components.py (Lukas Trippe 2024-08-28 11:28:36 +0200 170)         self.optimize: OptimizationAccessor = OptimizationAccessor(self)
```

Say:

- `git log -S` lists commits that add or remove a string. The oldest one, `9e7f1834`, brought in `optimize`, built on linopy, in October 2022. The newer one removed an old, deprecated function form of it.
- `9e7f1834^` is its parent. `git show <commit>:<file>` prints the file as it was then. Before `optimize`, you ran `n.lopf()`. It used Pyomo (`pypsa.opf`) or the leaner `pypsa.linopf`.
- `git blame` follows renames. Lines from 2015 still show the old name `classes.py`. The `^` marks the very first commit.
- `git blame` shows the *last* commit that touched a line. `5f2e4d3f` only added a type hint. To look further back, blame its parent: `git blame -L 242,242 5f2e4d3f^ -- pypsa/components.py` points at `9e7f1834` again.

### Challenge: when did the lean `lopf` reach `master`?

`pypsa.linopf` started on a branch called `nomopyomo` ("no more Pyomo"). Its first commit, `cf787d7b`, is dated 15 October 2019. PyPSA releases come from `master`. When did it reach `master`, and through which pull request?

<details>
<summary>Solution</summary>

Search only the commits on `master` itself, and look inside merge commits:

```bash
git log --first-parent -m -S'nomopyomo' --format='%h %ad %s' --date=short -- pypsa
```

```text
21f8d20c 2024-05-15 Merge pull request #884 from PyPSA/remove-pyomo
5b84f74b 2019-12-19 Merge pull request #99 from PyPSA/nomopyomo
```

`--first-parent` follows only `master`'s own line of commits. `-m` lets `-S` look at the changes each merge brought in.
The oldest hit is the answer: PR #99, merged on 19 December 2019, about two months after the first commit. The newer hit is the end of the story: PR #884 removed the Pyomo code and `n.lopf()` in May 2024.
`git log --oneline --merges --grep="'master' into nomopyomo"` shows the extra work it took: three merges pulled `master` back into the branch to catch up.

</details>

### Optional finale: is anything left of `capex_fixed`?

```bash
git grep -n capex_fixed
git log -S'capex_fixed' --oneline -1
```

```text
355f4efb rename capex_fixed to installed_capex
```

Say: `git grep` searches today's files and finds nothing. `git log -S` searches history. The newest commit that removed `capex_fixed` is `355f4efb`, the two-file commit from 9.4. Together, the two commands tell you when something disappeared. Drop the `-1` to see it was added one day earlier, in `76371326`.

### Tips

- PyPSA keeps changing. If outputs differ from this script, run `git switch --detach 96253dbf` to match it. Go back with `git switch master`.
- Do not clone with `--filter=blob:none`. The clone is smaller (15 MB), but `git log -S` then downloads old files one at a time and takes minutes.
- `git blame` prints 9-character hashes such as `5f2e4d3f7`, one more than `git log`. Both name the same commit.
- `git log -p -S'def optimize('` shows the matching diffs too.
- `-S` takes a plain string, not a pattern, so the `(` in `'def optimize('` needs no escaping.

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
3. Homework: in your PyPSA clone, find when the `Link` component arrived, and who added it.

<details>
<summary>Homework solution</summary>

```bash
git log -S'class Link' --format='%h %ad %an %s' --date=short -- pypsa/components.py
```

```text
1e104c95 2017-01-05 Tom Brown all: abolish component classes and all _types sets
6a076104 2016-07-03 Tom Brown Allow generic sector coupling with lossy link
```

The oldest line is the answer: Tom Brown, July 2016. `git show -s 6a076104` prints the full message: "Link is a directed controllable branch with efficiency, which can be used to connect generic buses." The newer line removed the class again when PyPSA dropped per-component classes. `Link` itself stayed.

</details>
