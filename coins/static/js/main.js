import { fetchKlinesData, fetchOrderBookData } from "./apiService";
import { renderD3KlineChart } from "./kline-chart";
import { renderOrderBook } from "./order-book";
import { renderSentimentChart, renderVolatilityChart, renderTechnicalChart } from "./indicator-charts";

document.addEventListener('DOMContentLoaded', async () => {
    // Получение конфигурации
    const configElement = document.getElementById('data-config');
    if (!configElement) {
        console.error("Элемент 'data-config' не найден!");
        return;
    }

    const klinesApiUrl = configElement.dataset.klinesApiUrl;
    const orderBookApiUrl = configElement.dataset.orderbookApiUrl; // Добавляем URL для стакана
        const sentimentApiUrl = configElement.dataset.sentimentApiUrl;
    const volatilityApiUrl = configElement.dataset.volatilityApiUrl;
    const technicalApiUrl = configElement.dataset.technicalApiUrl;

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

    // Контейнеры для индикаторных графиков
    const sentimentContainer = document.getElementById('sentiment-chart-container');
    if (!sentimentContainer) {
        console.error("Элемент 'sentiment-chart-container' не найден!");
        return;
    }

    const volatilityContainer = document.getElementById('volatility-chart-container');
    if (!volatilityContainer) {
        console.error("Элемент 'volatility-chart-container' не найден!");
        return;
    }

    const technicalContainer = document.getElementById('technical-chart-container');
    if (!technicalContainer) {
        console.error("Элемент 'technical-chart-container' не найден!");
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


    
    // Функция для загрузки и отрисовки sentiment индикаторов
    async function loadAndRenderSentiment() {
        try {
            console.log("Запуск загрузки sentiment индикаторов...");
            console.log(`URL запроса: ${sentimentApiUrl}`);

            const response = await fetch(`${sentimentApiUrl}?limit=50`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const sentimentData = await response.json();

            if (!sentimentData || sentimentData.length === 0) {
                throw new Error("Получены пустые данные sentiment индикаторов");
            }

            // Очищаем контейнер перед отрисовкой
            sentimentContainer.innerHTML = "";

            // Отрисовываем график
            renderSentimentChart('sentiment-chart-container', sentimentData);

        } catch (error) {
            console.error("Ошибка при загрузке или отрисовке sentiment индикаторов:", error.message);
            sentimentContainer.innerText = `Ошибка: ${error.message}`;
        }
    }

    // Функция для загрузки и отрисовки volatility/liquidity индикаторов
    async function loadAndRenderVolatility() {
        try {
            console.log("Запуск загрузки volatility/liquidity индикаторов...");
            console.log(`URL запроса: ${volatilityApiUrl}`);

            const response = await fetch(`${volatilityApiUrl}?limit=50`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const volatilityData = await response.json();

            if (!volatilityData || volatilityData.length === 0) {
                throw new Error("Получены пустые данные volatility/liquidity индикаторов");
            }

            // Очищаем контейнер перед отрисовкой
            volatilityContainer.innerHTML = "";

            // Отрисовываем график
            renderVolatilityChart('volatility-chart-container', volatilityData);

        } catch (error) {
            console.error("Ошибка при загрузке или отрисовке volatility/liquidity индикаторов:", error.message);
            volatilityContainer.innerText = `Ошибка: ${error.message}`;
        }
    }

    // Функция для загрузки и отрисовки technical индикаторов
    async function loadAndRenderTechnical() {
        try {
            console.log("Запуск загрузки technical индикаторов...");
            console.log(`URL запроса: ${technicalApiUrl}`);

            const response = await fetch(`${technicalApiUrl}?limit=50`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const technicalData = await response.json();

            if (!technicalData || technicalData.length === 0) {
                throw new Error("Получены пустые данные technical индикаторов");
            }

            // Очищаем контейнер перед отрисовкой
            technicalContainer.innerHTML = "";

            // Отрисовываем график
            renderTechnicalChart('technical-chart-container', technicalData);

        } catch (error) {
            console.error("Ошибка при загрузке или отрисовке technical индикаторов:", error.message);
            technicalContainer.innerText = `Ошибка: ${error.message}`;
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
        button.style.margin = "5px 2px";
        button.style.cursor = "pointer";

        // Добавляем класс для стилизации
        button.classList.add("btn");
        button.classList.add("btn-outline-success");

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
    // Загружаем и отрисовываем индикаторные графики
    loadAndRenderSentiment();
    loadAndRenderVolatility();
    loadAndRenderTechnical();

    // Опционально: обновляем стакан каждые 5 секунд
    setInterval(loadAndRenderOrderBook, 5000);
    // Опционально: обновляем индикаторы каждые 30 секунд
    setInterval(loadAndRenderSentiment, 30000);
    setInterval(loadAndRenderVolatility, 30000);
    setInterval(loadAndRenderTechnical, 30000);
});