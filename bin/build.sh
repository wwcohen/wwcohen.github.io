(cd pubgen/; python3 makepubs.py)
git status > /tmp/git-status.txt
git add `grep modified: /tmp/git-status.txt  | cut -f2 | cut -d':' -f2`
git status
git commit -m 'rebuild pubs'

