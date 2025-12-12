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

    const margin = { top: 20, right: 50, bottom: 30, left: 50 },
        width = 800 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom,
        container = d3.select(`#${containerId}`);

    if (container.empty()) {
        console.error(`Контейнер с ID '${containerId}' не найден.`);
        return;
    }
    container.html(""); 

    // Создание SVG
    const svg = container
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Масштабы (начальные до зума)
    const xScale = d3.scaleTime()
        .domain(d3.extent(data, d => d.date))
        .range([0, width]);

    const yScale = d3.scaleLinear()
        .domain([d3.min(data, d => d.low) * 0.98, d3.max(data, d => d.high) * 1.02])
        .range([height, 0]);
    
    // clipPath для ограничения области отрисовки
    svg.append("defs").append("clipPath")
        .attr("id", "clip")
        .append("rect")
        .attr("width", width)
        .attr("height", height);

    const chartBody = svg.append("g")
        .attr("clip-path", "url(#clip)");
        
    const xAxis = svg.append("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(xScale));

    const yAxis = svg.append("g")
        .attr("class", "y-axis")
        .call(d3.axisLeft(yScale));

    // Функция расчета ширины свечи
    function calculateBarWidth(scale) {
        if (data.length <= 1) return 10;
        let avgDiff = 0;
        for (let i = 0; i < Math.min(data.length - 1, 10); i++) {
            avgDiff += (data[i+1].date - data[i].date);
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
        .translateExtent([[-margin.left, 0], [width + margin.right, height]]) 
        .extent([[0, 0], [width, height]])
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
    chartBody.on("mousemove", function(event) {
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
    chartBody.on("mouseleave", function() {
        tooltip.style("opacity", 0);
    });

    console.log("График D3 обновлен с возможностями зума/панорамирования и рабочим тултипом.");
}