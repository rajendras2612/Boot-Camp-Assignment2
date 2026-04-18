const ingestForm = document.getElementById('ingest-form');
const queryForm = document.getElementById('query-form');
const ingestResponse = document.getElementById('ingest-response');
const queryResults = document.getElementById('query-results');
const queryInput = document.getElementById('query-input');

async function handleIngest(event) {
  event.preventDefault();
  const fileInput = document.getElementById('pdf-file');

  if (!fileInput.files.length) {
    ingestResponse.textContent = 'Please select a PDF file to upload.';
    return;
  }

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  ingestResponse.textContent = 'Uploading and ingesting...';

  try {
    const response = await fetch('/ingest', {
      method: 'POST',
      body: formData,
    });

    const payload = await response.json();

    if (!response.ok) {
      ingestResponse.textContent = `Ingestion failed: ${payload.detail || response.statusText}`;
      return;
    }

    ingestResponse.textContent = JSON.stringify(payload, null, 2);
  } catch (error) {
    ingestResponse.textContent = `Request error: ${error.message}`;
  }
}

async function handleQuery(event) {
  event.preventDefault();
  const queryText = queryInput.value.trim();

  if (!queryText) {
    queryResults.textContent = 'Please enter a query.';
    return;
  }

  queryResults.textContent = 'Running query...';

  try {
    const response = await fetch('/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: queryText }),
    });

    const payload = await response.json();

    if (!response.ok) {
      queryResults.textContent = `Query failed: ${payload.detail || response.statusText}`;
      return;
    }

    const sourceLines = payload.sources.map((source, index) => {
      return `Source ${index + 1}: ${source.text}\nMetadata: ${JSON.stringify(source.metadata)}`;
    });

    queryResults.textContent = `Answer:\n${payload.answer}\n\nSources:\n${sourceLines.join('\n\n')}`;
  } catch (error) {
    queryResults.textContent = `Request error: ${error.message}`;
  }
}

ingestForm.addEventListener('submit', handleIngest);
queryForm.addEventListener('submit', handleQuery);
