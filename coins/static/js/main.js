import { fetchKlinesData } from "./apiService";
import { renderD3KlineChart } from "./chart";

document.addEventListener('DOMContentLoaded', async () => {
    const configElement = document.getElementById('data-config');
    const apiUrl = configElement.dataset.apiUrl;

    const requestParams = {
        resolution: '1d',
        limit: 500
    }
    try {
        console.log("Запуск загрузки и отрисовки D3...");
        const rawData = await fetchKlinesData(apiUrl, requestParams);

        renderD3KlineChart('chart-conrainer', rawData);
    } catch (error) {
        console.error("Ошибка при загрузке или отрисовке D3:", error);
        document.getElementById('chart-conrainer').innerText = "не удалось загрузить данные графика d3";
    }
})