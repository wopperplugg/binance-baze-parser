// Функции для отрисовки индикаторных графиков
import * as d3 from 'd3';

// Функция для отрисовки графика Sentiment Indicators
export function renderSentimentChart(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Контейнер ${containerId} не найден!`);
        return;
    }

    // Очищаем контейнер
    container.innerHTML = '';

    if (!data || data.length === 0) {
        container.innerText = 'Нет данных для отображения';
        return;
    }

    // Создаем элементы для каждого индикатора
    const chartContainer = document.createElement('div');
    chartContainer.style.height = '400px';
    chartContainer.style.position = 'relative';
    container.appendChild(chartContainer);

    // Подготовка данных
    const chartData = data.map(item => ({
        date: new Date(item.transaction_time),
        open_interest: item.open_interest,
        funding_rate: item.funding_rate,
        long_short_ratio: item.long_short_ratio
    })).reverse(); // Обратный порядок для правильного отображения

    // Настройка размеров
    const margin = { top: 20, right: 30, bottom: 50, left: 60 };
    const width = chartContainer.clientWidth - margin.left - margin.right;
    const height = chartContainer.clientHeight - margin.top - margin.bottom;

    // Создание SVG
    const svg = d3.select(chartContainer)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // Масштабы
    const xScale = d3.scaleTime()
        .domain(d3.extent(chartData, d => d.date))
        .range([0, width]);

    // Для Open Interest
    const yScaleOI = d3.scaleLinear()
        .domain(d3.extent(chartData, d => d.open_interest).map(d => d || 0))
        .range([height, 0]);

    // Для Funding Rate
    const yScaleFR = d3.scaleLinear()
        .domain(d3.extent(chartData, d => d.funding_rate).map(d => d || 0))
        .range([height, 0]);

    // Для Long/Short Ratio
    const yScaleLSR = d3.scaleLinear()
        .domain(d3.extent(chartData, d => d.long_short_ratio).map(d => d || 0))
        .range([height, 0]);

    // Линии
    const lineOI = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleOI(d.open_interest))
        .defined(d => d.open_interest !== null);

    const lineFR = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleFR(d.funding_rate))
        .defined(d => d.funding_rate !== null);

    const lineLSR = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleLSR(d.long_short_ratio))
        .defined(d => d.long_short_ratio !== null);

    // Оси
    g.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale));

    g.append('g')
        .attr('class', 'y-axis')
        .call(d3.axisLeft(yScaleOI));

    // Добавляем линии
    g.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', 'steelblue')
        .attr('stroke-width', 1.5)
        .attr('d', lineOI);

    g.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', 'red')
        .attr('stroke-width', 1.5)
        .attr('d', lineFR);

    g.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', 'green')
        .attr('stroke-width', 1.5)
        .attr('d', lineLSR);

    // Добавляем легенду
    const legend = g.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(10,10)');

    legend.append('rect')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', 150)
        .attr('height', 60)
        .attr('fill', 'white')
        .attr('stroke', 'black')
        .attr('stroke-width', 0.5)
        .attr('opacity', 0.8);

    legend.append('circle')
        .attr('cx', 10)
        .attr('cy', 15)
        .attr('r', 5)
        .attr('fill', 'steelblue');

    legend.append('text')
        .attr('x', 20)
        .attr('y', 20)
        .text('Open Interest')
        .attr('font-size', '12px');

    legend.append('circle')
        .attr('cx', 10)
        .attr('cy', 35)
        .attr('r', 5)
        .attr('fill', 'red');

    legend.append('text')
        .attr('x', 20)
        .attr('y', 40)
        .text('Funding Rate')
        .attr('font-size', '12px');

    legend.append('circle')
        .attr('cx', 10)
        .attr('cy', 55)
        .attr('r', 5)
        .attr('fill', 'green');

    legend.append('text')
        .attr('x', 20)
        .attr('y', 60)
        .text('L/S Ratio')
        .attr('font-size', '12px');

    // Добавляем подписи осей
    svg.append('text')
        .attr('transform', `translate(${width / 2}, ${height + margin.top + 30})`)
        .style('text-anchor', 'middle')
        .text('Время');

    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 0)
        .attr('x', 0 - (height / 2))
        .attr('dy', '1em')
        .style('text-anchor', 'middle')
        .text('Значения');
}

// Функция для отрисовки графика Volatility/Liquidity Indicators
export function renderVolatilityChart(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Контейнер ${containerId} не найден!`);
        return;
    }

    // Очищаем контейнер
    container.innerHTML = '';

    if (!data || data.length === 0) {
        container.innerText = 'Нет данных для отображения';
        return;
    }

    // Создаем элементы для каждого индикатора
    const chartContainer = document.createElement('div');
    chartContainer.style.height = '400px';
    chartContainer.style.position = 'relative';
    container.appendChild(chartContainer);

    // Подготовка данных
    const chartData = data.map(item => ({
        date: new Date(item.transaction_time),
        atr_14: item.atr_14,
        atr_21: item.atr_21,
        vwap: item.vwap,
        vwap_high_band: item.vwap_high_band,
        vwap_low_band: item.vwap_low_band
    })).reverse(); // Обратный порядок для правильного отображения

    // Настройка размеров
    const margin = { top: 20, right: 30, bottom: 50, left: 60 };
    const width = chartContainer.clientWidth - margin.left - margin.right;
    const height = chartContainer.clientHeight - margin.top - margin.bottom;

    // Создание SVG
    const svg = d3.select(chartContainer)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // Масштабы
    const xScale = d3.scaleTime()
        .domain(d3.extent(chartData, d => d.date))
        .range([0, width]);

    // Для ATR
    const yScaleATR = d3.scaleLinear()
        .domain(d3.extent(chartData, d => Math.max(d.atr_14 || 0, d.atr_21 || 0)).map(d => d || 0))
        .range([height, 0]);

    // Для VWAP
    const yScaleVWAP = d3.scaleLinear()
        .domain(d3.extent(chartData, d => Math.max(
            d.vwap || 0,
            d.vwap_high_band || 0,
            d.vwap_low_band || 0
        )).map(d => d || 0))
        .range([height, 0]);

    // Линии
    const lineATR14 = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleATR(d.atr_14))
        .defined(d => d.atr_14 !== null);

    const lineATR21 = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleATR(d.atr_21))
        .defined(d => d.atr_21 !== null);

    const lineVWAP = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleVWAP(d.vwap))
        .defined(d => d.vwap !== null);

    const lineVWAPHigh = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleVWAP(d.vwap_high_band))
        .defined(d => d.vwap_high_band !== null);

    const lineVWAPlow = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleVWAP(d.vwap_low_band))
        .defined(d => d.vwap_low_band !== null);

    // Оси
    g.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale));

    g.append('g')
        .attr('class', 'y-axis')
        .call(d3.axisLeft(yScaleATR));

    // Добавляем линии
    g.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', 'blue')
        .attr('stroke-width', 1.5)
        .attr('d', lineATR14);

    g.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', 'orange')
        .attr('stroke-width', 1.5)
        .attr('d', lineATR21);

    g.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', 'green')
        .attr('stroke-width', 1.5)
        .attr('d', lineVWAP);

    g.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', 'lightgreen')
        .attr('stroke-width', 1)
        .attr('d', lineVWAPHigh);

    g.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', 'lightgreen')
        .attr('stroke-width', 1)
        .attr('d', lineVWAPlow);

    // Добавляем легенду
    const legend = g.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(10,10)');

    legend.append('rect')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', 150)
        .attr('height', 100)
        .attr('fill', 'white')
        .attr('stroke', 'black')
        .attr('stroke-width', 0.5)
        .attr('opacity', 0.8);

    legend.append('circle')
        .attr('cx', 10)
        .attr('cy', 15)
        .attr('r', 5)
        .attr('fill', 'blue');

    legend.append('text')
        .attr('x', 20)
        .attr('y', 20)
        .text('ATR 14')
        .attr('font-size', '12px');

    legend.append('circle')
        .attr('cx', 10)
        .attr('cy', 35)
        .attr('r', 5)
        .attr('fill', 'orange');

    legend.append('text')
        .attr('x', 20)
        .attr('y', 40)
        .text('ATR 21')
        .attr('font-size', '12px');

    legend.append('circle')
        .attr('cx', 10)
        .attr('cy', 55)
        .attr('r', 5)
        .attr('fill', 'green');

    legend.append('text')
        .attr('x', 20)
        .attr('y', 60)
        .text('VWAP')
        .attr('font-size', '12px');

    legend.append('circle')
        .attr('cx', 10)
        .attr('cy', 75)
        .attr('r', 5)
        .attr('fill', 'lightgreen');

    legend.append('text')
        .attr('x', 20)
        .attr('y', 80)
        .text('VWAP Bands')
        .attr('font-size', '12px');

    // Добавляем подписи осей
    svg.append('text')
        .attr('transform', `translate(${width / 2}, ${height + margin.top + 30})`)
        .style('text-anchor', 'middle')
        .text('Время');

    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 0)
        .attr('x', 0 - (height / 2))
        .attr('dy', '1em')
        .style('text-anchor', 'middle')
        .text('Значения');
}

