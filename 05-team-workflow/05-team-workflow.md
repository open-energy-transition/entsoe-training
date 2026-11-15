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

- [Block 5. Remotes in GitHub](#block-5-remotes-in-github-20-min)
- [Block 6. Collaborating](#block-6-collaborating-15-min)
- [Block 7. Conflicts](#block-7-conflicts-15-min)

## Block 5. Remotes in GitHub (20 min)

Original: [Ep 7: Remotes in GitHub](https://swcarpentry.github.io/git-novice/07-github.html)

### Say

- Git is the tool. GitHub is a company that hosts Git repositories. GitLab is a self-hosted alternative to GitHub.
- A remote is a named URL. `origin` is only a convention. Some projects call the shared repo `upstream`.
- `git push` sends your commits. `git pull` fetches commits and merges them.

Draw this on the whiteboard:

```text
  your laptop                      GitHub / GitLab
 +------------------+    push    +-----------------------+
 | recipes          | ---------> | you/recipes           |
 | remote: origin   | <--------- |                       |
 +------------------+    pull    +-----------------------+
                                        ^        |
                                   push |        | clone, pull
                                        |        v
                                 +-----------------------+
                                 | partner's laptop      |
                                 +-----------------------+
```

### 5.1 Check SSH (2 min)

SSH keys were set up before the session.

```bash
ssh -T git@github.com
```

```text
Hi your-username! You've successfully authenticated, but GitHub does not provide shell access.
```

If this fails, pair the learner with a helper and continue. They can use HTTPS for today.

### 5.2 Create an empty repo on GitHub / GitLab (4 min)

1. On GitHub, click **+** then **New repository**.
2. Owner: your personal account. Name: `recipes`. Private is fine.
3. Leave **README**, **.gitignore** and **licence** unset. The repo must be empty.
4. Click **Create repository**. Copy the SSH URL.

### 5.3 Connect and push (6 min)

```bash
git remote add origin git@github.com:your-username/recipes.git
git remote -v
git push -u origin main
```

```text
origin	git@github.com:your-username/recipes.git (fetch)
origin	git@github.com:your-username/recipes.git (push)
```

```text
To github.com:your-username/recipes.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

Say: `-u` links your local `main` to `origin/main`. From now on `git status` tells you if you are ahead or behind.

### 5.4 Look at it on GitHub / GitLab (4 min)

Refresh the page. Click **commits**. Click a commit to see its diff. Look at the file list and note that `a.png` and `pictures/` are not there.

### 5.5 Pull (1 min)

```bash
git pull origin main
```

```text
From github.com:your-username/recipes
 * branch            main       -> FETCH_HEAD
Already up to date.
```

### Challenge: the README checkbox

What would have happened if you had ticked "Add a README file" when creating the GitHub repo?

<details>
<summary>Solution</summary>

GitHub would have made its own first commit. Your local history and GitHub's history would share no commit.
`git push` is rejected, and `git pull origin main` refuses:

```text
fatal: refusing to merge unrelated histories
```

You can force it with `git pull --allow-unrelated-histories origin main`. Check both sides carefully before you do.
If you also had a local `README.md`, the two would clash as `CONFLICT (add/add)`, which you resolve like any other conflict.
It is easier to create the GitHub repo empty.

</details>

### Tips

| Problem | Fix |
|---|---|
| Typo in the remote URL or name | Diagnose with `git remote -v`. Fix with `git remote set-url origin <url>` or `git remote rename <old> <new>`. |
| `Permission denied (publickey)` | The SSH key is not on GitHub, or not authorised for the organisation (SSO). |
| Push output looks different from yours | Normal. It varies with Git version and with `-u`. |

---

## Block 6. Collaborating (15 min)

Original: [Ep 8: Collaborating](https://swcarpentry.github.io/git-novice/08-collab.html)

### Say

- In each pair, one person is the **Owner** and one is the **Collaborator**. The Collaborator works in the Owner's repo.
- `git clone` copies a repo and sets up `origin` for you.
- The basic workflow: pull, edit, add, commit, push.

### 6.1 Give access (3 min)

1. **Owner:** on GitHub, open `recipes` > **Settings** > **Collaborators** > **Add people**. Enter the partner's username.
2. **Collaborator:** accept the invite at https://github.com/notifications or from the email.

### 6.2 Collaborator: clone (2 min)

Clone into the Desktop, not inside your own `recipes`.

```bash
cd ~/Desktop
git clone git@github.com:owner-username/recipes.git ~/Desktop/owner-recipes
cd ~/Desktop/owner-recipes
```

```text
Cloning into '/home/you/Desktop/owner-recipes'...
```

### 6.3 Collaborator: add hummus (4 min)

```bash
nano hummus.md
```

```markdown
# Hummus
## Ingredients
* chickpeas
* lemon
* olive oil
* salt
```

```bash
git status
git add hummus.md
git commit -m "Add ingredients for hummus"
git push origin main
```

```text
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	hummus.md
```

```text
[main 1ee92c9] Add ingredients for hummus
 1 file changed, 6 insertions(+)
 create mode 100644 hummus.md
```

```text
To github.com:owner-username/recipes.git
   754b902..1ee92c9  main -> main
```

### 6.4 Owner: review, then pull (4 min)

```bash
git fetch origin
git status
git diff main origin/main
git pull origin main
```

```text
Your branch is behind 'origin/main' by 1 commit, and can be fast-forwarded.
```

`git diff main origin/main` shows the new `hummus.md` before you merge it.

```text
Updating 754b902..1ee92c9
Fast-forward
 hummus.md | 6 ++++++
 1 file changed, 6 insertions(+)
 create mode 100644 hummus.md
```

### Challenge: who added hummus?

The Owner wants to know which commit added chickpeas, and who made it, using only the command line.

<details>
<summary>Solution</summary>

```bash
git log -S'chickpeas' --format='%h %an %s'
```

```text
1ee92c9 Collaborator Name Add ingredients for hummus
```

`git log -S` finds commits that add or remove a string. `git blame hummus.md` shows the author of every line. We use both in block 9.

</details>

### Tips

- **Most common mistake:** pushing before pulling. Then the next pull may give a conflict. That is block 7.
- Clone from `~/Desktop`, never from inside another repo.
- Working solo? Clone your own repo a second time as `~/Desktop/recipes-at-work` and play both roles.

---

## Block 7. Conflicts (15 min)

Original: [Ep 9: Conflicts](https://swcarpentry.github.io/git-novice/09-conflict.html)

### Say

- A conflict happens when two people change the same lines.
- Git never overwrites someone's work silently. It stops and marks the lines.
- Resolving a conflict is a decision about content, not a git chore. Agree on the recipe.

### 7.1 Both: start in sync (1 min)

```bash
git pull origin main
cat guacamole.md
```

```text
# Guacamole
## Ingredients
* avocado
* lime
* salt
## Instructions
```

### 7.2 Collaborator: first instruction (2 min)

Add one line at the end of `guacamole.md`:

```text
* put one avocado into a bowl.
```

```bash
git add guacamole.md
git commit -m "First step on the instructions"
git push origin main
```

### 7.3 Owner: a different first instruction, without pulling (3 min)

Do **not** pull first. Add a different line at the same place:

```text
* peel the avocados
```

```bash
git add guacamole.md
git commit -m "Add first step"
git push origin main
```

```text
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'github.com:owner-username/recipes.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
```

### 7.4 Owner: pull and see the conflict (2 min)

```bash
git pull origin main
```

```text
Auto-merging guacamole.md
CONFLICT (content): Merge conflict in guacamole.md
Automatic merge failed; fix conflicts and then commit the result.
```

```bash
nano guacamole.md
```

```text
# Guacamole
## Ingredients
* avocado
* lime
* salt
## Instructions
<<<<<<< HEAD
* peel the avocados
=======
* put one avocado into a bowl.
>>>>>>> 59345edf8f4138cc5d6a419a967e707bc899ea23
```

Say: above `=======` is your version (`HEAD`). Below it is the version from GitHub. The hash names the incoming commit.

### 7.5 Owner: resolve, add, commit, push (4 min)

The pair agrees on one step that combines both. Delete the markers so the end of the file reads:

```text
## Instructions
* peel the avocados and put them into a bowl.
```

```bash
git add guacamole.md
git status
git commit -m "Merge changes from GitHub"
git push origin main
```

```text
All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)
```

```text
[main 0d76591] Merge changes from GitHub
```

### 7.6 Collaborator: pull the merge (1 min)

```bash
git pull origin main
git log --oneline --graph -6
```

```text
Fast-forward
 guacamole.md | 2 +-
```

```text
*   0d76591 Merge changes from GitHub
|\
| * 59345ed First step on the instructions
* | 796c011 Add first step
|/
* 1ee92c9 Add ingredients for hummus
* 754b902 Ignore png files and the pictures folder
* 6a6a840 Revert "Add garlic"
```

### 7.7 What the merge kept (2 min)

| Version | First instruction |
|---|---|
| Owner (`HEAD`) | `* peel the avocados` |
| Collaborator (incoming) | `* put one avocado into a bowl.` |
| Merged | `* peel the avocados and put them into a bowl.` |

Say: the merged line matches neither side. Git could not have written it. Only the pair could, because only they know what the recipe should say. A silent merge would have kept one step and lost the other.

### Challenge: a conflict in a picture

Both partners take a photo, save it as `guacamole.jpg` and commit it. Fake one with random bytes:

```bash
head -c 1024 /dev/urandom > guacamole.jpg
git add guacamole.jpg
git commit -m "Add picture of guacamole"
```

The Collaborator pushes first. The Owner pushes, gets rejected, and pulls. What happens, and how do you fix it?

<details>
<summary>Solution</summary>

```text
warning: Cannot merge binary files: guacamole.jpg (HEAD vs. 940f2bf64136a4d57ef73548d16cadc5926ecf9d)
Auto-merging guacamole.jpg
CONFLICT (add/add): Merge conflict in guacamole.jpg
Automatic merge failed; fix conflicts and then commit the result.
```

Git cannot put markers in an image. Pick one side, then add and commit:

```bash
git checkout --theirs guacamole.jpg
git add guacamole.jpg
git commit -m "Use collaborator's picture of guacamole"
git push origin main
```

Use `--ours` to keep your own. To keep both, save them under two names, such as `guacamole-only.jpg` and `guacamole-nachos.jpg`, as the original lesson does.
Note that the block 4 rule `*.png` does not cover `.jpg` files.

</details>

### Tips

- **Forgot `git add` after fixing the file?** `git commit` fails with `Committing is not possible because you have unmerged files.` Run `git status`, then `git add guacamole.md`.
- **Want out?** `git merge --abort` returns to the state before the pull.
- **Divergent branches error?** The learner skipped `git config --global pull.rebase false` in block 1. Run it and pull again.
- Expect mistakes here, including your own. Everyone is tired by now.
- VS Code shows "Accept Current / Accept Incoming" buttons above conflict markers. Fine to use.
