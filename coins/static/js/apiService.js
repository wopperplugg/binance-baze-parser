export async function fetchKlinesData(apiUrl, params = {}) {
    const urlParams = new URLSearchParams(params);
    const response = await fetch(`${apiUrl}?${urlParams.toString()}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const jsonResponse = await response.json();
    return jsonResponse.data;
}