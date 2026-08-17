const form = document.getElementById('commandForm');
const input = document.getElementById('repoInput');
const error = document.getElementById('formError');
const result = document.getElementById('commandResult');
const commandText = document.getElementById('commandText');
const copyButton = document.getElementById('copyButton');
const scanButton = document.getElementById('scanButton');
const scanStatus = document.getElementById('scanStatus');
const scanResults = document.getElementById('scanResults');

function validRepository(value) {
  return /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(value);
}

async function github(path) {
  const response = await fetch(`https://api.github.com${path}`, {
    headers: { Accept: 'application/vnd.github+json' }
  });
  if (response.status === 404) return null;
  if (!response.ok) throw new Error(`GitHub API returned ${response.status}`);
  return response.json();
}

async function contentExists(repository, path) {
  const response = await fetch(`https://api.github.com/repos/${repository}/contents/${path}`, {
    headers: { Accept: 'application/vnd.github+json' }
  });
  if (response.status === 404) return false;
  if (!response.ok) throw new Error(`GitHub API returned ${response.status}`);
  return true;
}

function row(status, title, detail) {
  const article = document.createElement('article');
  article.className = 'scan-row';
  const badge = document.createElement('strong');
  badge.className = `scan-badge ${status.toLowerCase()}`;
  badge.textContent = status;
  const text = document.createElement('div');
  const heading = document.createElement('b');
  heading.textContent = title;
  const description = document.createElement('span');
  description.textContent = detail;
  text.append(heading, description);
  article.append(badge, text);
  return article;
}

async function runPublicScan(repository) {
  scanResults.replaceChildren();
  scanStatus.textContent = 'Reading public GitHub metadata…';
  scanButton.disabled = true;

  try {
    const repo = await github(`/repos/${repository}`);
    if (!repo) throw new Error('Repository not found or not publicly accessible.');

    const [security, codeownersRoot, codeownersGithub, dependabot] = await Promise.all([
      contentExists(repository, 'SECURITY.md'),
      contentExists(repository, 'CODEOWNERS'),
      contentExists(repository, '.github/CODEOWNERS'),
      contentExists(repository, '.github/dependabot.yml')
    ]);

    const checks = [
      ['PASS', 'Repository reachable', `${repo.full_name} is publicly readable.`],
      [repo.archived ? 'FAIL' : 'PASS', 'Repository active', repo.archived ? 'Repository is archived.' : 'Repository is not archived.'],
      [repo.default_branch ? 'PASS' : 'UNKNOWN', 'Default branch', repo.default_branch ? `Default branch: ${repo.default_branch}.` : 'Default branch was not exposed.'],
      [security ? 'PASS' : 'FAIL', 'Security policy', security ? 'SECURITY.md found.' : 'SECURITY.md not found at repository root.'],
      [codeownersRoot || codeownersGithub ? 'PASS' : 'FAIL', 'Code ownership', codeownersRoot || codeownersGithub ? 'CODEOWNERS found.' : 'CODEOWNERS not found in checked public paths.'],
      [dependabot ? 'PASS' : 'FAIL', 'Dependabot configuration', dependabot ? '.github/dependabot.yml found.' : '.github/dependabot.yml not found.']
    ];

    checks.forEach(([status, title, detail]) => scanResults.append(row(status, title, detail)));
    scanStatus.textContent = 'Public quick scan complete. No token was used.';
  } catch (err) {
    scanStatus.textContent = err.message || 'Public scan failed.';
  } finally {
    scanButton.disabled = false;
  }
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const repository = input.value.trim();
  error.textContent = '';
  result.hidden = true;

  if (!validRepository(repository)) {
    error.textContent = 'Use OWNER/REPOSITORY format, for example Cyber-G3/security-evidence-collector.';
    return;
  }

  commandText.textContent = `sec-evidence collect github ${repository} --output ./evidence`;
  result.hidden = false;
  copyButton.textContent = 'Copy';
});

scanButton.addEventListener('click', async () => {
  const repository = input.value.trim();
  error.textContent = '';
  if (!validRepository(repository)) {
    error.textContent = 'Use OWNER/REPOSITORY format before running the public scan.';
    return;
  }
  await runPublicScan(repository);
});

copyButton.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(commandText.textContent);
    copyButton.textContent = 'Copied';
  } catch {
    copyButton.textContent = 'Select & copy';
  }
});
