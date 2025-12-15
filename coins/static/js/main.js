import { fetchKlinesData } from "./apiService";
import { renderD3KlineChart } from "./chart";

document.addEventListener('DOMContentLoaded', async () => {
    const configElement = document.getElementById('data-config');
    const apiUrl = configElement.dataset.apiUrl;

    // Инициализация параметров запроса
    let requestParams = {
        resolution: '1d', // Начальное разрешение
        limit: 500,
        table: "coins_kline_1d" // Начальная таблица из RES_MAP
    };

    // Отображение разрешений на таблицы
    const RES_MAP = {
        "1m": "coins_kline_1m",
        "5m": "coins_kline_5m",
        "15m": "coins_kline_15m",
        "1h": "coins_kline_1h",
        "4h": "coins_kline_4h",
        "1d": "coins_kline_1d",
    };

    // Элемент контейнера графика
    const chartContainer = document.getElementById('chart-container');

    // Функция для загрузки и отрисовки данных
    async function loadAndRenderChart(resolution) {
        try {
            console.log(`Запуск загрузки и отрисовки D3 с разрешением ${resolution}...`);
            requestParams.resolution = resolution; // Обновляем разрешение
            requestParams.table = RES_MAP[resolution]; // Обновляем таблицу

            const rawData = await fetchKlinesData(apiUrl, requestParams);

            // Очищаем контейнер перед отрисовкой нового графика
            chartContainer.innerHTML = "";

            // Отрисовываем график
            renderD3KlineChart('chart-container', rawData);
        } catch (error) {
            console.error("Ошибка при загрузке или отрисовке D3:", error);
            chartContainer.innerText = "Не удалось загрузить данные графика D3";
        }
    }

    // Создаем кнопки для изменения разрешения
    const buttonContainer = document.createElement('div');
    buttonContainer.style.marginBottom = "10px"; // Отступ между кнопками и графиком

    // Возможные значения разрешения
    const resolutions = Object.keys(RES_MAP); // ['1m', '5m', '15m', '1h', '4h', '1d']
    resolutions.forEach(resolution => {
        const button = document.createElement('button');
        button.textContent = resolution;
        button.style.marginRight = "5px";
        button.style.padding = "5px 10px";
        button.style.border = "1px solid #ccc";
        button.style.cursor = "pointer";

        // Добавляем обработчик события на кнопку
        button.addEventListener('click', () => {
            loadAndRenderChart(resolution); // Загружаем и отрисовываем график с новым разрешением
        });

        buttonContainer.appendChild(button);
    });

    // Добавляем контейнер с кнопками перед графиком
    chartContainer.parentNode.insertBefore(buttonContainer, chartContainer);

    // Загружаем начальный график с разрешением '1d'
    loadAndRenderChart(requestParams.resolution);
});