// Функция для отрисовки графика Technical Triggers
export function renderTechnicalChart(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Контейнер ${containerId} не найден!`);
        return;
    }

    // Очищаем контейнер
    container.innerHTML = '';

    if (!data || data.length === 0) {
        container.innerText = 'Нет данных для отображения';
        return;
    }

    // Создаем элементы для каждого индикатора
    const chartContainer = document.createElement('div');
    chartContainer.style.height = '400px';
    chartContainer.style.position = 'relative';
    container.appendChild(chartContainer);

    // Подготовка данных
    const chartData = data.map(item => ({
        date: new Date(item.transaction_time),
        ema_20: item.ema_20,
        ema_50: item.ema_50,
        ema_100: item.ema_100,
        ema_200: item.ema_200,
        stoch_rsi_k: item.stoch_rsi_k,
        stoch_rsi_d: item.stoch_rsi_d
    })).reverse(); // Обратный порядок для правильного отображения

    // Настройка размеров
    const margin = { top: 20, right: 30, bottom: 50, left: 60 };
    const width = chartContainer.clientWidth - margin.left - margin.right;
    const height = chartContainer.clientHeight - margin.top - margin.bottom;

    // Создание SVG
    const svg = d3.select(chartContainer)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // Масштабы
    const xScale = d3.scaleTime()
        .domain(d3.extent(chartData, d => d.date))
        .range([0, width]);

    // Для EMA
    const yScaleEMA = d3.scaleLinear()
        .domain(d3.extent(chartData, d => Math.max(
            d.ema_20 || 0,
            d.ema_50 || 0,
            d.ema_100 || 0,
            d.ema_200 || 0
        )).map(d => d || 0))
        .range([height, 0]);

    // Для Stochastic RSI
    const yScaleStoch = d3.scaleLinear()
        .domain([0, 100])
        .range([height, 0]);

    // Линии
    const lineEMA20 = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleEMA(d.ema_20))
        .defined(d => d.ema_20 !== null);

    const lineEMA50 = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleEMA(d.ema_50))
        .defined(d => d.ema_50 !== null);

    const lineEMA100 = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleEMA(d.ema_100))
        .defined(d => d.ema_100 !== null);

    const lineEMA200 = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleEMA(d.ema_200))
        .defined(d => d.ema_200 !== null);

    const lineStochK = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleStoch(d.stoch_rsi_k * 100)) // Преобразуем в проценты
        .defined(d => d.stoch_rsi_k !== null);

    const lineStochD = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScaleStoch(d.stoch_rsi_d * 100)) // Преобразуем в проценты
        .defined(d => d.stoch_rsi_d !== null);

    // Оси
    g.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale));

    g.append('g')
        .attr('class', 'y-axis')
        .call(d3.axisLeft(yScaleEMA));

    // Добавляем линии
    g.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', '#FF6B6B')
        .attr('stroke-width', 1.5)
        .attr('d', lineEMA20);

    g.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', '#4ECDC4')
        .attr('stroke-width', 1.5)
        .attr('d', lineEMA50);

    g.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', '#45B7D1')
        .attr('stroke-width', 1.5)
        .attr('d', lineEMA100);

    g.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', '#96CEB4')
        .attr('stroke-width', 1.5)
        .attr('d', lineEMA200);

    // Добавляем Stochastic RSI на отдельной оси
    const g2 = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    g2.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', '#FFEAA7')
        .attr('stroke-width', 1.5)
        .attr('d', lineStochK);

    g2.append('path')
        .datum(chartData)
        .attr('class', 'line')
        .attr('fill', 'none')
        .attr('stroke', '#FD79A8')
        .attr('stroke-width', 1.5)
        .attr('d', lineStochD);

    // Добавляем уровни 20 и 80 для Stochastic
    g2.append('line')
        .attr('x1', 0)
        .attr('x2', width)
        .attr('y1', yScaleStoch(20))
        .attr('y2', yScaleStoch(20))
        .attr('stroke', 'gray')
        .attr('stroke-dasharray', '5,5')
        .attr('stroke-width', 1);

    g2.append('line')
        .attr('x1', 0)
        .attr('x2', width)
        .attr('y1', yScaleStoch(80))
        .attr('y2', yScaleStoch(80))
        .attr('stroke', 'gray')
        .attr('stroke-dasharray', '5,5')
        .attr('stroke-width', 1);

    // Добавляем легенду
    const legend = g.append('g')
        .attr('class', 'legend')
        .attr('transform', 'translate(10,10)');

    legend.append('rect')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', 180)
        .attr('height', 140)
        .attr('fill', 'white')
        .attr('stroke', 'black')
        .attr('stroke-width', 0.5)
        .attr('opacity', 0.8);

    legend.append('circle')
        .attr('cx', 10)
        .attr('cy', 15)
        .attr('r', 5)
        .attr('fill', '#FF6B6B');

    legend.append('text')
        .attr('x', 20)
        .attr('y', 20)
        .text('EMA 20')
        .attr('font-size', '12px');

    legend.append('circle')
        .attr('cx', 10)
        .attr('cy', 35)
        .attr('r', 5)
        .attr('fill', '#4ECDC4');

    legend.append('text')
        .attr('x', 20)
        .attr('y', 40)
        .text('EMA 50')
        .attr('font-size', '12px');

    legend.append('circle')
        .attr('cx', 10)
        .attr('cy', 55)
        .attr('r', 5)
        .attr('fill', '#45B7D1');

    legend.append('text')
        .attr('x', 20)
        .attr('y', 60)
        .text('EMA 100')
        .attr('font-size', '12px');

    legend.append('circle')
        .attr('cx', 10)
        .attr('cy', 75)
        .attr('r', 5)
        .attr('fill', '#96CEB4');

    legend.append('text')
        .attr('x', 20)
        .attr('y', 80)
        .text('EMA 200')
        .attr('font-size', '12px');

    legend.append('circle')
        .attr('cx', 10)
        .attr('cy', 95)
        .attr('r', 5)
        .attr('fill', '#FFEAA7');

    legend.append('text')
        .attr('x', 20)
        .attr('y', 100)
        .text('Stoch RSI K')
        .attr('font-size', '12px');

    legend.append('circle')
        .attr('cx', 10)
        .attr('cy', 115)
        .attr('r', 5)
        .attr('fill', '#FD79A8');

    legend.append('text')
        .attr('x', 20)
        .attr('y', 120)
        .text('Stoch RSI D')
        .attr('font-size', '12px');

    // Добавляем подписи осей
    svg.append('text')
        .attr('transform', `translate(${width / 2}, ${height + margin.top + 30})`)
        .style('text-anchor', 'middle')
        .text('Время');

    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 0)
        .attr('x', 0 - (height / 2))
        .attr('dy', '1em')
        .style('text-anchor', 'middle')
        .text('Значения');
}