# Publish the profile

1. Create the public repository `gc292/gc292` on GitHub.
2. Upload `README.md`, `assets/`, `scripts/` and `.github/` to its root. Keep the directory structure; remember that `.github` is a hidden folder.
3. In the repository's Actions tab, run **Refresh profile statistics** once. It will subsequently run daily, using the automatically supplied GitHub token. No personal access token is needed.

The README will appear on your GitHub profile automatically. GitHub reference: https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme

The banner and project cards are original, local SVG assets. Badges are served by Shields.io. Statistics are generated from your actual public repositories; private repositories and forks are excluded. The GitHub profile repository itself is included once published. This is a count of each repository's primary language, not lines of code or contribution history.

`preview.html` is a local visual preview, not a deployed website. It uses the same artwork as the README, with an approximation of GitHub's dark Markdown layout. Do not upload it or this setup guide unless you want them in the repository.

To update the artwork locally: `python3 scripts/update_stats.py`.
