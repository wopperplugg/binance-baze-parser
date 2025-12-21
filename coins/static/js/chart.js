import * as d3 from "d3";

export function renderD3KlineChart(containerId, rawData) {
    // Преобразование данных
    const data = rawData.map(d => ({
        date: new Date(typeof d.time === "number" ? d.time * 1000 : d.time),
        open: +d.open,
        high: +d.high,
        low: +d.low,
        close: +d.close
    }));
    data.sort((a, b) => a.date - b.date);

    // Получаем контейнер
    const container = d3.select(`#${containerId}`);
    if (container.empty()) {
        console.error(`Контейнер с ID '${containerId}' не найден.`);
        return;
    }

    // Очищаем контейнер
    container.html("");

    // Функция для получения размеров контейнера
    function getContainerSize() {
        const boundingBox = container.node().getBoundingClientRect();
        return {
            width: boundingBox.width,
            height: boundingBox.height
        };
    }

    // Размеры контейнера
    let { width, height } = getContainerSize();

    // Отступы
    const margin = { top: 20, right: 50, bottom: 30, left: 50 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Создание SVG
    const svg = container
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Масштабы
    const xScale = d3.scaleTime()
        .domain(d3.extent(data, d => d.date))
        .range([0, innerWidth]);

    const yScale = d3.scaleLinear()
        .domain([d3.min(data, d => d.low) * 0.98, d3.max(data, d => d.high) * 1.02])
        .range([innerHeight, 0]);

    // clipPath для ограничения области отрисовки
    svg.append("defs").append("clipPath")
        .attr("id", "clip")
        .append("rect")
        .attr("width", innerWidth)
        .attr("height", innerHeight);

    const chartBody = svg.append("g")
        .attr("clip-path", "url(#clip)");

    const xAxis = svg.append("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0, ${innerHeight})`)
        .call(d3.axisBottom(xScale));

    const yAxis = svg.append("g")
        .attr("class", "y-axis")
        .call(d3.axisLeft(yScale));

    // Функция расчета ширины свечи
    function calculateBarWidth(scale) {
        if (data.length <= 1) return 10;
        let avgDiff = 0;
        for (let i = 0; i < Math.min(data.length - 1, 10); i++) {
            avgDiff += (data[i + 1].date - data[i].date);
        }
        avgDiff /= Math.min(data.length - 1, 10);
        const baseDate = data[0].date;
        const widthAtScale = scale(new Date(baseDate.getTime() + avgDiff)) - scale(baseDate);
        return Math.max(2, widthAtScale * 0.8);
    }

    let barWidth = calculateBarWidth(xScale);

    // Функция отрисовки свечей
    function drawCandles(xScaleCurrent) {
        const candleGroups = chartBody.selectAll(".candle-group")
            .data(data);
        const enterGroup = candleGroups.enter()
            .append("g")
            .attr("class", "candle-group");
        enterGroup.append("line").attr("class", "wick");
        enterGroup.append("rect").attr("class", "candle");
        const mergedGroups = enterGroup.merge(candleGroups);

        mergedGroups
            .select(".wick")
            .attr("x1", d => xScaleCurrent(d.date))
            .attr("x2", d => xScaleCurrent(d.date))
            .attr("y1", d => yScale(d.high))
            .attr("y2", d => yScale(d.low))
            .attr("stroke", d => d.open > d.close ? "red" : "green");

        mergedGroups
            .select(".candle")
            .attr("x", d => xScaleCurrent(d.date) - barWidth / 2)
            .attr("y", d => yScale(Math.max(d.open, d.close)))
            .attr("width", barWidth)
            .attr("height", d => Math.abs(yScale(d.open) - yScale(d.close)))
            .attr("fill", d => d.open > d.close ? "red" : "green");
    }

    // Tooltip setup
    const tooltip = d3.select("body")
        .append("div")
        .attr("id", "tooltip")
        .style("position", "absolute")
        .style("background", "white")
        .style("padding", "5px")
        .style("border", "1px solid #ccc")
        .style("pointer-events", "none")
        .style("opacity", 0)
        .style("font-family", "Arial, sans-serif");

    // Zoom functionality setup
    const zoom = d3.zoom()
        .scaleExtent([1, 40])
        .translateExtent([[-margin.left, 0], [innerWidth + margin.right, innerHeight]])
        .extent([[0, 0], [innerWidth, innerHeight]])
        .on("zoom", zoomed);

    // Применяем зум ко всему SVG-контейнеру
    svg.call(zoom);

    // Функция обработки зума/панорамирования
    function zoomed(event) {
        const newTransform = event.transform;

        // Обновляем xScale на основе трансформации (масштаб и сдвиг)
        const updatedXScale = newTransform.rescaleX(xScale);

        barWidth = calculateBarWidth(updatedXScale);

        // Обновляем оси
        xAxis.call(d3.axisBottom(updatedXScale));

        // Перерисовываем свечи с новыми масштабами/сдвигами
        drawCandles(updatedXScale);
    }

    // Первичная отрисовка свечей
    drawCandles(xScale);

    // Добавляем динамическое событие для тултипа
    chartBody.on("mousemove", function (event) {
        const [mouseX] = d3.pointer(event);

        // Находим ближайшую свечу к позиции курсора
        const bisectDate = d3.bisector(d => d.date).left;
        const x0 = xScale.invert(mouseX);
        const index = bisectDate(data, x0, 1);
        const d0 = data[index - 1];
        const d1 = data[index];
        const d = x0 - d0.date > d1.date - x0 ? d1 : d0;

        if (d) {
            // Показываем тултип
            tooltip.style("opacity", 1)
                .html(`
                    <strong>Дата:</strong> ${d.date.toLocaleString()}<br/>
                    <strong>Открытие:</strong> ${d.open.toFixed(2)}<br/>
                    <strong>Максимум:</strong> ${d.high.toFixed(2)}<br/>
                    <strong>Минимум:</strong> ${d.low.toFixed(2)}<br/>
                    <strong>Закрытие:</strong> ${d.close.toFixed(2)}
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        } else {
            tooltip.style("opacity", 0);
        }
    });

    // Скрываем тултип при выходе за пределы графика
    chartBody.on("mouseleave", function () {
        tooltip.style("opacity", 0);
    });

    // Обновление графика при изменении размера окна
    function updateChartSize() {
        const newSize = getContainerSize();
        width = newSize.width;
        height = newSize.height;

        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        // Обновляем размеры SVG
        svg.attr("width", width).attr("height", height);

        // Обновляем масштабы
        xScale.range([0, innerWidth]);
        yScale.range([innerHeight, 0]);

        // Обновляем оси
        xAxis.attr("transform", `translate(0, ${innerHeight})`).call(d3.axisBottom(xScale));
        yAxis.call(d3.axisLeft(yScale));

        // Обновляем clipPath
        svg.select("#clip rect")
            .attr("width", innerWidth)
            .attr("height", innerHeight);

        // Перерисовываем свечи
        barWidth = calculateBarWidth(xScale);
        drawCandles(xScale);
    }

    // Добавляем обработчик изменения размера окна
    window.addEventListener("resize", updateChartSize);

    // Первая отрисовка
    updateChartSize();
}

export function renderOrderBook(containerId, orderBookData) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Контейнер с ID '${containerId}' не найден.`);
        return;
    }

    // Проверяем структуру данных
    if (!orderBookData || !Array.isArray(orderBookData.bids) || !Array.isArray(orderBookData.asks)) {
        container.innerHTML = '<p class="text-muted text-center">Некорректные данные стакана.</p>';
        return;
    }

    // Преобразуем строки в числа для удобства
    const bids = orderBookData.bids.map(([price, amount]) => [Number(price), Number(amount)]);
    const asks = orderBookData.asks.map(([price, amount]) => [Number(price), Number(amount)]);

    // Очищаем контейнер
    container.innerHTML = '';

    // Создаем обертку
    const wrapper = document.createElement('div');
    wrapper.classList.add('order-book-container-wrapper');

    // Заголовок
    const header = document.createElement('div');
    header.classList.add('order-book-header', 'd-flex', 'justify-content-between', 'fw-bold', 'pb-1', 'border-bottom');
    header.innerHTML = `
        <span>Цена</span>
        <span>Объем</span>
        <span>Всего</span>
    `;
    wrapper.appendChild(header);

    // Отрисовка ask (продажи) - отсортированы по возрастанию цены
    const asksContainer = document.createElement('div');
    asksContainer.classList.add('order-book-asks');

    // Проверяем, что asks — массив, и реверсируем его для отображения сверху вниз
    if (Array.isArray(asks)) {
        asks.slice().reverse().forEach(([price, amount]) => {
            const row = document.createElement('div');
            row.classList.add('order-book-row', 'd-flex', 'justify-content-between', 'py-1', 'text-danger');
            row.innerHTML = `
                <span>${price.toFixed(2)}</span>
                <span>${amount.toFixed(6)}</span>
                <span>${(price * amount).toFixed(2)}</span>
            `;
            asksContainer.appendChild(row);
        });
    } else {
        asksContainer.innerHTML = '<div class="text-muted p-2">Нет данных продаж</div>';
    }

    wrapper.appendChild(asksContainer);

    // Средняя цена (spread)
    const spreadContainer = document.createElement('div');
    spreadContainer.classList.add('spread', 'text-center', 'my-2', 'text-muted', 'fst-italic');
    if (bids.length > 0 && asks.length > 0) {
        const bestBid = bids[0][0];
        const bestAsk = asks[0][0];
        const midPrice = ((bestBid + bestAsk) / 2).toFixed(2);
        const spreadPercent = (((bestAsk - bestBid) / bestBid) * 100).toFixed(2);
        spreadContainer.textContent = `Средняя цена: ${midPrice} (Spread: ${spreadPercent}%)`;
    } else {
        spreadContainer.textContent = 'Нет данных для расчета средней цены';
    }
    wrapper.appendChild(spreadContainer);

    // Отрисовка bid (покупки) - отсортированы по убыванию цены
    const bidsContainer = document.createElement('div');
    bidsContainer.classList.add('order-book-bids');

    if (Array.isArray(bids)) {
        bids.forEach(([price, amount]) => {
            const row = document.createElement('div');
            row.classList.add('order-book-row', 'd-flex', 'justify-content-between', 'py-1', 'text-success');
            row.innerHTML = `
                <span>${price.toFixed(2)}</span>
                <span>${amount.toFixed(6)}</span>
                <span>${(price * amount).toFixed(2)}</span>
            `;
            bidsContainer.appendChild(row);
        });
    } else {
        bidsContainer.innerHTML = '<div class="text-muted p-2">Нет данных покупок</div>';
    }

    wrapper.appendChild(bidsContainer);

    // Добавляем обертку в контейнер
    container.appendChild(wrapper);
}