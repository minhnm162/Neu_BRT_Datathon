# GitHub Large File Fix

GitHub rejects normal Git pushes when any single file is larger than 100 MB.

The current risky file is:

```text
aggregated_tables/order_lines_enriched.csv
```

It is an analysis-ready generated table and can be recreated by running:

```powershell
python scripts\pipeline_review_fixes.py
```

## Recommended Approach

Keep the large CSV locally, but do not track it in normal Git.

If it is already tracked in your local commit, remove it from Git tracking while keeping the file on disk:

```powershell
git rm --cached aggregated_tables/order_lines_enriched.csv
git add .gitignore aggregated_tables/README.md docs_git_large_file_fix.md
git commit --amend --no-edit
git push -u origin test_R
```

If Git still rejects the push because the file exists in an older unpushed commit, use an interactive rebase or create a fresh branch from the remote base and recommit without the large file.

## Alternative

Use Git LFS:

```powershell
git lfs install
git lfs track "aggregated_tables/order_lines_enriched.csv"
git add .gitattributes aggregated_tables/order_lines_enriched.csv
git commit -m "Track large aggregated table with Git LFS"
git push -u origin test_R
```

For competition review, the recommended option is usually to commit the script and small artifacts, not the 188 MB generated CSV.
