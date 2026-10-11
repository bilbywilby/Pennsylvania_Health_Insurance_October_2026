import { Octokit } from "octokit";

const CONFIG = {
  OWNER: process.env.REPO_OWNER ?? 'octocat',
  REPO: process.env.REPO_NAME ?? 'Spoon-Knife',
  TOKEN: process.env.GITHUB_TOKEN,
  STATE: process.env.ISSUE_STATE ?? 'all',
};

class APIClientError extends Error {
  constructor(status, message) {
    super(message);
    this.name = 'APIClientError';
    this.status = status;
  }
}

async function fetchIssuesWithSafety() {
  if (!CONFIG.TOKEN) {
    throw new Error('Missing GITHUB_TOKEN environment variable');
  }

  const octokit = new Octokit({ auth: CONFIG.TOKEN });

  try {
    const response = await octokit.request('GET /repos/{owner}/{repo}/issues', {
      owner: CONFIG.OWNER,
      repo: CONFIG.REPO,
      state: CONFIG.STATE,
      per_page: 100, // GitHub max
    });

    // Validate response structure
    if (!response?.data || !Array.isArray(response.data)) {
      throw new APIClientError(500, 'Invalid response structure from GitHub API');
    }

    // Safe transformation with all edge cases handled
    const sanitized = response.data.map(issue => ({
      number: issue.number ?? null,
      title: issue.title?.slice(0, 255) ?? '[No Title]',
      state: issue.state ?? 'unknown',
      createdAt: issue.created_at ?? null,
      labels: Array.isArray(issue.labels) 
        ? issue.labels.map(l => l.name ?? '').filter(Boolean)
        : [],
      author: {
        id: issue.user?.id ?? null,
        login: issue.user?.login ?? 'deleted-account',
        html_url: issue.user?.html_url ?? null,
      },
      metadata: {
        comments: issue.comments ?? 0,
        locked: issue.locked ?? false,
        pull_request: !!issue.pull_request,
      },
    }));

    // Log summary for monitoring
    console.log(`✓ Processed ${sanitized.length} issues`);
    console.log(`  Deleted accounts: ${sanitized.filter(i => !i.author.id).length}`);
    console.log(`  PRs included: ${sanitized.filter(i => i.metadata.pull_request).length}`);

    return sanitized;

  } catch (error) {
    // Structured error logging
    console.error('[API ERROR]', {
      status: error.status,
      statusText: error.statusText,
      message: error.response?.data?.message ?? error.message,
      owner: CONFIG.OWNER,
      repo: CONFIG.REPO,
      timestamp: new Date().toISOString(),
    });
    process.exit(1);
  }
}

export default fetchIssuesWithSafety;

if (import.meta.url === `file://${process.argv[1]}`) {
  fetchIssuesWithSafety().then(data => {
    console.log(JSON.stringify(data, null, 2));
  });
}
