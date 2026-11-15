# Git refresher for energy modellers

- **Instructor:** Will Usher
- **Length:** 60 minutes
- **Audience:** data analysts and energy modellers

> **Attribution**
>
> This script is derived from [Version Control with Git](https://swcarpentry.github.io/git-novice/),
> Copyright (c) [The Carpentries](https://carpentries.org/), licensed under
> [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> It is not an official Carpentries lesson, and The Carpentries do not endorse it.
>

## Contents

- [Instructor prep](#instructor-prep)
- [Block 1. Why version control, setup check, create a repo](#block-1-why-version-control-setup-check-create-a-repo-10-min)
- [Block 2. Tracking changes](#block-2-tracking-changes-15-min)
- [Block 3. Exploring history](#block-3-exploring-history-15-min)
- [Block 4. Ignoring things](#block-4-ignoring-things-10-min)


## Schedule

| # | Block | Ep | Min | Starts at |
|---|---|---|---|---|
| 1 | Why version control, setup check, create a repo | 1-3 | 10 | 0:00 |
| 2 | Tracking changes | 4 | 15 | 0:10 |
| 3 | Exploring history | 5 | 15 | 0:25 |
| 4 | Ignoring things | 6 | 10 | 0:40 |

Sub-step minutes inside a block can add up to less than the block total. Use the spare minutes for that block's challenge.


## Instructor prep

1. Test the network and the projector. Make the terminal font big.
2. Use a short prompt: `export PS1='$ '`.
3. Make a second folder for solo demos of blocks 6 and 7: you will clone your own repo as `~/Desktop/recipes-at-work`.
4. Clone the lesson repo in a second terminal: `git clone https://github.com/swcarpentry/git-novice.git`. You show its `.gitignore` in block 4, and everyone clones it in block 9.
5. Paste each snippet into the chat as you reach it, for anyone who falls behind.

---

## Block 1. Why version control, setup check, create a repo (10 min)

Original: [Ep 1](https://swcarpentry.github.io/git-novice/01-basics.html), [Ep 2](https://swcarpentry.github.io/git-novice/02-setup.html), [Ep 3](https://swcarpentry.github.io/git-novice/03-create.html)

### Key Messages

- Version control is an unlimited undo. It also lets many people work in parallel.
- `git config --global` sets your name, email and editor once per machine.
- `git init` creates a `.git` folder. One project, one repository. Never put a repo inside another repo.

### 1.1 Open with a familiar folder (2 min)

Show this listing and ask who has a folder like it.

```text
guacamole.md
guacamole_FINAL.md
guacamole_FINAL_v3_lime.md
groceries.md
groceries_new.md
groceries_new_REALLY.md
```

Ask: which version did you cook for last month's party? Git answers that question.

### 1.2 Check the setup (4 min)

Learners type their own name and email.

```bash
git --version
git config --global user.name "Your Name"
git config --global user.email "your.name@openenergytransition.org"
git config --global init.defaultBranch main
git config --global pull.rebase false
git config --global core.editor "nano -w"
git config --list --global
```

VS Code users can run `git config --global core.editor "code --wait"` instead of the nano line.

Line endings: Windows users run `git config --global core.autocrlf true`. macOS and Linux users run `git config --global core.autocrlf input`.

Expected output of the last command:

```text
user.name=Your Name
user.email=your.name@openenergytransition.org
init.defaultbranch=main
pull.rebase=false
core.editor=nano -w
```

`pull.rebase false` is not in the original episode 2. Recent Git (tested on 2.43) otherwise stops the block 7 pull with `fatal: Need to specify how to reconcile divergent branches.`

### 1.3 Create the repository (4 min)

```bash
cd ~/Desktop
mkdir recipes
cd recipes
git init
ls -a
git status
```

Expected:

```text
Initialized empty Git repository in /home/you/Desktop/recipes/.git/
```

```text
.  ..  .git
```

```text
On branch main

No commits yet

nothing to commit (create/copy files and use "git add" to track)
```

### Challenge: a repo inside a repo

Alfredo also wants to track desserts. Inside `recipes`, he runs:

```bash
cd ~/Desktop/recipes
mkdir desserts
cd desserts
git init
```

Does he need the second `git init`? What goes wrong, and how does he fix it?

<details>
<summary>Solution</summary>

No. `recipes` already tracks everything below it. A second `.git` inside it makes a nested repo.
The outer repo lists `desserts/` as untracked, and `git add desserts` fails with:

```text
error: 'desserts/' does not have a commit checked out
error: unable to index file 'desserts/'
fatal: adding files failed
```

Fix: check where you are with `pwd`, then remove only the inner `.git`:

```bash
cd ~/Desktop/recipes
pwd
rm -rf desserts/.git
```

Better: make `desserts/` a plain folder in `recipes`, or keep a separate project outside other repos.

</details>

### Tips

| Problem | Fix |
|---|---|
| Learners copy your name and email from the screen | Check `git config --list --global` on every screen you walk past. |
| Git is older than 2.28, so `init.defaultBranch` does nothing | Run `git branch -M main` after the first commit. |
| Git is older than 2.23, so `git restore` and `git switch` fail | Upgrade Git. Fallbacks: `git checkout -- file` and `git checkout -b name`. |
| macOS shows `.DS_Store` as untracked | Ignore it. Block 4 covers `.gitignore`. |
| Someone ran `git init` in the wrong place, such as their home folder | Move the folder somewhere safe first, then delete the stray `.git`. |

---

## Block 2. Tracking changes (15 min)

Original: [Ep 4: Tracking Changes](https://swcarpentry.github.io/git-novice/04-changes.html)

### Say

- The cycle is: edit, `git add`, `git commit`. The staging area holds what goes into the next snapshot.
- `git diff` shows unstaged changes. `git diff --staged` shows what you are about to commit.
- A good commit message is short and imperative, and says what the change does: "Add ingredients for basic guacamole".

### 2.1 First commit: the recipe skeleton (4 min)

```bash
nano guacamole.md
```

Type these three lines. Save with Ctrl+O, Enter. Exit with Ctrl+X.

```markdown
# Guacamole
## Ingredients
## Instructions
```

Say: a title and two empty sections. We fill them in step by step.

```bash
git status
git add guacamole.md
git status
git commit -m "Create initial structure for a Guacamole recipe"
git log
```

Expected (your hashes and dates will differ):

```text
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	guacamole.md
```

```text
Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
	new file:   guacamole.md
```

```text
[main (root-commit) d54ae52] Create initial structure for a Guacamole recipe
 1 file changed, 3 insertions(+)
 create mode 100644 guacamole.md
```

```text
commit d54ae52ce3708a15b663d4eea7e43f695a258d3f (HEAD -> main)
Author: Your Name <your.name@openenergytransition.org>
Date:   Sun Nov 15 20:41:53 2026 +0000

    Create initial structure for a Guacamole recipe
```

### 2.2 Second commit: ingredients, with the staging area (5 min)

Add three lines under `## Ingredients`:

```markdown
* avocado
* lemon
* salt
```

Say: one ingredient per line keeps diffs readable.

```bash
git diff
git add guacamole.md
git diff
git diff --staged
git commit -m "Add ingredients for basic guacamole"
```

Expected `git diff` before `git add`:

```diff
diff --git a/guacamole.md b/guacamole.md
index b5426e1..0bfdbcb 100644
--- a/guacamole.md
+++ b/guacamole.md
@@ -1,3 +1,6 @@
 # Guacamole
 ## Ingredients
+* avocado
+* lemon
+* salt
 ## Instructions
```

After `git add`, plain `git diff` prints nothing. `git diff --staged` prints the same diff again.

```text
[main bbc1bde] Add ingredients for basic guacamole
 1 file changed, 3 insertions(+)
```

### 2.3 Third commit: lemon to lime, on your own (4 min)

Learners do the full cycle alone: edit, `git diff`, `git add`, `git commit`. Change one word: `lemon` becomes `lime`.

```diff
 * avocado
-* lemon
+* lime
 * salt
```

Suggested message: `git commit -m "Modify guacamole to the traditional recipe"`. Then:

```bash
git log --oneline
```

```text
8cfe7e4 Modify guacamole to the traditional recipe
bbc1bde Add ingredients for basic guacamole
d54ae52 Create initial structure for a Guacamole recipe
```

<details>
<summary>Full guacamole.md after step 2.3</summary>

```markdown
# Guacamole
## Ingredients
* avocado
* lime
* salt
## Instructions
```

</details>

Bonus, before committing: `git diff --word-diff` shows the change as `* [-lemon-]{+lime+}`.

### 2.4 Directories (1 min)

Git tracks files, not folders. Try it:

```bash
mkdir cakes
git status
rmdir cakes
```

`git status` still says `nothing to commit, working tree clean`.
That is why some projects put an empty `.gitkeep` file in a folder they want to keep.

### Challenge: a grocery list

Create `groceries.md` with the prices from Market A, and commit it. **Everyone does this one**, because block 3 counts commits back from it.

<details>
<summary>Solution</summary>

```bash
nano groceries.md
```

```markdown
# Market A
* avocado: 1.35 per unit
* lime: 0.64 per unit
* salt: 2 per kg
```

```bash
git add groceries.md
git commit -m "Write prices for ingredients and their source"
git log --oneline
```

```text
7e312f6 Write prices for ingredients and their source
8cfe7e4 Modify guacamole to the traditional recipe
bbc1bde Add ingredients for basic guacamole
d54ae52 Create initial structure for a Guacamole recipe
```

The staging area can hold changes to several files. `git add guacamole.md groceries.md` puts both into one commit.

</details>

### Tips

- Every learner must complete one full cycle alone. That is the point of step 2.3.
- Stuck in the log pager? Press `q`.
- Avoid `git commit -a` for now. Explicit `git add` stops you committing changes you forgot about.
- `git diff --word-diff` helps when only one word on a line changes.
- If the commit opens an editor, the learner forgot `-m`. Type the message, save and exit.

---

## Block 3. Exploring history (15 min)

Original: [Ep 5: Exploring History](https://swcarpentry.github.io/git-novice/05-history.html)

### Say

- `HEAD` is the latest commit. `HEAD~1` is the one before it. Hashes also work.
- `git restore` puts files back. It changes your working copy, not the history.
- `git revert` adds a new commit that undoes an old one. That is safe once others have pulled your work.

### 3.1 Make an ill-considered change (3 min)

Open `guacamole.md` and add one line at the end. Save, but do not commit.

```text
An ill-considered change
```

```bash
git diff
```

```diff
@@ -4,3 +4,4 @@
 * lime
 * salt
 ## Instructions
+An ill-considered change
```

Say: `git diff` compares your working copy with the last commit. `git diff HEAD` prints the same here.

### 3.2 Compare with older commits (4 min)

```bash
git log --oneline
git diff HEAD~2 guacamole.md
git show HEAD~1
git log --patch guacamole.md
```

`git diff HEAD~2 guacamole.md` compares your working copy with "Add ingredients for basic guacamole". It shows the lime change and the new line:

```diff
@@ -1,6 +1,7 @@
 # Guacamole
 ## Ingredients
 * avocado
-* lemon
+* lime
 * salt
 ## Instructions
+An ill-considered change
```

`git show HEAD~1` prints one commit: its message and its diff.

```text
commit 8cfe7e4...
Author: Your Name <your.name@openenergytransition.org>

    Modify guacamole to the traditional recipe

diff --git a/guacamole.md b/guacamole.md
@@ -1,6 +1,6 @@
 # Guacamole
 ## Ingredients
 * avocado
-* lemon
+* lime
 * salt
 ## Instructions
```

`git log --patch guacamole.md` shows every change to the file, newest first. Press `q` to quit.

### 3.3 Restore the last committed version (1 min)

```bash
git restore guacamole.md
git diff
```

`git diff` prints nothing. The ill-considered line is gone.

### 3.4 Get an old version of the file (3 min)

Use your own hash of "Create initial structure for a Guacamole recipe" from `git log --oneline`.

```bash
git restore -s d54ae52 guacamole.md
cat guacamole.md
git status
git restore guacamole.md
cat guacamole.md
```

```text
# Guacamole
## Ingredients
## Instructions
```

```text
	modified:   guacamole.md
```

```text
# Guacamole
## Ingredients
* avocado
* lime
* salt
## Instructions
```

Say: `-s` is the source commit. Use the commit *before* the change you want to undo. `git restore -s HEAD~3 guacamole.md` does the same here.

### 3.5 Undo a commit with revert (4 min)

Add garlic below salt and commit it.

```diff
 * salt
+* garlic
 ## Instructions
```

```bash
git add guacamole.md
git commit -m "Add garlic"
git revert HEAD
git log --oneline
```

`git revert` opens nano with the message `Revert "Add garlic"`. Save and exit.

```text
[main 6a6a840] Revert "Add garlic"
 Date: ...
 1 file changed, 1 deletion(-)
```

```text
6a6a840 Revert "Add garlic"
1630875 Add garlic
7e312f6 Write prices for ingredients and their source
8cfe7e4 Modify guacamole to the traditional recipe
bbc1bde Add ingredients for basic guacamole
d54ae52 Create initial structure for a Guacamole recipe
```

Say: both commits stay in history. Anyone can see that garlic was tried and undone. The recipe reads fine either way, so only the history tells you it was a mistake.

### Challenge: recover a broken script

Jennifer has been working on `data_cruncher.py` for weeks. This morning's edits broke it. Which commands recover the last committed version?

1. `git restore`
2. `git restore data_cruncher.py`
3. `git restore -s HEAD~1 data_cruncher.py`
4. `git restore -s <hash of last commit> data_cruncher.py`
5. Both 2 and 4

<details>
<summary>Solution</summary>

**5.** Options 2 and 4 both restore the latest committed version. `HEAD` is the last commit.
Option 3 restores the version from one commit earlier, which is not what Jennifer wants.
Option 1 fails:

```text
fatal: you must specify path(s) to restore
```

Use `git restore .` to restore every file.

</details>

### Tips

- **Detached HEAD.** If someone runs `git checkout d54ae52` without a file name, Git says `You are in 'detached HEAD' state`. Get back with `git switch main` (or `git checkout main`).
- **Silent changes.** Change `* lime` back to `* lemon` and save. The recipe still reads fine. Only `git diff` shows the change.
- **Unstage a file.** `git restore --staged guacamole.md` takes it out of the staging area and keeps your edits.

---

## Block 4. Ignoring things (10 min)

Original: [Ep 6: Ignoring Things](https://swcarpentry.github.io/git-novice/06-ignore.html)

### Say

- Track what you write. Ignore what tools generate, and large files you do not want in every clone.
- `.gitignore` is a tracked file. The whole team shares the rules.
- `.gitignore` only affects untracked files. A file that is already tracked stays tracked.

### 4.1 Make some files to ignore (2 min)

```bash
mkdir pictures
touch a.png b.png c.png pictures/cake1.jpg pictures/cake2.jpg
git status
```

```text
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	a.png
	b.png
	c.png
	pictures/
```

### 4.2 Ignore them (3 min)

```bash
nano .gitignore
```

```text
*.png
pictures/
```

```bash
git status
git add .gitignore
git commit -m "Ignore png files and the pictures folder"
git status
```

```text
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	.gitignore
```

```text
[main 754b902] Ignore png files and the pictures folder
 1 file changed, 2 insertions(+)
 create mode 100644 .gitignore
```

```text
On branch main
nothing to commit, working tree clean
```

### 4.3 Ignored, not invisible (2 min)

```bash
git add a.png
git status --ignored
```

```text
The following paths are ignored by one of your .gitignore files:
a.png
hint: Use -f if you really want to add them.
hint: Disable this message with "git config set advice.addIgnoredFile false"
```

```text
Ignored files:
  (use "git add -f <file>..." to include in what will be committed)
	a.png
	b.png
	c.png
	pictures/
```

### 4.4 A real .gitignore (3 min, on your screen)

In your `git-novice` clone, the lesson repo we explore in block 9:

```bash
head -4 .gitignore
```

```text
# sandpaper files
episodes/*html
site/*
!site/README.md
```

| Pattern | What it covers | Why ignore it |
|---|---|---|
| `episodes/*html` | HTML pages built from the Markdown episodes | The build makes them again. |
| `site/*` | the built website | Rebuilt on every build, and large. |
| `!site/README.md` | one file inside `site/` | An exception: it explains the folder, so it stays tracked. |
| `.Rhistory`, `.RData` | R session files | Specific to one machine. |
| `*.pyc` | Python bytecode | Generated when Python runs. |

### Challenge: keep one picture

You want to ignore everything in `pictures/` except `pictures/cake1.jpg`. What goes in `.gitignore`?

<details>
<summary>Solution</summary>

```text
*.png
pictures/*
!pictures/cake1.jpg
```

`pictures/` ignores the folder itself, so Git never looks inside it and the `!` rule has no effect.
`pictures/*` ignores the contents, so the `!` rule can re-include one file.
`git-novice` uses the same form: `site/*`, then `!site/README.md`.

</details>

### Tips

- To stop tracking a file you committed by mistake: `git rm --cached file`, add it to `.gitignore`, and commit.
- Rule order matters. A later `!pattern` overrides an earlier ignore pattern.
