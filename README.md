# apps

A collection of small, single-file web apps, each built from a prompt.

Layout, inspired by [simonw/tools](https://github.com/simonw/tools):

```
{slug}.html         # the app — a single, self-contained HTML file
{slug}.docs.md      # description + the prompt that produced it
```

On every push to `main`, [`.github/workflows/pages.yml`](.github/workflows/pages.yml)
runs [`build_index.py`](build_index.py) to generate `index.html` and deploys
the whole repo to GitHub Pages.

## Adding a new app

1. Create `my-thing.html` at the repo root — a self-contained HTML file.
2. Create `my-thing.docs.md`:

   ```markdown
   # My Thing

   One-paragraph description of what it does.

   ## Prompt

   > the prompt you gave Claude to build it
   ```

3. Commit and push to `main`. The workflow rebuilds `index.html` and redeploys.

## Local preview

```sh
pip install markdown
python build_index.py
python -m http.server 8000
```

Then open <http://localhost:8000/>.

## One-time GitHub Pages setup

In the repo settings: **Settings → Pages → Source: GitHub Actions**. That's it
— the workflow handles everything else.
