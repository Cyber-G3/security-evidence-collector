const form = document.getElementById('commandForm');
const input = document.getElementById('repoInput');
const error = document.getElementById('formError');
const result = document.getElementById('commandResult');
const commandText = document.getElementById('commandText');
const copyButton = document.getElementById('copyButton');

function validRepository(value) {
  return /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(value);
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

copyButton.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(commandText.textContent);
    copyButton.textContent = 'Copied';
  } catch {
    copyButton.textContent = 'Select & copy';
  }
});
