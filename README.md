# awesome-single-cell-stars

A curated list of single-cell analysis software packages, sorted by GitHub stars.

## About

This repository automatically fetches and displays repositories from [seandavi/awesome-single-cell](https://github.com/seandavi/awesome-single-cell) with their GitHub star counts. The page is updated daily via GitHub Actions.

## Features

- **Star Counts**: View the number of GitHub stars for each repository
- **Sortable**: Sort by stars (ascending/descending) or name (A-Z/Z-A)
- **Filterable**: Filter by category or view all packages
- **Clean Design**: Minimal GitHub-like theme
- **Auto-Updated**: Data refreshes automatically every day

## View the Page

Visit: [https://fbnrst.github.io/awesome-single-cell-stars/](https://fbnrst.github.io/awesome-single-cell-stars/)

## How It Works

1. A GitHub Action runs daily (or on-demand)
2. Python script fetches the awesome-single-cell README
3. Script extracts GitHub repositories and their categories
4. GitHub API is queried to get star counts
5. Data is saved as JSON and deployed to GitHub Pages
6. Static HTML page displays the data with sorting and filtering

## Development

### Manual Update

You can manually trigger the update workflow from the Actions tab.

### Local Testing

```bash
# Install Python 3.11+
# Set GITHUB_TOKEN environment variable
export GITHUB_TOKEN=your_token_here

# Run the script
python fetch_repos.py

# Open index.html in a browser
```

## License

BSD 3-Clause License - See LICENSE file for details

## Credits

Data source: [seandavi/awesome-single-cell](https://github.com/seandavi/awesome-single-cell)