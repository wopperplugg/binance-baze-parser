export async function fetchKlinesData(apiUrl, params = {}) {
    const urlParams = new URLSearchParams(params);
    const response = await fetch(`${apiUrl}?${urlParams.toString()}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const jsonResponse = await response.json();
    return jsonResponse.data;
}

export async function fetchOrderBookData(orderBookApiUrl) {
    try {
        const response = await fetch(orderBookApiUrl);
        if (!response.ok) {
            throw new Error(`Ошибка сети: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();

        if (!Array.isArray(data.data) || data.data.length === 0) {
            throw new Error("Пустой массив данных");
        }

        const latestSnapshot = data.data[data.data.length - 1];

        // ИСПРАВЛЕНИЕ: bids и asks — это строки, их нужно распарсить
        const bids = JSON.parse(latestSnapshot.bids);
        const asks = JSON.parse(latestSnapshot.asks);

        // Проверяем, что это массивы
        if (!Array.isArray(bids) || !Array.isArray(asks)) {
            throw new Error("bids или asks не являются массивами после парсинга");
        }

        return {
            bids: bids,
            asks: asks
        };

    } catch (error) {
        console.error("Ошибка при загрузке стакана ордеров:", error.message);
        throw error;
    }
}