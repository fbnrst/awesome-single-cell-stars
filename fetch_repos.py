#!/usr/bin/env python3
"""
Fetch repositories from awesome-single-cell and get their star counts.
"""

import re
import json
import urllib.request
import urllib.error
import time
import os
import sys
import unicodedata

# GitHub API settings
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
AWESOME_SC_URL = 'https://raw.githubusercontent.com/seandavi/awesome-single-cell/refs/heads/master/README.md'

def fetch_readme():
    """Fetch the awesome-single-cell README."""
    print(f"Fetching README from {AWESOME_SC_URL}...")
    with urllib.request.urlopen(AWESOME_SC_URL) as response:
        return response.read().decode('utf-8')

def parse_github_url(url):
    """Extract owner and repo name from GitHub URL."""
    # Match various GitHub URL patterns
    patterns = [
        r'github\.com/([^/]+)/([^/\s\)]+)',
        r'github\.com/([^/]+)/([^/\s\)]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            owner = match.group(1)
            repo = match.group(2)
            # Clean up repo name
            repo = re.sub(r'[^\w\-\.]', '', repo)
            return owner, repo
    return None, None

def get_star_count(owner, repo):
    """Fetch star count from GitHub API."""
    url = f'https://api.github.com/repos/{owner}/{repo}'
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('stargazers_count', 0)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"  Warning: Repository {owner}/{repo} not found")
        elif e.code == 403:
            print(f"  Warning: Rate limit exceeded or forbidden for {owner}/{repo}")
        else:
            print(f"  Warning: Error fetching {owner}/{repo}: {e}")
        return 0
    except Exception as e:
        print(f"  Warning: Error fetching {owner}/{repo}: {e}")
        return 0

def remove_emojis(text):
    """Remove emoji characters from text."""
    # Remove emoji characters using a comprehensive pattern
    # This covers most emoji ranges in Unicode
    emoji_pattern = re.compile(
        "["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002600-\U000026FF"  # Miscellaneous Symbols
        "\U00002700-\U000027BF"  # Dingbats
        "\U0000FE00-\U0000FE0F"  # Variation Selectors
        "\u200d"                 # Zero Width Joiner
        "\u2640-\u2642"          # Gender symbols
        "\u2600-\u2B55"          # Miscellaneous symbols
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"                 # Variation selector
        "\u3030"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text).strip()

def parse_repos(readme_content):
    """Parse repositories from README content."""
    repos = []
    current_category = None
    in_software_section = False
    
    lines = readme_content.split('\n')
    
    for line in lines:
        # Check if we're entering the Software packages section
        if line.strip() == '## Software packages':
            in_software_section = True
            continue
        
        # Check if we're leaving the Software packages section
        if in_software_section and line.startswith('##') and line.strip() != '## Software packages':
            # We've reached another main section
            if not line.startswith('###'):
                break
        
        # Parse category headers (### headers)
        if line.startswith('###'):
            current_category = line.replace('###', '').strip()
            continue
        
        # Parse repository entries
        if in_software_section and current_category and line.strip().startswith('- ['):
            # Extract repo name and URL
            match = re.search(r'\[([^\]]+)\]\(([^\)]+)\)', line)
            if match:
                name = match.group(1)
                url = match.group(2)
                
                # Only process GitHub URLs - check that github.com is the domain
                # Handle both http and https, with or without www
                if '://github.com/' in url or '://www.github.com/' in url or url.startswith('github.com/'):
                    owner, repo = parse_github_url(url)
                    if owner and repo:
                        # Extract description (text after closing `)` or after language tag)
                        desc_match = re.search(r'\]\s*-\s*(?:\[[^\]]+\]\s*-\s*)?(.+)$', line)
                        description = desc_match.group(1).strip() if desc_match else ''
                        # Remove emojis from description
                        description = remove_emojis(description)
                        
                        repos.append({
                            'name': name,
                            'url': url,
                            'owner': owner,
                            'repo': repo,
                            'category': current_category,
                            'description': description,
                            'stars': 0  # Will be filled later
                        })
    
    return repos

def main():
    """Main function."""
    print("Starting fetch_repos.py...")
    
    # Fetch README
    readme_content = fetch_readme()
    
    # Parse repositories
    print("Parsing repositories...")
    repos = parse_repos(readme_content)
    print(f"Found {len(repos)} GitHub repositories")
    
    # Fetch star counts
    print("Fetching star counts...")
    for i, repo_info in enumerate(repos):
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{len(repos)}")
        
        stars = get_star_count(repo_info['owner'], repo_info['repo'])
        repo_info['stars'] = stars
        
        # Be nice to GitHub API
        time.sleep(0.1)
    
    # Sort by stars (descending)
    repos.sort(key=lambda x: x['stars'], reverse=True)
    
    # Save to JSON
    output_file = 'repos_data.json'
    print(f"Saving data to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump({
            'repos': repos,
            'updated': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        }, f, indent=2)
    
    print(f"Done! Processed {len(repos)} repositories")
    print(f"Top 5 by stars:")
    for repo in repos[:5]:
        print(f"  {repo['name']}: {repo['stars']} stars")

if __name__ == '__main__':
    main()
