import { fetchKlinesData, fetchOrderBookData } from "./apiService";
import { renderD3KlineChart, renderOrderBook } from "./chart";

document.addEventListener('DOMContentLoaded', async () => {
    // Получение конфигурации
    const configElement = document.getElementById('data-config');
    if (!configElement) {
        console.error("Элемент 'data-config' не найден!");
        return;
    }

    const klinesApiUrl = configElement.dataset.klinesApiUrl;
    const orderBookApiUrl = configElement.dataset.orderbookApiUrl; // Добавляем URL для стакана

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

    // Элементы контейнеров
    const chartContainer = document.getElementById('kline-chart-container');
    if (!chartContainer) {
        console.error("Элемент 'kline-chart-container' не найден!");
        return;
    }

    const orderBookContainer = document.getElementById('orderbook-container'); // Добавляем контейнер для стакана
    if (!orderBookContainer) {
        console.error("Элемент 'orderbook-container' не найден!");
        return;
    }

    // Функция для загрузки и отрисовки данных графика
    async function loadAndRenderChart(resolution) {
        try {
            console.log(`Запуск загрузки и отрисовки D3 с разрешением ${resolution}...`);
            requestParams.resolution = resolution; // Обновляем разрешение
            requestParams.table = RES_MAP[resolution]; // Обновляем таблицу

            console.log(`Запрос данных с параметрами:`, requestParams);
            console.log(`URL запроса: ${klinesApiUrl}`);

            const rawData = await fetchKlinesData(klinesApiUrl, requestParams);

            if (!rawData || rawData.length === 0) {
                throw new Error("Получены пустые данные");
            }

            // Очищаем контейнер перед отрисовкой нового графика
            chartContainer.innerHTML = "";

            // Отрисовываем график
            renderD3KlineChart('kline-chart-container', rawData);
        } catch (error) {
            console.error("Ошибка при загрузке или отрисовке D3:", error.message);
            chartContainer.innerText = `Ошибка: ${error.message}`;
        }
    }

    // Функция для загрузки и отрисовки стакана ордеров
    async function loadAndRenderOrderBook() {
        try {
            console.log("Запуск загрузки стакана ордеров...");
            console.log(`URL запроса: ${orderBookApiUrl}`);

            const orderBookData = await fetchOrderBookData(orderBookApiUrl);

            if (!orderBookData || (!orderBookData.bids?.length && !orderBookData.asks?.length)) {
                throw new Error("Получены пустые данные стакана");
            }

            // Очищаем контейнер перед отрисовкой
            orderBookContainer.innerHTML = "";

            // Отрисовываем стакан
            renderOrderBook('orderbook-container', orderBookData);

        } catch (error) {
            console.error("Ошибка при загрузке или отрисовке стакана:", error.message);
            orderBookContainer.innerText = `Ошибка: ${error.message}`;
        }
    }

    // Создаем кнопки для изменения разрешения
    const buttonContainer = document.createElement('div');
    buttonContainer.style.marginBottom = "10px";
    buttonContainer.style.display = "flex"; // Горизонтальное расположение кнопок
    buttonContainer.style.gap = "5px"; // Пространство между кнопками

    const resolutions = Object.keys(RES_MAP); // ['1m', '5m', '15m', '1h', '4h', '1d']
    resolutions.forEach(resolution => {
        const button = document.createElement('button');
        button.textContent = resolution;
        button.style.padding = "5px 10px";
        button.style.border = "1px solid #ccc";
        button.style.cursor = "pointer";

        // Добавляем класс для стилизации
        button.classList.add("resolution-button");

        // Обработчик события
        button.addEventListener('click', () => {
            loadAndRenderChart(resolution);
        });

        buttonContainer.appendChild(button);
    });

    // Добавляем контейнер с кнопками перед графиком
    if (!chartContainer.parentNode) {
        console.error("Родительский элемент для 'kline-chart-container' не найден!");
        return;
    }
    chartContainer.parentNode.insertBefore(buttonContainer, chartContainer);

    // Загружаем начальный график с разрешением '1d'
    loadAndRenderChart(requestParams.resolution);

    // Загружаем и отрисовываем стакан ордеров
    loadAndRenderOrderBook();

    // Опционально: обновляем стакан каждые 5 секунд
    setInterval(loadAndRenderOrderBook, 5000);
});