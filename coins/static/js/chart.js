import * as d3 from "d3";
export function renderD3KlineChart(containerId, rawData) {
    // 1. Преобразование данных и форматов
    const parseTime = d3.timeParse("%Y-%m-%dT%H:%M:%S%Z"); // Парсер ISO формата из Django
    const data = rawData.map(d => ({
        date: new Date(d.time), // Просто используем new Date() для строк из Django
        open: +d.open,
        high: +d.high,
        low: +d.low,
        close: +d.close
    }));

    // 2. Определение размеров и отступов
    const margin = {top: 20, right: 30, bottom: 30, left: 50},
        width = 800 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    // Очищаем контейнер перед отрисовкой
    d3.select(`#${containerId}`).html("");

    // Добавление SVG-контейнера
    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // 3. Определение шкал (Scales)
    // Шкала X (время)
    const xScale = d3.scaleTime()
        .domain(d3.extent(data, d => d.date))
        .range([0, width]);

    svg.append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(xScale));

    // Шкала Y (цена)
    const yScale = d3.scaleLinear()
        .domain([d3.min(data, d => d.low) * 0.98, d3.max(data, d => d.high) * 1.02])
        .range([height, 0]);

    svg.append("g")
        .call(d3.axisLeft(yScale));

    // 4. Отрисовка свечей

    // Ширина свечи (примерно 10 пикселей)
    const barWidth = 10; 

    // Вертикальные линии (wick/shadow)
    svg.selectAll(".wick")
        .data(data)
        .enter()
        .append("line")
        .attr("class", "wick")
        .attr("x1", d => xScale(d.date))
        .attr("x2", d => xScale(d.date))
        .attr("y1", d => yScale(d.high))
        .attr("y2", d => yScale(d.low))
        .attr("stroke", d => d.open > d.close ? "red" : "green");

    // Прямоугольники тела свечи (body)
    svg.selectAll(".candle")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", "candle")
        .attr("x", d => xScale(d.date) - barWidth / 2)
        .attr("y", d => yScale(Math.max(d.open, d.close)))
        .attr("width", barWidth)
        .attr("height", d => Math.abs(yScale(d.open) - yScale(d.close)))
        .attr("fill", d => d.open > d.close ? "red" : "green");
        
    console.log("График D3 успешно отрисован.");
}